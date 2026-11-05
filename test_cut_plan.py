"""Independent tiny exhaustive assignment oracle and public CLI checks."""
import itertools
import json
import random
import subprocess
import sys
from pathlib import Path
from cut_plan import solve


def oracle(parts, stock, kerf):
    best = None
    for placement in itertools.product(range(len(stock)), repeat=len(parts)):
        used = [0] * len(stock)
        for piece, bar in zip(parts, placement):
            used[bar] += piece + kerf
        if any(a > b for a, b in zip(used, stock)):
            continue
        objective = (sum(stock[i] for i, v in enumerate(used) if v), sum(bool(v) for v in used))
        if best is None or objective < best:
            best = objective
    return best


def verify(job, result):
    ids = []
    stock_ids = []
    for bar in result['bars']:
        i = bar['stock_index']
        stock_ids.append(i)
        assert bar['stock_length'] == job['stock'][i]
        ids.extend(bar['part_indices'])
        assert bar['part_lengths'] == [job['parts'][j] for j in bar['part_indices']]
        assert bar['kerf_allowance'] == len(bar['part_indices']) * job['kerf']
        assert sum(bar['part_lengths']) + bar['kerf_allowance'] + bar['offcut'] == job['stock'][i]
        assert bar['offcut'] >= 0
    assert sorted(ids) == list(range(len(job['parts'])))
    assert len(stock_ids) == len(set(stock_ids))
    assert result['used_stock_length'] == sum(job['stock'][i] for i in stock_ids)
    assert result['bar_count'] == len(stock_ids)


rng = random.Random(77193)
cases = [
    {'parts':[40,30,20], 'stock':[100,60], 'kerf':3},
    {'parts':[100], 'stock':[100], 'kerf':0},
    {'parts':[100], 'stock':[100], 'kerf':1},
    {'parts':[5,5], 'stock':[5,5,20], 'kerf':0},
    {'parts':[6,4], 'stock':[10,10], 'kerf':0},
]
for _ in range(150):
    cases.append({'parts':[rng.randint(1,15) for _ in range(rng.randint(1,5))],
                  'stock':[rng.randint(3,35) for _ in range(rng.randint(1,4))], 'kerf':rng.randint(0,3)})
feasible = 0
for job in cases:
    expected = oracle(**job)
    result = solve(job)
    if expected is None:
        assert result['status'] == 'infeasible'
    else:
        assert result['status'] == 'optimal_for_model'
        assert (result['used_stock_length'], result['bar_count']) == expected
        verify(job, result)
        feasible += 1
cli = [
    (json.dumps(cases[0]).encode(), 0),
    (json.dumps(cases[2]).encode(), 2),
    (b'{"parts":[true],"stock":[10],"kerf":0}', 1),
    (b'{"parts":[1],"stock":[10],"kerf":0,"kerf":1}', 1),
    (b'{"parts":[1.2],"stock":[10],"kerf":0}', 1),
    (b'{"parts":[],"stock":[10],"kerf":0}', 1),
    (b'{"parts":[1],"stock":[10],"kerf":-1}', 1),
    (b'{"parts":[1],"stock":[10],"kerf":0,"extra":1}', 1),
    (b'['*10000, 1),
    (b' '*65537, 1),
    (b'not json',1),
]
for raw, expected_code in cli:
    p = subprocess.run([sys.executable, 'cut_plan.py'], input=raw, capture_output=True, timeout=5)
    assert p.returncode == expected_code, (expected_code,p.returncode)
    if expected_code == 1:
        assert not p.stdout and p.stderr == b'Invalid job: use documented integer lengths and limits.\n'
# Exercise documented maximum dimensions without asserting a speed guarantee.
maximum = {'parts':[10]*10,'stock':[11]*10,'kerf':1}
verify(maximum, solve(maximum))
report = {'classification':'SYNTHETIC_ONLY','oracle_cases_passed':len(cases),'feasible_cases':feasible,
          'cli_cases_passed':len(cli),'max_dimension_case_passed':True,'failed':0,
          'python':sys.version.split()[0],'independent_workshop_users':'UNKNOWN','revenue':'UNKNOWN'}
Path('test-result.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))

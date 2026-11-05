"""Bounded exact finite-stock assignment. Python standard library only."""
import json
import sys


def solve(job):
    if not isinstance(job, dict) or set(job) != {'parts', 'stock', 'kerf'}:
        raise ValueError('Expected exactly parts, stock, kerf')
    parts, stock, kerf = job['parts'], job['stock'], job['kerf']
    for values in (parts, stock):
        if not isinstance(values, list) or not 1 <= len(values) <= 10:
            raise ValueError('Each length list needs 1 to 10 entries')
        if any(type(v) is not int or not 1 <= v <= 1000000 for v in values):
            raise ValueError('Lengths must be positive integers at most 1000000')
    if type(kerf) is not int or not 0 <= kerf <= 1000000:
        raise ValueError('Kerf must be a nonnegative integer at most 1000000')
    n = len(parts)
    full = (1 << n) - 1
    sizes = [0] * (full + 1)
    for mask in range(1, full + 1):
        bit = mask & -mask
        sizes[mask] = sizes[mask ^ bit] + parts[bit.bit_length()-1] + kerf
    # For each assigned subset keep the lowest consumed stock length, then bar count.
    dp = {0: (0, 0, ())}
    for index, length in enumerate(stock):
        nxt = dict(dp)
        for mask, (cost, count, plan) in dp.items():
            remaining = full ^ mask
            sub = remaining
            while sub:
                if sizes[sub] <= length:
                    candidate = (cost + length, count + 1, plan + ((index, sub),))
                    old = nxt.get(mask | sub)
                    if old is None or candidate[:2] < old[:2]:
                        nxt[mask | sub] = candidate
                sub = (sub - 1) & remaining
        dp = nxt
    if full not in dp:
        return {'status': 'infeasible', 'kerf_model': 'one kerf allowance per required piece'}
    cost, count, plan = dp[full]
    bars = []
    for index, mask in plan:
        ids = [i for i in range(n) if mask & (1 << i)]
        bars.append({'stock_index': index, 'stock_length': stock[index],
                     'part_indices': ids, 'part_lengths': [parts[i] for i in ids],
                     'kerf_allowance': len(ids)*kerf, 'offcut': stock[index]-sizes[mask]})
    return {'status': 'optimal_for_model', 'objective': 'minimum total used stock length, then bar count',
            'kerf_model': 'one kerf allowance per required piece', 'used_stock_length': cost,
            'bar_count': count, 'bars': bars}


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON field')
        result[key] = value
    return result


def main():
    try:
        if len(sys.argv) != 1:
            raise ValueError('Pipe one JSON job to stdin; no arguments accepted')
        raw = sys.stdin.buffer.read(65537)
        if len(raw) > 65536:
            raise ValueError('Input exceeds 64 KiB')
        result = solve(json.loads(raw, object_pairs_hook=unique))
        print(json.dumps(result, indent=2))
        return 0 if result['status'] == 'optimal_for_model' else 2
    except (ValueError, TypeError, RecursionError):
        print('Invalid job: use documented integer lengths and limits.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

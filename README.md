# Cut Plan — experimental finite-stock assignment

Download the [source ZIP](https://codeload.github.com/Dexter-Ou/cut-plan/zip/b7378b2246cbd2e29925c16d4f7b434b5f34828a), extract it, and open a terminal in the extracted folder.

Run with Python 3.10 or later, no packages or network needed:

    python3 cut_plan.py < example.json

Give `parts` (required lengths), `stock` (each available bar's length), and `kerf` as JSON. All lengths use the same integer unit. Scale fractional units to integers yourself. Lists contain 1–10 entries each; lengths are 1–1000000, kerf 0–1000000. Indices in the result start at zero. Each stock entry can be used once. Repeat entries for repeated pieces/bars. All stock must be interchangeable in material and cross section.

The exact bounded solver minimizes total original length of used stock, breaking ties by bar count. It does not minimize purchases, monetary cost, cut sequence, or number of patterns. `offcut` excludes a kerf allowance for EVERY requested piece, including the last piece on each used bar. This conservative model can reject a physically possible exact-end fit. It assumes stock is already end-trimmed and ignores defects, grain, clamping and machine allowances. This is an assignment calculator, not machine instructions; check measurements and workshop requirements before cutting.

The example uses the 100-unit bar for all three parts: 90 units of parts + 9 kerf allowance + 1 offcut. The 60-unit bar stays unused. Exit status: 0 optimal under this model, 2 infeasible under this model, 1 invalid job. JSON output goes to stdout. No input data is stored. No pricing, purchase or savings guarantee is provided.

Test with `python3 test_cut_plan.py`. Automated synthetic tests were run on Linux with Python 3.12.15. Other Python versions and operating systems have not been tested.

## License and feedback

Free MIT-licensed preview from Gong LLC. See LICENSE. Support is best effort; no service commitment is included. Report setup problems, incorrect assignments or missing workflow details through this repository’s Issues, using a small non-sensitive example.

# Build Book

Build any book from its HTML parts into a PDF and send the file to the user.

**Usage:** `/build-book <prefix>`

| Prefix | Book |
|--------|------|
| `grid` | Grid Trading Mastery |
| `playground` | The Playground |
| `arb` | Arbitrage |
| `eye` | ตาของ Arbitrageur |
| `math` | คณิตศาสตร์สำหรับ Options |
| `pm` | Payoff Mastery |
| `python` | Python for Quant Traders |
| `statarb` | Statistical Arbitrage |
| `vol` | Volatility Mastery |
| `vp` | View → Payoff |

## Steps

The requested prefix is: $ARGUMENTS

1. Run the appropriate builder:
   - `grid` → `python /home/user/Claude-code-project/build_pdf.py`
   - `playground` → `python /home/user/Claude-code-project/build_pdf_playground.py`
   - All others → `python /home/user/Claude-code-project/build_pdf_generic.py $ARGUMENTS`
2. The build takes 2–5 minutes depending on the number of parts. Wait for completion.
3. Report: output file path, total pages, file size in MB.
4. Send the generated PDF to the user using SendUserFile.
5. Commit any changed PDF files to git and push to `claude/continue-latest-commit-sxxwJ`.

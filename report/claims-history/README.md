# Claim-ledger history

`f1c1387/` holds `README.md`, `report/draft.md` and `report/video-script.md` exactly as committed at `f1c1387`, the revision the first claim-checking pass read. `report/tools/check_claims.py` reads the historical ledger rows from these copies, so they still verify after a squash merge drops that commit. The checker pins each file's SHA256 and rejects a modified copy. These copies are a frozen record; do not edit them.

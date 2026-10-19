# GrantKeeper — Portal submission

**Primary tag:** Governance
**Tag 1:** Treasury Allocation
**Tag 2:** Reputation Voting

---

## Title
GrantKeeper — on-chain accountability gate for grant deliveries

## One-liner (<=180 chars)
Locks a grant recipient's pledge on-chain, then uses GenLayer consensus to read the delivery report and grade it across five fixed facets — gating the next tranche.

## Description (<=1000 chars)
GrantKeeper turns "did they do what they promised?" into an auditable on-chain verdict. A treasury
locks a recipient's delivery pledge at funding time; the text is hashed and can never be rewritten.
When the work is delivered, the steward attaches one public delivery report and a disclosure note.
Anyone can then run the audit: GenLayer validators each read the locked pledge and the live report
and independently grade five fixed facets — SCOPE, MILESTONES, BUDGET, TIMELINE, BENEFICIARIES — as
KEPT, AMENDED_DISCLOSED, AMENDED_SILENT, or UNVERIFIABLE. The contract, not the model, folds those
into a terminal verdict and a tranche gate: all kept clears funding, a disclosed change makes it
conditional, missing evidence holds it, and any silent change revokes it. Byte comparison can't tell
a reworded milestone from a quietly dropped one; decentralized judgment, constrained to a fixed
vocabulary, can — and settles it deterministically.

## How to verify (<=500 chars)
Run `gltest tests` for the full direct-mode suite (five-facet grading, authorization, terminal state,
all four gates). On studionet: call open_grant to lock a pledge, file_delivery with a public HTTPS
report URL and "NONE", then audit. The repo fixtures (docs/) drive a DIVERTED / REVOKED result
because the delivery moves the beta past the pledged window with no disclosure. Contract address and
deploy tx are in deployment.json.

## Links
- Repo: https://github.com/phu1271997/grant-keeper
- Network: GenLayer studionet (chain 61999), RPC https://studio.genlayer.com/api
- Contract: `0xE2A9b3aD351C83ABC4AfB3B40349CAdC39992797`

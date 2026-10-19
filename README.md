# GrantKeeper

GrantKeeper is a standalone GenLayer Intelligent Contract that locks a grant recipient's
delivery **pledge** on-chain, then derives a consensus **accountability verdict** by reading
the public delivery report and grading it against the pledge across five fixed facets.

It does not try to decide whether the funded work was *good*. It answers a narrower, auditable
question a treasury actually needs before releasing the next tranche: **did the delivery honor
what was pledged, and were any material changes openly disclosed?**

## Fixed accountability facets

Every audit grades exactly, and in this order:

1. `SCOPE`
2. `MILESTONES`
3. `BUDGET`
4. `TIMELINE`
5. `BENEFICIARIES`

Each facet is graded `KEPT`, `AMENDED_DISCLOSED`, `AMENDED_SILENT`, or `UNVERIFIABLE`.
The **contract** — not the model — folds the facets into one verdict and gate:

| Worst facet present | Outcome | Tranche gate |
|---|---|---|
| any `AMENDED_SILENT` | `DIVERTED` | `REVOKED` |
| any `UNVERIFIABLE` | `UNPROVEN` | `HELD` |
| any `AMENDED_DISCLOSED` | `REVISED` | `CONDITIONAL` |
| all `KEPT` | `DELIVERED` | `CLEARED` |

## Why decentralized judgment is necessary

A grant pledge and its delivery report describe the same commitments in different prose. A byte
or keyword comparison cannot tell a harmless rewording from a quietly dropped milestone, a
reallocated budget, or a narrowed beneficiary set. GenLayer validators each read the same locked
pledge and the same live report and must independently agree on the per-facet verdict, while the
contract constrains them to a small canonical vocabulary and derives the money gate deterministically.

## Lifecycle

1. `open_grant(ref, recipient, pledge, tranche)` — the pledge is hashed and **locked at creation**; it can never be rewritten.
2. `file_delivery(ref, evidence_url, disclosed_changes)` — the steward attaches one public HTTPS delivery report and a disclosure note (`NONE` or a description).
3. `audit(ref)` — reads the report, grades the five facets under consensus, and records a terminal verdict + gate.

Auditing is terminal: there is no owner-controlled re-grade, appeal, or silent overwrite.

## Security boundaries

- Public HTTPS evidence only (localhost / internal hosts rejected).
- The pledge is immutable from creation and SHA-256 fingerprinted.
- Only the grant steward may file a delivery, exactly once.
- The delivery report body is bounded to 9,000 normalized characters.
- The five consensus verdicts are schema-checked and order-enforced.
- Missing evidence can never produce a `CLEARED` gate.
- The contract audits pledge alignment; it does not establish that the work was correct, impactful, or complete.

## Tests

```bash
gltest tests
```

The suite (direct mode) covers the locked/immutable pledge, steward and HTTPS authorization,
single-use delivery, complete ordered output, silent vs disclosed changes, missing evidence,
terminal state, and every gate consequence.

## Deploy (studionet)

```bash
source ~/.genlayer/env.sh      # loads GENLAYER_PRIVATE_KEY
python3 scripts/deploy.py      # deploys to studionet (chain 61999) and writes deployment.json
```

- RPC: `https://studio.genlayer.com/api`
- Chain ID: `61999`

The live contract address is recorded in `deployment.json` and the table below.

### Verified deployment (studionet)

| Field | Value |
|---|---|
| Network | GenLayer studionet (chain `61999`) |
| Contract | `0xE2A9b3aD351C83ABC4AfB3B40349CAdC39992797` |
| Deploy tx | `0xdcd378016716d86925e4f09ff141d14c2f8067d46a479b8dd2f5e2d9d7732209` |
| Runner | `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6` |
| Explorer | https://genlayer-explorer.vercel.app (search the contract address) |

## Demonstration fixtures

`docs/pledge.txt` and `docs/delivery-report.txt` are repository-controlled fixtures: the delivery
quietly moves the public beta past the pledged window with no disclosure, which drives a
`DIVERTED / REVOKED` result. They are for reproducibility, not real grant evidence.

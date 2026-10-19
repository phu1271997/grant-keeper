import json

CONTRACT = "contracts/grant_keeper.py"
EVIDENCE_URL = "https://grants.example/ledger/alpha-grant"
EVIDENCE_PATTERN = r"grants\.example"
PANEL_TAG = "GRANTKEEPER_PANEL"

FACETS = ["SCOPE", "MILESTONES", "BUDGET", "TIMELINE", "BENEFICIARIES"]

PLEDGE = (
    "Milestone grant pledge. SCOPE: ship an open-source audit dashboard. "
    "MILESTONES: alpha in month two, public beta in month four. "
    "BUDGET: 40,000 USD, with 60 percent to engineering. "
    "TIMELINE: completed within six months of funding. "
    "BENEFICIARIES: independent security researchers in the ecosystem."
)
REPORT = (
    "Final delivery report for the audit dashboard grant. The dashboard shipped as open source. "
    "Alpha landed in month two and the public beta in month four. Spending totaled roughly forty "
    "thousand dollars with the majority on engineering. The work finished inside the six month window. "
    "Independent security researchers are the primary users today."
)


def panel(verdicts=None):
    verdicts = verdicts or ["KEPT"] * 5
    return {"facets": [{"facet": f, "verdict": verdicts[i], "note": "ok"} for i, f in enumerate(FACETS)]}


def mock_panel(vm, value):
    vm.mock_llm(PANEL_TAG, json.dumps(value))


def open_grant(contract):
    return contract.open_grant("alpha-grant", "Audit Dashboard Team", PLEDGE, "Tranche 2")


def filed(contract, vm, notice="NONE"):
    ref = open_grant(contract)
    contract.file_delivery(ref, EVIDENCE_URL, notice)
    vm.mock_web(EVIDENCE_PATTERN, {"method": "GET", "status": 200, "body": REPORT})
    return ref


def test_contract_loads(direct_deploy):
    assert direct_deploy(CONTRACT) is not None


def test_pledge_locked_and_validated(direct_vm, direct_deploy):
    contract = direct_deploy(CONTRACT)
    with direct_vm.expect_revert("pledge text are required"):
        contract.open_grant("alpha-grant", "Team", "too short", "T1")
    ref = open_grant(contract)
    record = contract.get_grant(ref)
    assert record["status"] == "PLEDGE_LOCKED"
    assert len(record["pledge_sha256"]) == 64
    with direct_vm.expect_revert("already exists"):
        open_grant(contract)


def test_file_delivery_requires_steward_https_and_single_use(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy(CONTRACT)
    ref = open_grant(contract)
    with direct_vm.expect_revert("public https"):
        contract.file_delivery(ref, "http://grants.example/x", "NONE")
    steward = contract.get_grant(ref)["steward"]
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("Only the grant steward"):
        contract.file_delivery(ref, EVIDENCE_URL, "NONE")
    direct_vm.sender = bytes.fromhex(steward[2:])
    contract.file_delivery(ref, EVIDENCE_URL, "NONE")
    with direct_vm.expect_revert("filed once"):
        contract.file_delivery(ref, EVIDENCE_URL, "NONE")


def test_audit_requires_filed_delivery(direct_vm, direct_deploy):
    contract = direct_deploy(CONTRACT)
    ref = open_grant(contract)
    with direct_vm.expect_revert("filed delivery is required"):
        contract.audit(ref)


def test_all_kept_clears_and_is_terminal(direct_vm, direct_deploy):
    contract = direct_deploy(CONTRACT)
    ref = filed(contract, direct_vm)
    mock_panel(direct_vm, panel())
    result = contract.audit(ref)
    assert result["outcome"] == "DELIVERED"
    assert [row["facet"] for row in result["facets"]] == FACETS
    gate = contract.get_gate(ref)
    assert gate["status"] == "DELIVERED" and gate["gate"] == "CLEARED"
    direct_vm.clear_mocks()
    with direct_vm.expect_revert("filed delivery is required"):
        contract.audit(ref)


def test_silent_change_is_revoked(direct_vm, direct_deploy):
    contract = direct_deploy(CONTRACT)
    ref = filed(contract, direct_vm)
    mock_panel(direct_vm, panel(["KEPT", "KEPT", "AMENDED_SILENT", "KEPT", "KEPT"]))
    assert contract.audit(ref)["outcome"] == "DIVERTED"
    assert contract.get_gate(ref)["gate"] == "REVOKED"


def test_disclosed_change_is_conditional(direct_vm, direct_deploy):
    contract = direct_deploy(CONTRACT)
    ref = filed(contract, direct_vm, notice="BUDGET reallocated to audits with board approval.")
    mock_panel(direct_vm, panel(["KEPT", "KEPT", "AMENDED_DISCLOSED", "KEPT", "KEPT"]))
    assert contract.audit(ref)["outcome"] == "REVISED"
    assert contract.get_gate(ref)["gate"] == "CONDITIONAL"


def test_unverifiable_is_held(direct_vm, direct_deploy):
    contract = direct_deploy(CONTRACT)
    ref = filed(contract, direct_vm)
    mock_panel(direct_vm, panel(["KEPT", "UNVERIFIABLE", "KEPT", "KEPT", "KEPT"]))
    assert contract.audit(ref)["outcome"] == "UNPROVEN"
    assert contract.get_gate(ref)["gate"] == "HELD"


def test_panel_output_is_schema_checked(direct_vm, direct_deploy):
    contract = direct_deploy(CONTRACT)
    ref = filed(contract, direct_vm)
    short = panel(); short["facets"].pop()
    mock_panel(direct_vm, short)
    with direct_vm.expect_revert("accountability facet"):
        contract.audit(ref)
    direct_vm.clear_mocks()
    direct_vm.mock_web(EVIDENCE_PATTERN, {"method": "GET", "status": 200, "body": REPORT})
    disordered = panel(); disordered["facets"][0]["facet"] = "BUDGET"
    mock_panel(direct_vm, disordered)
    with direct_vm.expect_revert("out of order"):
        contract.audit(ref)
    direct_vm.clear_mocks()
    direct_vm.mock_web(EVIDENCE_PATTERN, {"method": "GET", "status": 200, "body": REPORT})
    bad = panel(); bad["facets"][0]["verdict"] = "MAYBE"
    mock_panel(direct_vm, bad)
    with direct_vm.expect_revert("not in the allowed set"):
        contract.audit(ref)

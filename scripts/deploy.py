#!/usr/bin/env python3
"""Deploy GrantKeeper to GenLayer studionet.

    source ~/.genlayer/env.sh
    python3 scripts/deploy.py
"""
import os
import sys
import json
import pathlib

from genlayer_py import create_client, create_account, chains

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTRACT = ROOT / "contracts" / "grant_keeper.py"


def main() -> int:
    key = os.environ.get("GENLAYER_PRIVATE_KEY")
    if not key:
        print("GENLAYER_PRIVATE_KEY missing — run: source ~/.genlayer/env.sh")
        return 1
    client = create_client(chain=chains.studionet, account=create_account(key))
    code = CONTRACT.read_bytes()
    print(f"Deploying {CONTRACT.name} ({len(code)} bytes) to studionet (61999)...")
    tx = client.deploy_contract(code=code, args=[])
    print("deploy tx:", tx)
    receipt = client.wait_for_transaction_receipt(
        transaction_hash=tx, status="ACCEPTED", interval=5, retries=120
    )
    address = _address_from(receipt)
    status = receipt.get("status_name") or receipt.get("status")
    print("status:", status)
    if not address:
        print("could not locate contract address in receipt; dumping keys:")
        print(sorted(receipt.keys()) if isinstance(receipt, dict) else dir(receipt))
        return 2
    print("CONTRACT_ADDRESS:", address)
    (ROOT / "deployment.json").write_text(
        json.dumps({"network": "studionet", "chain_id": 61999, "deploy_tx": tx, "contract_address": address}, indent=2)
    )
    print("wrote deployment.json")
    return 0


def _address_from(receipt) -> str:
    if not isinstance(receipt, dict):
        return ""
    for key in ("contract_address", "to_address", "recipient"):
        value = receipt.get(key)
        if value and str(value).startswith("0x") and len(str(value)) == 42 and value != "0x" + "0" * 40:
            return value
    data = receipt.get("data")
    if isinstance(data, dict):
        for key in ("contract_address", "contractAddress", "address"):
            value = data.get(key)
            if value:
                return value
    return ""


if __name__ == "__main__":
    sys.exit(main())

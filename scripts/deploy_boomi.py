import json
import os
import requests
import sys
import time

ACCOUNT_ID = os.environ['BOOMI_ACCOUNT_ID']
USERNAME = os.environ['BOOMI_USERNAME']
PASSWORD = os.environ['BOOMI_PASSWORD']
ENV_ID = os.environ['BOOMI_ENV_ID']
RUN_NUMBER = os.environ.get('GITHUB_RUN_NUMBER', '1')

BASE_URL = f"https://api.boomi.com/api/rest/v1/{ACCOUNT_ID}"

def call_api(endpoint, payload):
    response = requests.post(
        f"{BASE_URL}/{endpoint}",
        auth=(USERNAME, PASSWORD),
        json=payload
    )

    print(f"\n Response: {response.packageId}")
    
    try:
        data = response.json()
    except:
        print("Invalid JSON response")
        sys.exit(1)

    if isinstance(data, dict) and data.get('@type') == 'Error':
        print(f"Boomi Error: {data.get('message')}")
        return None

    return data


def main():
    with open('configs/components.json') as f:
        components = json.load(f)['components']

    failed = False

    for c in components:
        comp_id = c['componentId']
        version = f"{c['packageVersion']}.{RUN_NUMBER}"
        name = c['name']
        notes = c.get('notes', 'Deployed via GitHub Actions')

        print(f"\n--- Deploying {name} ---")

        pkg = call_api("PackagedComponent", {
            "componentId": comp_id,
            "packageVersion": version,
            "notes": notes
        })

        if not pkg:
            failed = True
            continue

        print(f"\n--- Package Component Response {pkg} ---")

        pkg_id = pkg.get("packageId")
        print(f"Package ID: {pkg_id}")

        deploy = call_api("DeployedPackage", {
            "environmentId": ENV_ID,
            "packageId": pkg_id,
            "notes": f"Run #{RUN_NUMBER}"
        })

        if not deploy:
            failed = True
            continue

        print(f"SUCCESS: {name}")
        time.sleep(0.5)

    if failed:
        print("Some deployments failed")
        sys.exit(1)

    print("All deployments successful")


if __name__ == "__main__":
    main()

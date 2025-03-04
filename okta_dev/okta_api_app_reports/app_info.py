import requests
import csv
import time

OKTA_DOMAIN = "https://biogen-test.oktapreview.com"
API_TOKEN = "00zSc7l6hB-lwqART1Ok7wNNmhyvnQJvy7I3TKG8Ao"

HEADERS = {
    "Authorization": f"SSWS {API_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def get_applications():
    url = f"{OKTA_DOMAIN}/api/v1/apps"
    apps = []
    while url:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        apps.extend(response.json())
        url = response.links.get('next', {}).get('url')
        time.sleep(0.2)  # Rate limit protection
    return apps

def get_policy_details(policy_id):
    policy_url = f"{OKTA_DOMAIN}/api/v1/policies/{policy_id}"
    policy_response = requests.get(policy_url, headers=HEADERS)
    policy_response.raise_for_status()
    policy = policy_response.json()

    rules_url = f"{OKTA_DOMAIN}/api/v1/policies/{policy_id}/rules"
    rules_response = requests.get(rules_url, headers=HEADERS)
    rules_response.raise_for_status()
    rules = rules_response.json()

    return {'policy': policy, 'rules': rules}

def parse_policy_rules(rules):
    rule_details = []
    for rule in rules:
        actions = rule.get('actions', {}).get('appSignOn', {})
        verification_method = actions.get('verificationMethod', {})
        
        rule_data = {
            'rule_name': rule.get('name', 'N/A'),
            'factor_mode': verification_method.get('factorMode', 'N/A'),
        }
        rule_details.append(rule_data)
    return rule_details

def main():
    try:
        apps = get_applications()
        results = []
        for app in apps:
            app_name = app.get('label', 'N/A')
            auth_type = app.get('signOnMode', 'N/A')
            policy_id = app.get('_links', {}).get('accessPolicy', {}).get('href', '').split('/')[-1]

            policy_data = None
            rules_data = []
            
            if policy_id:
                policy_details = get_policy_details(policy_id)
                if policy_details:
                    policy = policy_details['policy']
                    rules = policy_details['rules']
                    rules_data = parse_policy_rules(rules)
                    
                    policy_data = {
                        'policy_name': policy.get('name', 'N/A'),
                        'policy_type': policy.get('type', 'N/A'),
                        'policy_status': policy.get('status', 'N/A')
                    }

            results.append({
                "Application Name": app_name,
                "Auth Type": auth_type,
                "Policy Name": policy_data['policy_name'] if policy_data else 'N/A',
                "Policy Status": policy_data['policy_status'] if policy_data else 'N/A',
                "Policy Rules": "; ".join([r['rule_name'] for r in rules_data]),
                "Factor Modes": "; ".join([r['factor_mode'] for r in rules_data if r['factor_mode'] != 'N/A'])
            })

        with open("okta_applications.csv", "w", newline="") as csvfile:
            fieldnames = [
                "Application Name", "Auth Type", "Policy Name", "Policy Status",
                "Policy Rules", "Factor Modes"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print("CSV file created successfully")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

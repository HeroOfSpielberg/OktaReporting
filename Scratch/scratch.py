#!/usr/bin/env python3
import requests
import time
import csv

# Replace with your actual Okta domain and API token
OKTA_DOMAIN = "https://biogen-test.oktapreview.com"
API_TOKEN = "00zSc7l6hB-lwqART1Ok7wNNmhyvnQJvy7I3TKG8Ao"

# Common headers for API requests
HEADERS = {
    "Authorization": f"SSWS {API_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def get_applications():
    """
    Retrieves all applications from your Okta instance.
    Handles pagination via the 'next' link in API responses.
    """
    url = f"{OKTA_DOMAIN}/api/v1/apps"
    apps = []
    while url:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        apps.extend(response.json())
        url = response.links.get('next', {}).get('url')
    return apps

def get_user_count(app_id, max_retries=5):
    """
    Retrieves the user count for a specific application.
    Handles pagination and rate limiting (HTTP 429 responses).
    """
    url = f"{OKTA_DOMAIN}/api/v1/apps/{app_id}/users"
    count = 0
    while url:
        retries = 0
        while retries < max_retries:
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "1"))
                print(f"429 Rate limit hit for App ID {app_id}. Sleeping for {retry_after} seconds...")
                time.sleep(retry_after)
                retries += 1
            else:
                break
        response.raise_for_status()
        users = response.json()
        count += len(users)
        url = response.links.get("next", {}).get("url")
    return count

def main():
    apps = get_applications()
    if not apps:
        print("No applications found!")
        return

    results = []
    for app in apps:
        app_name = app.get("label") or "N/A"
        auth_type = app.get("signOnMode") or "N/A"
        app_id = app.get("id")
        if not app_id:
            continue
        try:
            user_count = get_user_count(app_id)
        except requests.exceptions.HTTPError as err:
            print(f"Error processing app '{app_name}' (ID: {app_id}): {err}")
            user_count = "Error"
        results.append({
            "Application Name": app_name,
            "Auth Type": auth_type,
            "User Count": user_count
        })

    # Write results to a CSV file with headers.
    with open("okta_applications.csv", "w", newline="") as csvfile:
        fieldnames = ["Application Name", "Auth Type", "User Count"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in results:
            writer.writerow(entry)

    print("CSV file 'okta_applications.csv' has been created successfully.")

if __name__ == "__main__":
    main()
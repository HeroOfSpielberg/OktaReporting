import requests

OKTA_DOMAIN = "https://biogen-test.oktapreview.com"
API_TOKEN = "00zSc7l6hB-lwqART1Ok7wNNmhyvnQJvy7I3TKG8Ao"
APP_ID = "0oaiiw7fyhBv6gS5Q1d7"

HEADERS = {
    "Authorization": f"SSWS {API_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def get_app_details(app_id):
    url = f"{OKTA_DOMAIN}/api/v1/apps/{app_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def main():
    try:
        app_details = get_app_details(APP_ID)

        print("Application Details:")
        print(f"Name: {app_details.get('label')}")
        print(f"Authentication Type: {app_details.get('signOnMode')}")
        print(f"Status: {app_details.get('status')}")
        print(f"Created: {app_details.get('created')}")
        print(f"Last Updated: {app_details.get('lastUpdated')}")

        settings = app_details.get('settings', {})
        sign_on = settings.get('signOn', {})
        print(f"\nSSO ACS URL: {sign_on.get('ssoAcsUrl')}")
        print(f"Audience: {sign_on.get('audience')}")

        credentials = app_details.get('credentials', {})
        signing = credentials.get('signing', {})
        print(f"\nSigning Key ID: {signing.get('kid')}")

    except requests.exceptions.HTTPError as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    main()

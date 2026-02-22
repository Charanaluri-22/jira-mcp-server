import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")

auth = (JIRA_EMAIL, JIRA_API_TOKEN)

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}


def get_ticket(issue_key: str):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"
    params = {
        "fields": "summary,description,status,priority,assignee,reporter,issuetype,labels,components,created,updated"
    }
    response = requests.get(url, headers=headers, auth=auth, params=params)
    print("GET TICKET STATUS:", response.status_code)
    print("RAW RESPONSE:", response.text)
    return response.json()

def add_comment(issue_key: str, comment: str):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/comment"

    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"text": comment, "type": "text"}]
                }
            ]
        }
    }


    response = requests.post(url, json=payload, headers=headers, auth=auth)
    print("ADD COMMENT STATUS:", response.status_code)
    print("COMMENT RESPONSE:", response.text)
    return response.json()


def get_transitions(issue_key: str):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/transitions"
    response = requests.get(url, headers=headers, auth=auth)
    print("TRANSITIONS STATUS:", response.status_code)
    print("TRANSITIONS:", response.text)
    return response.json()


def transition_issue(issue_key: str, transition_id: str):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/transitions"
    payload = {
        "transition": {
            "id": transition_id
        }
    }
    response = requests.post(url, json=payload, headers=headers, auth=auth)
    print("TRANSITION STATUS:", response.status_code)
    print("TRANSITION RESPONSE:", response.text)
    return response.status_code
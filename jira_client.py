import os
import logging
import requests
from dotenv import load_dotenv

from logging_config import setup_logging

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

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
    logger.info("GET ticket %s -> %s", issue_key, response.status_code)
    logger.debug("GET ticket response body: %s", response.text)
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
    logger.info("Add comment %s -> %s", issue_key, response.status_code)
    logger.debug("Add comment response body: %s", response.text)
    return response.json()


def get_transitions(issue_key: str):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/transitions"
    response = requests.get(url, headers=headers, auth=auth)
    logger.info("Get transitions %s -> %s", issue_key, response.status_code)
    logger.debug("Transitions response body: %s", response.text)
    return response.json()


def transition_issue(issue_key: str, transition_id: str):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/transitions"
    payload = {
        "transition": {
            "id": transition_id
        }
    }
    response = requests.post(url, json=payload, headers=headers, auth=auth)
    logger.info(
        "Transition issue %s with transition %s -> %s",
        issue_key,
        transition_id,
        response.status_code,
    )
    logger.debug("Transition response body: %s", response.text)
    return response.status_code

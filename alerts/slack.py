"""
slack.py

Sends a notification to a Slack channel via Incoming Webhook whenever
new matching stories are found.

Uses a webhook URL kept OUT of the code (in a GitHub secret / env
variable) so it's never exposed in the public repo.
"""

import os
import requests


def send_slack_alert(new_items: list[dict]) -> None:
    """
    Sends one Slack message summarizing all new matches from this run.
    Does nothing if no webhook URL is configured, or if there's
    nothing new to report — this keeps the pipeline safe to run
    even before Slack is set up.
    """
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")

    if not webhook_url:
        print("ℹ️ No SLACK_WEBHOOK_URL set — skipping Slack alert")
        return

    if not new_items:
        return

    lines = []
    for item in new_items:
        lines.append(f"• <{item['url']}|{item['title']}>  _(via {item['source']})_")

    message = {
        "text": f"🔎 *TrendWatch found {len(new_items)} new signal(s):*\n\n" + "\n".join(lines)
    }

    try:
        response = requests.post(webhook_url, json=message, timeout=10)
        response.raise_for_status()
        print(f"✅ Slack alert sent for {len(new_items)} item(s)")
    except Exception as e:
        # Never let a failed alert crash the whole pipeline —
        # scraping/saving data matters more than the notification.
        print(f"⚠️ Failed to send Slack alert: {e}")
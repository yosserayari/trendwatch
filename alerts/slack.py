import os
import requests

from scraper.sanitize import sanitize_item


def send_slack_alert(new_items: list[dict]) -> None:
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")

    if not webhook_url:
        print("No SLACK_WEBHOOK_URL set — skipping Slack alert")
        return

    if not new_items:
        return

    lines = []
    for item in new_items:
        clean_item = sanitize_item(item)
        if clean_item is None:
            print(f"Skipped item with invalid URL: {item.get('title', '(no title)')!r}")
            continue
        lines.append(f"• <{clean_item['url']}|{clean_item['title']}>  _(via {clean_item['source']})_")

    if not lines:
        return

    message = {
        "text": f"*TrendWatch found {len(lines)} new signal(s):*\n\n" + "\n".join(lines)
    }

    try:
        response = requests.post(webhook_url, json=message, timeout=10)
        response.raise_for_status()
        print(f"Slack alert sent for {len(lines)} item(s)")
    except Exception as e:
        print(f"⚠️ Failed to send Slack alert: {e}")
"""
discord.py

Sends a notification to a Discord channel via webhook whenever
new matching stories are found.

Uses a webhook URL kept OUT of the code (in a GitHub secret / env
variable) so it's never exposed in the public repo.
"""

import os
import requests


def send_discord_alert(new_items: list[dict]) -> None:
    """
    Sends one Discord message summarizing all new matches from this run.
    Does nothing if no webhook URL is configured, or if there's
    nothing new to report — this keeps the pipeline safe to run
    even before Discord is set up.
    """
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        print("ℹ️ No DISCORD_WEBHOOK_URL set — skipping Discord alert")
        return

    if not new_items:
        return

    lines = []
    for item in new_items:
        lines.append(f"• **[{item['title']}]({item['url']})** _(via {item['source']})_")

    message = {
        "content": f"🔎 **TrendWatch found {len(new_items)} new signal(s):**\n\n" + "\n".join(lines)
    }

    try:
        response = requests.post(webhook_url, json=message, timeout=10)
        response.raise_for_status()
        print(f"✅ Discord alert sent for {len(new_items)} item(s)")
    except Exception as e:
        # Never let a failed alert crash the whole pipeline —
        # scraping/saving data matters more than the notification.
        print(f"⚠️ Failed to send Discord alert: {e}")
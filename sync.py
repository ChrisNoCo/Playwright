import os
import json
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, expect

LOG_FILE = "log.json"

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return []

def save_log(entries):
    with open(LOG_FILE, "w") as f:
        json.dump(entries, f, indent=2)

def run_sync():
    messages = []
    status = "success"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto("https://www.valuesinteaching.org/manage")
            page.fill("#login", os.environ["VIT_USERNAME"])
            page.fill("#password", os.environ["VIT_PASSWORD"])
            page.click("button.login-submit-button")
            page.wait_for_load_state("networkidle")

            expect(page.locator(".userinfo__logoutlink")).to_be_attached()
            messages.append("✓ Login verified — logout link is present")

            page.goto(os.environ["VIT_COURSE_URL"])
            page.wait_for_load_state("networkidle")
            messages.append("✓ Navigated to course content page")

            if page.locator("#syncing-complete").is_visible():
                messages.append("ℹ️ Already in sync — no changes to sync")
                status = "skipped"
            else:
                expect(page.locator("#sync-button")).to_be_visible()
                page.click("#sync-button")
                messages.append("✓ Sync button clicked")

                expect(page.locator("#syncing-complete")).to_be_visible(timeout=30000)
                messages.append("✓ Sync complete — 'All changes synced' message appeared")

            browser.close()

    except Exception as e:
        messages.append(f"✗ Error: {str(e)}")
        status = "failed"

    return status, messages

# Run and log
status, messages = run_sync()
timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

entry = {
    "timestamp": timestamp,
    "status": status,
    "messages": messages
}

for msg in messages:
    print(msg)

log = load_log()
log.insert(0, entry)  # newest first
save_log(log)

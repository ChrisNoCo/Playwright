import os
from playwright.sync_api import sync_playwright, expect

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Navigate to login page
    page.goto("https://www.valuesinteaching.org/manage")

    # Fill in credentials from environment variables
    page.fill("#login", os.environ["VIT_USERNAME"])
    page.fill("#password", os.environ["VIT_PASSWORD"])

    # Submit
    page.click("button.login-submit-button")

    # Wait for page to load
    page.wait_for_load_state("networkidle")

    # Verify login succeeded — logout link exists in DOM
    expect(page.locator(".userinfo__logoutlink")).to_be_attached()
    print("✓ Login verified — logout link is present")

    # Navigate to course content page
    page.goto("https://www.valuesinteaching.org/courses/3048746/content")
    page.wait_for_load_state("networkidle")
    print("✓ Navigated to course content page")

    # If already synced, nothing to do
    if page.locator("#syncing-complete").is_visible():
        print("ℹ️ Already in sync — no changes to sync. Exiting.")
        browser.close()
        exit(0)

    # Click the sync button
    expect(page.locator("#sync-button")).to_be_visible()
    page.click("#sync-button")
    print("✓ Sync button clicked")

    # Wait for sync to complete
    expect(page.locator("#syncing-complete")).to_be_visible(timeout=30000)
    print("✓ Sync complete — 'All changes synced' message appeared")

    browser.close()

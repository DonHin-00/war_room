from playwright.sync_api import sync_playwright
import time

def verify(page):
    # OmegaBank Verification
    print("Navigating to OmegaBank...")
    page.goto("http://localhost:5000/auth/login")
    page.fill("input[name='username']", "alice")
    page.fill("input[name='password']", "password123")
    page.click("button[type='submit']")
    page.wait_for_selector(".dashboard")
    print("LoggedIn. Taking screenshot...")
    page.screenshot(path="verification_bank.png")

    # SOC Verification
    print("Navigating to SOC Dashboard...")
    page.goto("http://localhost:5001")
    page.wait_for_selector(".header")
    time.sleep(5) # Wait for stats to load via JS
    print("SOC Loaded. Taking screenshot...")
    page.screenshot(path="verification_soc.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify(page)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

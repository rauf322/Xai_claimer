import asyncio
import os
from patchright.async_api import async_playwright, Page
from metamask_notification import find_metamask_page
from xai_claimer import xai_claimer
from dotenv import load_dotenv,dotenv_values
        

path_to_extension = "./Extensions/MetaMask-Chrome-Web-Store"
user_data_dir = "/Users/rauffaizov/Work/programming/python/Playwright/Chrome" 


async def run(playwright):
    context = await playwright.chromium.launch_persistent_context(
        user_data_dir,
        channel="chrome",
        args=[
            '--disable-blink-features=AutomationControlled',
            f"--disable-extensions-except={path_to_extension}",
            f"--load-extension={path_to_extension}",
        ],
        headless=False,
    )
    mnemonics = os.getenv("SEED")
    extensions = {}

    await asyncio.sleep(5)
    page = await context.new_page()
    await page.set_viewport_size({"width": 1920, "height": 1080})
    await page.goto("chrome://extensions/")

    # Wait for elements to appear
    await page.wait_for_selector("div#card")

    # Get all extension elements
    extension_elements = await page.query_selector_all("div#card")
    
    for element in extension_elements:
        name_element = await element.query_selector("div#name")
        name = (await name_element.text_content()).strip()

        details = await element.query_selector("cr-button#detailsButton")
        await details.click()

        # Wait for navigation to the details page
        await page.wait_for_load_state("domcontentloaded")
        extension_url = page.url.split("=")[1].strip()

        extensions[name] = extension_url
        print(f"{name}: {extension_url}")

        # Go back to the extensions page
        back = await page.query_selector("cr-icon-button#closeButton")
        await back.click()

        # Wait before interacting with the next element
        await asyncio.sleep(1)

    if "MetaMask" not in extensions:
        raise RuntimeError("MetaMask extension not found!")

    metaMask = extensions["MetaMask"]
    await page.goto(f"chrome-extension://{metaMask}/home.html#onboarding/welcome")

    # Accept terms
    await page.get_by_test_id("onboarding-terms-checkbox").click()
    
    # Import an existing wallet
    await page.get_by_text("Import an existing wallet").click()
    await page.get_by_text("No thanks").click()

    # Fill in the Secret Recovery Phrase (SRP)
    mnemonics = mnemonics.split(" ")
    for index in range(12):
        input_element = page.get_by_test_id(f'import-srp__srp-word-{index}')
        await input_element.fill(mnemonics[index])

    # Confirm and set password
    await page.get_by_test_id("import-srp-confirm").click()
    await page.get_by_test_id("create-password-new").fill("xipxop2013")
    await page.get_by_test_id("create-password-confirm").fill("xipxop2013")
    await page.get_by_test_id("create-password-terms").click()
    await page.get_by_test_id("create-password-import").click()

    # Complete onboarding
    await page.get_by_test_id("onboarding-complete-done").click()
    await page.get_by_test_id("pin-extension-next").click()
    await page.get_by_test_id("pin-extension-done").click()
    
# ----------------------------------------------------------------------------------------------------------------------------
    await xai_claimer(page, context)

    await asyncio.Future()

    await context.close()

    
async def main():
    async with async_playwright() as playwright:
        await run(playwright)


if __name__ == "__main__":
    asyncio.run(main())
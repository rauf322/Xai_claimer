from metamask_notification import find_metamask_page
import asyncio

async def xai_claimer(page, context):
    await page.goto("https://app.xai.games/staking?chainId=undefined&search=&page=1&showKeys=false&hideFull=true&hideFullKeys=false&sort=tierIndex&sortOrder=-1&esXaiMinStake=0")

    # Check if modal exists
    modal = page.locator('.bg-black.fixed')
    if await modal.is_visible():
        print("Modal Detected!")
        tick = page.get_by_role("checkbox").first
        await tick.click()
        continue_button = page.locator("button", has_text="Continue")
        await continue_button.wait_for(state="visible")
        await continue_button.click()

    # Connect Wallet
    connect_wallet = page.get_by_role("button", name="CONNECT WALLET").first
    await connect_wallet.click()
    wallet = page.get_by_role("button", name="MetaMask").first
    await wallet.click()

    await asyncio.sleep(3)

    metamask_page = await find_metamask_page(context)
    
    
    await metamask_page.get_by_test_id("confirm-btn").click()
    await metamask_page.get_by_test_id("confirmation-submit-button").click()

    await asyncio.sleep(3)

        # Extract balance correctly
    mined = page.locator('.mt-1.block.md\\:text-3xl.text-2xl.font-bold.text-white.undefined')
    balance = await mined.text_content()

    # Clean the balance string (removing non-numeric characters)
    balance = balance.split(" ")[0].split(".")[0].strip()  # Extracts only the number before any text like 'esXAI'
    print(f"Balance: {balance} esXAI")

    # Ensure balance is numeric before trying to convert it to an integer
    try:
        balance = int(balance)
    except ValueError:
        print(f"Invalid balance value: {balance}")
        balance = 0  # Set to 0 if the balance isn't a valid number

# Check if balance is greater than 100
    if balance > 100:
        print("We need to claim")
        
        # Click the "CLAIM" button
        claim = page.get_by_role("button", name="CLAIM").first
        await claim.click()
        await asyncio.sleep(3)

        # Handle MetaMask confirmation
        metamask_page = await find_metamask_page(context)
        await metamask_page.get_by_test_id("confirm-footer-button").click()
        await asyncio.sleep(3)

        # Check balance again after claiming
        mined = page.locator('.mt-1.block.md\\:text-3xl.text-2xl.font-bold.text-white.undefined')
        new_balance = await mined.text_content()
        new_balance = new_balance.split(" ")[0].strip()
        print(f"New Balance: {new_balance}")

        # Check if the balance was claimed successfully
        if new_balance == "0":
            print("Claimed successfully!")
        else:
            print(f"Claim failed. New balance: {new_balance}")
        
        # Click the "REDEEM" button
        await page.get_by_text("REDEEM").click()
        span_element = page.locator('div.flex.w-full.justify-center.my-3.relative span.cursor-pointer')
        await span_element.click()
        await asyncio.sleep(2)
        balance_div = page.locator('div.w-max.md\\:w-full.text-elementalGrey.text-lg.font-medium.flex.items-center.justify-end.gap-2')
        whole_balance = await balance_div.locator('span.block').first.text_content()
        digits_of_balance = whole_balance.split(":")[1].split(" ")[1].split(".")[0]
        input_element = page.locator('input[placeholder="0"]').first
        await input_element.fill(digits_of_balance)
        await page.locator("div.false.w-full button").first.click()
        await asyncio.sleep(1)
        await page.locator("div.false.w-full button").first.click()
        await asyncio.sleep(4)
        metamask_page = await find_metamask_page(context)
        await metamask_page.get_by_test_id("confirm-footer-button").click()
    else:
        print("Balance is not enough!")
        return 
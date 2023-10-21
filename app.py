from pyppeteer import launch
from quart import Quart, request, jsonify

app = Quart(__name__)

async def scrape_data(consumer_number, subdivision_code, registered_mobile):
    browser = await launch(headless=True, executablePath='/opt/render/.local/share/pyppeteer/local-chromium/588429/chrome-linux/chrome')
    page = await browser.newPage()
    await page.goto("https://www.recharge1.com/online-electricity-bill-payment/jbvnl-jharkhand.aspx")
    await page.type("#ctl00_ContentPlaceHolder2_UtilityControlId_TXT_Consumer_Number", consumer_number)
    await page.select("#ctl00_ContentPlaceHolder2_UtilityControlId_DDL_Subdivision_Code", subdivision_code)
    await page.type("#ctl00_ContentPlaceHolder2_UtilityControlId_TXTCustomerNumber", registered_mobile)
    await page.click("#ctl00_ContentPlaceHolder2_UtilityControlId_BtnCheckBill")
    await page.waitForSelector("#ctl00_ContentPlaceHolder2_UtilityControlId_ctl01_lblheading")
    consumer_number = await page.evaluate('() => document.evaluate("//span[text()=\'Consumer Number\']/following-sibling::span[1]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent')
    total_arrears = await page.evaluate('() => document.evaluate("//span[text()=\'Total Arrears\']/following-sibling::span[1]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent')
    net_amount = await page.evaluate('() => document.evaluate("//span[text()=\'Net Demand\']/following-sibling::span[1]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent')
    consumer_name = await page.evaluate('() => document.evaluate("//span[text()=\'CustomerName\']/following-sibling::span[1]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent')
    bill_number = await page.evaluate('() => document.evaluate("//span[text()=\'BillNumber\']/following-sibling::span[1]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent')
    due_date = await page.evaluate('() => document.evaluate("//span[text()=\'DueDate\']/following-sibling::span[1]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent')
    await browser.close()
    result = {
        "Consumer Name": consumer_name.strip(),
        "Consumer Number": consumer_number.strip(),
        "Total Arrears": total_arrears.strip(),
        "Bill Number": bill_number.strip(),
        "Due Date": due_date.strip(),
        "Net Amount": net_amount.strip(),
    }
    return result

@app.route('/scrape', methods=['POST'])
async def scrape():
    try:
        data = await request.get_json()
        consumer_number = data.get("consumer_number")
        subdivision_code = data.get("subdivision_code")
        registered_mobile = data.get("registered_mobile")
        result = await scrape_data(consumer_number, subdivision_code, registered_mobile)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    import os
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        import asyncio
        asyncio.get_event_loop().run_until_complete(scrape_data("your_consumer_number", "your_subdivision_code", "your_registered_mobile"))
    app.run()

from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape_data():
    # Parse input data in JSON format
    data = request.get_json()
    consumer_number = data.get('consumer_number')
    subdivision_code = data.get('subdivision_code')
    mobile_number = data.get('mobile_number')

    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # Initialize the Selenium web driver with Chrome options
    driver = webdriver.Chrome(options=chrome_options)

    # Base URL
    base_url = "https://www.recharge1.com/online-electricity-bill-payment/jbvnl-jharkhand.aspx"

    # Open the webpage
    driver.get(base_url)

    # Fill in the form data
    driver.find_element(By.ID, "ctl00_ContentPlaceHolder2_UtilityControlId_TXT_Consumer_Number").send_keys(consumer_number)

    # Select the Subdivision Code
    subdivision_dropdown = Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder2_UtilityControlId_DDL_Subdivision_Code"))
    subdivision_dropdown.select_by_value(subdivision_code)

    driver.find_element(By.ID, "ctl00_ContentPlaceHolder2_UtilityControlId_TXTCustomerNumber").send_keys(mobile_number)

    # Click the "Check Bill" button
    driver.find_element(By.ID, "ctl00_ContentPlaceHolder2_UtilityControlId_BtnCheckBill").click()

    # Add explicit waits to ensure elements are present
    wait = WebDriverWait(driver, 5)  # Wait up to 10 seconds

    try:
        # Parse the data from the popup
        data_to_scrape = {
            "Consumer Number": consumer_number,
            "Total Arrears": wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Total Arrears')]/following-sibling::span"))).text,
            "Net Amount": wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Net Demand')]/following-sibling::span"))).text,
            "Consumer Name": wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'CustomerName')]/following-sibling::span"))).text,
            "Bill Number": wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'BillNumber')]/following-sibling::span"))).text,
            "Due Date": wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'DueDate')]/following-sibling::span"))).text,
        }

    except Exception as e:
        data_to_scrape = {
            "Consumer Number": consumer_number,
            "Total Arrears": "Not Found",
            "Net Amount": "Not Found",
            "Consumer Name": "Not Found",
            "Bill Number": "Not Found",
            "Due Date": "Not Found",
        }

    # Close the browser
    driver.quit()

    return jsonify(data_to_scrape)

if __name__ == '__main__':
    app.run()

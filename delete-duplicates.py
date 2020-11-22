import requests, dbm, os, json, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from chromedriver_py import binary_path # this will get you the path variable


def delete_duplicate(media_item_id):
    return


def main():
    count = 0
    with dbm.open('duplicate_store.db', 'c') as db:
        options = Options()
        options.add_argument(f'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36')
        driver = webdriver.Chrome(options=options, executable_path=binary_path)

        wait = WebDriverWait(driver, 10)

        driver.get("https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount?redirect_uri=https%3A%2F%2Fdevelopers.google.com%2Foauthplayground&prompt=consent&response_type=code&client_id=407408718192.apps.googleusercontent.com&scope=email&access_type=offline&flowName=GeneralOAuthFlow")
        input("Login to Google Photos")

        k = db.firstkey()
        while k != None:
            print(db[k])
            try:
                media_item = json.loads(db[k])
            except:
                k = db.nextkey(k)
                continue
            print("Opening " + media_item['productUrl'])
            driver.get(media_item['productUrl'])

            delete_css = "button[title='Delete']"
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, delete_css)))
            delete_button = driver.find_element_by_css_selector(delete_css)
            delete_button.click()
            time.sleep(2)

            confirm_span_xpath = "//span[text()='Move to trash']"
            confirm_span_elements = driver.find_elements_by_xpath(confirm_span_xpath)
            confirm_span_element = None
            for elem in confirm_span_elements:
                if elem.is_displayed():
                    confirm_span_element = elem
            confirm_button = confirm_span_element.find_element_by_xpath("..")
            time.sleep(2)
            confirm_button.click()

            time.sleep(3)
            db[k] = ""
            input("Next?")

            count += 1
            k = db.nextkey(k)

    print("Duplicates found: " + str(count))
    input("Close?")


if __name__ == "__main__":
    main()
import time
import os
import random
import json
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchFrameException
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import MoveTargetOutOfBoundsException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import JavascriptException
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
import requests
from requests.exceptions import HTTPError
class ProxyExtension:
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Proxy Extension",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {"scripts": ["background.js"]},
        "minimum_chrome_version": "76.0.0"
    }
    """

    background_js = """
    var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: %d
            },
            bypassList: ["localhost"]
        }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        { urls: ["<all_urls>"] },
        ['blocking']
    );
    """

    def __init__(self, path:str, host:str, port:str, user:str, password:str):
        parent_dir = f"{path}/"
        self._dir = os.path.join(parent_dir, "extensions")
        try:
            os.mkdir(self._dir)
        except FileExistsError:
            pass

        try:
            manifest_file = os.path.join(self._dir, "manifest.json")

            with open(manifest_file, mode="w") as f:
                f.write(self.manifest_json)

            background_js = self.background_js % (host, port, user, password)
            background_file = os.path.join(self._dir, "background.js")
            with open(background_file, mode="w") as f:
                f.write(background_js)
        except FileNotFoundError:
            pass


    @property
    def directory(self):
        return self._dir


def main(args=None):

    sleep = time.sleep
    proxy_extension = ProxyExtension(os.getcwd(),'MOBILE_PROXY_IP',int('MOBILE_PROXY_PORT'),'MOBILE_PROXY_USERNAME','MOBILE_PROXY_PASSWORD')
    chrome_options = uc.ChromeOptions()
    chrome_options.arguments.extend(["--no-sandbox", "--disable-setuid-sandbox"])
    chrome_options.add_argument(f"--load-extension={proxy_extension.directory}")

    driver = uc.Chrome(options=chrome_options)

    driver.get('https://twitter.com')
    with open('cookies.json', 'r', newline='') as inputdata:
        cookies = json.load(inputdata)
    for cookie in cookies:
            if 'sameSite' in cookie:
                if cookie['sameSite'] == 'unspecified':
                    cookie['sameSite'] = 'Strict'
                if cookie['sameSite'] == 'no_restriction':
                    cookie['sameSite'] = 'None'
                if cookie['sameSite'] == 'lax':
                    cookie['sameSite'] = 'Lax'
            driver.add_cookie(cookie)
    sleep(5)
    driver.get('https://twitter.com/')
    sleep(5)
    tweets = driver.find_elements(By.XPATH, '//div[@data-testid="tweet"]')
    print(len(tweets))
    for i in tweets:
        tweet_time = i.find_elements(By.XPATH, '//time')
        print(i.get_attribute('innerText'))
    sleep(10)
    driver.quit()


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--no-sleeps", "-ns", action="store_false")
    a = p.parse_args()
    main(a)

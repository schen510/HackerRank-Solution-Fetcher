from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
import time

def GetElement(driver, searchmethod, value):
    try:
        webElement = WebDriverWait(driver, 5).until(EC.presence_of_element_located((searchmethod, value)))
    except:
        return None
    return webElement

def getUserNameAndPassword():
    userName = raw_input('Please input username: ')
    passWord = raw_input('Please input password: ')

    payload = {
        'login': userName,
        'password': passWord,
    }

    return payload

def createSession():
    driver = webdriver.Chrome('/Users/schen/Downloads/chromedriver')
    driver.get("http://www.hackerrank.com/")

    try:
        loginButton = driver.find_element_by_link_text('Log In')
        loginButton.click()

        loginField = GetElement(driver, By.XPATH, "//input[@id='login']")
        loginField.send_keys('stanley.chen0@gmail.com')
        print("Sent UserName")

        passWordField = GetElement(driver, By.XPATH, "//input[@id='password' and @data-attr2='Login']")
        passWordField.send_keys('syferR123@')
        print("Sent PW")

        submitButton = GetElement(driver, By.XPATH, "//button[text()='Log In']")
        submitButton.click()
        print("Sent Click")
    except:
        print("Selenium ran into an exception.")
        driver.close()
        return None

    time.sleep(5)
    return driver

def main():
    #loginInfo = getUserNameAndPassword()
    driver = createSession()



if __name__ == '__main__':
    main()

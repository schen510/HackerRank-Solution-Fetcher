from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def GetElement(driver, searchmethod, value):
    try:
        webElement = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((searchmethod, value)))
    except:
        return None
    return webElement

def GetElements(driver, searchmethod, value):
    try:
        webElements = WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located((searchmethod, value)))
    except:
        return None
    return webElements

def getUserNameAndPassword():
    userName = raw_input('Please input username: ')
    passWord = raw_input('Please input password: ')

    payload = {
        'login': userName,
        'password': passWord,
    }

    return payload

def createSession(load):
    options = webdriver.ChromeOptions()
    options.add_argument("--kiosk")

    driver = webdriver.Chrome('/Users/schen/Downloads/chromedriver', chrome_options=options)
    driver.get("http://www.hackerrank.com/")

    try:
        loginButton = driver.find_element_by_link_text('Log In')
        loginButton.click()

        loginField = GetElement(driver, By.XPATH, "//input[@id='login']")
        loginField.send_keys(load['login'])
        print("Sent UserName")

        passWordField = GetElement(driver, By.XPATH, "//input[@id='password' and @data-attr2='Login']")
        passWordField.send_keys(load['password'])
        print("Sent PW")

        submitButton = GetElement(driver, By.XPATH, "//button[text()='Log In']")
        submitButton.click()
        print("Sent Click")

        dropDown = GetElement(driver, By.XPATH, "//a[span='stanleychen510']")
        dropDown.click()

        submissionlink = GetElement(driver, By.LINK_TEXT, "Submissions")
        submissionlink.click()

        sortByChallengeButton = GetElement(driver, By.XPATH, "//span[text()='Sort by Challenge']/..")
        if not ('active' in sortByChallengeButton.get_attribute('class')):
            sortByChallengeButton.click()

    except:
        print("Selenium ran into an exception.")
        driver.close()
        return None

    return driver

def createAllChallengeLinks(driver):
    dictionaryOfProblems = {}

    while True:
        problems = GetElements(driver, By.XPATH, "//div[@class='clearfix row row-btn row-clear']")
        if not(problems):
            return None

        for problem in problems:
            key = GetElement(problem, By.XPATH, "div[1]/p/a[1]")
            value = GetElement(problem, By.XPATH, "div[6]/a")
            link = key.get_attribute('href') + value.get_attribute('href')[26:]
            dictionaryOfProblems[key.text] = link

        rightPagination = GetElement(driver, By.XPATH, "//a[@data-analytics='Pagination' and @data-attr1='Right']")
        if rightPagination.get_attribute('href'):
            rightPagination.click()
        else:
            break

    return dictionaryOfProblems

def navigateAndScrape(driver, links, github):
    for link in links.keys():
        if (os.path.isdir(github + link)):
            print("Folder %s exists. Skipping folder creation." %(link))
        else:
            print("Folder %s does not exist. Setting up Folder" %(link))
            os.makedirs(github + link)
        driver.get(links[link])
        source = driver.page_source
        soup = BeautifulSoup(source, "lxml")
        soup.encode('utf-8')
        codeLines = soup.find_all("pre", attrs={'class':' CodeMirror-line '})
        with open(github+link+"/main.cpp", "w") as f:
            for line in codeLines:
                codeText = line.find("span", attrs={'role': 'presentation'})
                code = (codeText.text).strip(u'\u200b').replace(u'\xa0', u'')
                f.write(code + "\n")

def main():
    loginInfo = getUserNameAndPassword()
    driver = createSession(loginInfo)
    if not(driver):
        print("INFO - Selenium driver was not created. Ending Script.")
        return 0

    links = createAllChallengeLinks(driver)
    if not(links):
        print("INFO - No links on your submissions page for this account.")

    navigateAndScrape(driver, links, '/Users/schen/Documents/stanley_repo/Hacker Rank Solutions/')


if __name__ == '__main__':
    main()

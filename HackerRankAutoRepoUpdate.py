from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import json
import sys
import git
import datetime

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
    driver = webdriver.PhantomJS()
    driver.set_window_size(1120, 550)
    driver.get("http://www.hackerrank.com/")

    loginButton = driver.find_element_by_link_text('Log In')
    loginButton.click()

    loginField = GetElement(driver, By.XPATH, "//input[@id='login']")
    loginField.send_keys(load['login'])
    time.sleep(1)

    passWordField = GetElement(driver, By.XPATH, "//input[@id='password' and @data-attr2='Login']")
    passWordField.send_keys(load['password'])
    time.sleep(1)

    submitButton = GetElement(driver, By.XPATH, "//button[text()='Log In']")
    submitButton.click()

    driver.get("https://www.hackerrank.com/submissions/grouped")

    sortByChallengeButton = GetElement(driver, By.XPATH, "//span[text()='Sort by Challenge']/..")
    if not ('active' in sortByChallengeButton.get_attribute('class')):
        sortByChallengeButton.click()

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
            print("INFO - Folder %s exists. Skipping folder creation." %(link))
        else:
            print("INFO - Folder %s does not exist. Setting up Folder" %(link))
            os.makedirs(github + link)

        print("INFO - Navigating to %s" %(links[link]))
        driver.get(links[link])
        time.sleep(1)
        source = driver.page_source
        soup = BeautifulSoup(source, "lxml")
        soup.encode('utf-8')
        codeLines = soup.find_all("pre", attrs={'class':' CodeMirror-line '})
        with open(github+link+"/main.cpp", "w") as f:
            for line in codeLines:
                codeText = line.find("span", attrs={'role': 'presentation'})
                code = (codeText.text).strip(u'\u200b').replace(u'\xa0', u'')
                f.write(code + "\n")
        print("INFO - Finished copying code for %s" %(link))

def main():
    if len(sys.argv) < 2:
       print "Usage: python HackerRankAutoRepoUpdate.py [CONFIG_FILE]"
       return 0

    #reads if the config file is in this 
    if os.path.isfile(sys.argv[1]):
        with open(sys.argv[1], 'r') as configJson:
            configLoad = json.load(configJson)
    else:
        "INFO - Configuration file does not exist. Ending execution."
        return 0

    loginInfo = getUserNameAndPassword()
    driver = createSession(loginInfo)
    if not(driver):
        print("INFO - Selenium driver was not created. Ending Script.")
        return 0

    links = createAllChallengeLinks(driver)
    if not(links):
        print("INFO - No links on your submissions page for this account.")

    navigateAndScrape(driver, links, configLoad['hacker_rank_solution_folder'])

    if configLoad['push_to_github']:
        print "Push changes to Github branch enabled. Starting the process."
        repo = git.Repo(configLoad['hacker_rank_solution_folder'])
        print repo.git.status()
        if 'Changes not staged for commit:' in repo.git.status():
            print "Uncommitted changes. Need to commit."
            repo.git.add('--all')
            repo.git.commit(m=('Automated Update after fetching solutions on %s' %(datetime.datetime.now().strftime("%Y-%m-%d"))))
            repo.git.push("origin", "master")
        else:
            print "No changes found. Ending Github update process."

if __name__ == '__main__':
    main()

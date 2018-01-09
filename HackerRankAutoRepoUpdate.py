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
        try:
            webElements = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((searchmethod, value)))
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

def createSession(load,chromedriver):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(chromedriver, chrome_options=options)
    driver.get("http://www.hackerrank.com/")
    time.sleep(1)

    loginButton = driver.find_element_by_link_text('Log In')
    loginButton.click()

    loginField = GetElement(driver, By.XPATH, "//input[@id='login']")
    loginField.send_keys(load['login'])
    time.sleep(1)

    passWordField = GetElement(driver, By.XPATH, "//input[@id='password' and @data-attr2='Login']")
    passWordField.send_keys(load['password'])
    time.sleep(1)

    submitButton = GetElement(driver, By.XPATH, "//button[text()='Log In' and @data-analytics='LoginPassword']")
    submitButton.click()
    time.sleep(2)

    driver.get("https://www.hackerrank.com/submissions/grouped")

    sortByChallengeButton = GetElement(driver, By.XPATH, "//span[text()='Sort by Challenge']/..")
    if not ('active' in sortByChallengeButton.get_attribute('class')):
        sortByChallengeButton.click()

    return driver

def createAllChallengeLinks(driver, github):
    dictionaryOfProblems = {}

    while True:
        problems = GetElements(driver, By.XPATH, "//div[@class='clearfix row row-btn row-clear']")
        if not(problems):
            return None

        for problem in problems:
            key = GetElement(problem, By.XPATH, "div[1]/p/a[1]")
            value = GetElement(problem, By.XPATH, "div[6]/a")
            attempt = '0'
            try:
                attemptString = (GetElement(problem, By.XPATH, "div[1]/p/a[2]").text).split()
                attempt = attemptString[0][2:]
            except:
                attempt = '0'

            link = key.get_attribute('href') + value.get_attribute('href')[26:]

            if (os.path.isdir(github + key.text)):
                print("INFO - Folder %s exists. Skipping folder creation." %(key.text))
                with open(github + key.text + '/attempts.txt', 'r') as f:
                    first_line = f.readline()
                if first_line == attempt:
                    print("INFO - Not updating %s since there has been no changes since last run." %(key.text))
                    continue
                else:
                    with open(github + key.text + '/attempts.txt', 'w') as f:
                        f.write(attempt)
            else:
                print("INFO - Folder %s does not exist. Setting up folder" %(key.text))
                os.makedirs(github + key.text)
                with open(github + key.text + '/attempts.txt', 'w+') as attemptFile:
                    attemptFile.write(attempt)
            dictionaryOfProblems[key.text] = link

        rightPagination = GetElement(driver, By.XPATH, "//a[@data-analytics='Pagination' and @data-attr1='Right']")
        if rightPagination.get_attribute('href'):
            rightPagination.click()
        else:
            break

    return dictionaryOfProblems

def navigateAndScrape(driver, links, github):
    for link in links.keys():
        print("INFO - Navigating to %s" %(links[link]))
        driver.get(links[link])
        time.sleep(1)

        source = driver.page_source
        soup = BeautifulSoup(source,'lxml')
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
    driver = createSession(loginInfo, configLoad['chromedriver_location'])
    if not(driver):
        print("INFO - Selenium driver was not created. Ending Script.")
        return 0

    links = createAllChallengeLinks(driver, configLoad['hacker_rank_solution_folder'])

    if not(links):
        print("INFO - No links on your submissions page for this account. Ending Program.")
        return 0

    navigateAndScrape(driver, links, configLoad['hacker_rank_solution_folder'])

    if configLoad['push_to_github']:
        print "Push changes to Github branch enabled. Starting the process."
        repo = git.Repo(configLoad['hacker_rank_solution_folder'])
        if 'Changes not staged for commit:' in repo.git.status():
            print "Uncommitted changes. Need to commit."
            repo.git.add('--all')
            repo.git.commit(m=('Automated Update after fetching solutions on %s\\n' %(datetime.datetime.now().strftime("%Y-%m-%d"))))
            repo.git.push("origin", "master")
        else:
            print "No changes found. Ending Github update process."
    else:
        print("INFO - Github did not update with any changes because they were not pushed.")

if __name__ == '__main__':
    main()

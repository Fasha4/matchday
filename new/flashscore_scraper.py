from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException, TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import datetime
import json
import os

def getTeams(url):
	options = webdriver.ChromeOptions()
	options.add_argument('--headless')
	options.add_argument('--window-size=1920,1080')
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	options.add_argument('log-level=3')
	options.add_argument('--disable-search-engine-choice-screen')
	driver = webdriver.Chrome(service=ChromeService(), options=options)

	driver.get(url)

	wait = WebDriverWait(driver, 10)
	cookies = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler")))
	cookies.click()

	wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.tableCellParticipant__name')))

	sport = driver.find_element(By.CSS_SELECTOR, '.breadcrumb__link').text.capitalize()
	league_name = driver.find_element(By.CSS_SELECTOR, '.heading__name').text
	league_teams = driver.find_elements(By.CSS_SELECTOR, '.tableCellParticipant__name')
	teams = []
	for team in league_teams:
		teams.append(team.text)

	league = {
		'sport': sport,
		'league': league_name,
		'teams': teams
	}

	return league


if __name__ == '__main__':
	url = input("Podaj link do tabeli:")
	filename = 'scraped/Flashscore.json'
	os.makedirs(os.path.dirname(filename), exist_ok=True)
	with open(filename, 'w', encoding='utf-8') as f:
		matches = getTeams(url)
		json.dump(matches, f, ensure_ascii=False, indent=4)

	print("Wyeksportuj wygenerowany plik do bazy danych")
	input()
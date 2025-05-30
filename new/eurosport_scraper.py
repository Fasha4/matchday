from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException, TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import datetime
import json
import os

def getMatches(date):
	options = webdriver.ChromeOptions()
	options.add_argument('--headless')
	options.add_argument('--window-size=1920,1080')
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	options.add_argument('log-level=3')
	driver = webdriver.Chrome(service=ChromeService(), options=options)

	url = "https://eurosport.tvn24.pl/watch/schedule.shtml"
	driver.get(url)

	wait = WebDriverWait(driver, 10)

	cookies = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
	cookies.click()

	date_diff = datetime.date.fromisoformat(date) - datetime.date.today()

	if date_diff.days == 1:
		day = driver.find_element(By.XPATH, "//div[@data-testid='day-after']")
	else:
		day = driver.find_element(By.XPATH, "//div[@data-testid='day-after']/../following-sibling::div[" + str(date_diff.days - 1) + "]")
	day.click()

	dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='atom-dropdown-filter-button']")))
	dropdown.click()

	only_online = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@data-testid='atom-dropdown-filter-option-1']")))
	only_online.click()

	wait.until(EC.visibility_of_element_located((By.XPATH, "//a[@data-testid='link-organism-schedule-card']")))
	elements = driver.find_elements(By.XPATH, "//a[@data-testid='link-organism-schedule-card']")

	games = []
	sports = []
	leagues = []
	matches = []

	for event in elements:
		text = event.text.split('\n')
		sport = text[0].title()

		if '-' not in text[1]:
			league = text[1].split('|')[0].strip().title()
			event_name = text[1].split('|')[-1].strip().title()
		else:
			if '.' not in text[2]:
				league = text[2].split('|')[-1].strip().title()
			else:
				league = text[2].split('|')[-2].strip().title()
			event_name = text[1].title()

		league += ' ' + sport
		time = text[-3].split('-')[0]
		link = event.get_attribute("href").split('?')[0]

		if league not in leagues:
			leagues.append(league)

		matches.append({
			'event': event_name,
			'time': time,
			'sport': sport,
			'league': league,
			'link': link
			})

	games = []

	for event in leagues:
		league = {
			'name': event,
			'matches': []
			}

		for match in matches:
			if match["league"] == event:
				league["matches"].append({
					'home': '',
					'away': '',
					'event': match["event"],
					'time': match["time"],
					'link': match["link"]
					})
		games.append(league)

	return games

if __name__ == '__main__':
	date = input("Podaj datę (YYYY-MM-DD):")
	filename = 'scraped/'+ date + '_MAX.json'
	os.makedirs(os.path.dirname(filename), exist_ok=True)
	with open(filename, 'w', encoding='utf-8') as f:
		matches = getMatches(date)
		json.dump(matches, f, ensure_ascii=False, indent=4)
	print("Wyeksportuj wygenerowany plik do bazy danych")
	input()
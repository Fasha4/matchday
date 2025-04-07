from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException, TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import json
import os

def getMatches(date):
	options = webdriver.ChromeOptions()
	options.add_argument('--headless')
	options.add_argument('--window-size=1920,1080')
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	options.add_argument('log-level=3')
	driver = webdriver.Chrome(service=ChromeService(), options=options)

	url = "https://onefootball.com/en/matches?date=" + date + "&only_watchable=true"
	driver.get(url)

	driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
	sleep(3)

	elements = driver.find_elements(By.CSS_SELECTOR, ".xpaLayoutContainerFullWidth--matchCardsList")

	games = []

	for country in elements:
		matches = country.find_elements(By.CSS_SELECTOR, ".MatchCard_matchCard__iOv4G")
		leagues = country.find_element(By.CSS_SELECTOR, ".screen-reader-only").text

		league = {
		'name': leagues,
		'matches': []
		}

		for match in matches:
			home = match.find_elements(By.CSS_SELECTOR, '.SimpleMatchCardTeam_simpleMatchCardTeam__name__7Ud8D')[0].text
			away = match.find_elements(By.CSS_SELECTOR, '.SimpleMatchCardTeam_simpleMatchCardTeam__name__7Ud8D')[1].text
			try:
				time = match.find_element(By.CSS_SELECTOR, '.SimpleMatchCard_simpleMatchCard__infoMessage___NJqW').text
			except:
				time = 'brak'
			link = match.get_attribute("href")
			league["matches"].append({
				'home': home,
				'away': away,
				'time': time,
				'link': link
				})

		games.append(league)

	return games

if __name__ == '__main__':
	date = input("Podaj datę (YYYY-MM-DD):")
	filename = 'scraped/'+ date + '_OneFootball.json'
	os.makedirs(os.path.dirname(filename), exist_ok=True)
	with open(filename, 'w', encoding='utf-8') as f:
		matches = getMatches(date)
		json.dump(matches, f, ensure_ascii=False, indent=4)
	print("Wyeksportuj wygenerowany plik do bazy danych")
	input()
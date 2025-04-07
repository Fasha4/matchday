from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import datetime
from time import sleep
import json
import os

def getMatches(custom_date):
	options = webdriver.ChromeOptions()
	options.add_argument('--headless')
	options.add_argument('--window-size=1920,1080')
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	options.add_argument('log-level=3')
	options.add_argument('--disable-search-engine-choice-screen')
	driver = webdriver.Chrome(service=ChromeService(), options=options)

	url = "https://polsatboxgo.pl/live"
	driver.get(url)

	wait = WebDriverWait(driver, 10)

	cookies = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler")))
	cookies.click()

	days = driver.find_elements(By.CSS_SELECTOR, ".sc-t2thp5-0.bnoQYD")
	for day in days:
		events = day.find_elements(By.CSS_SELECTOR, ".sc-1vdpbg2-0.hUqdCF")
		try:
			date = day.find_element(By.CSS_SELECTOR, ".sc-1nb07ih-1.fKFnFV")
			date = datetime.datetime.strptime(date.text + str(datetime.date.today().year), '%d.%m%Y').date()
		except:
			date = day.find_element(By.CSS_SELECTOR, ".sc-orrg5d-0.LUuFy")

			if date.text == "Dzisiaj":
				date = datetime.date.today()
			elif date.text == "Jutro":
				date = datetime.date.today() + datetime.timedelta(days=1)

		if date < datetime.date.fromisoformat(custom_date):
			continue
		elif date > datetime.date.fromisoformat(custom_date):
			break

		matches = []
		leagues = []

		for match in events:
			time, league = match.find_element(By.CSS_SELECTOR, '.sc-orrg5d-0.ezqpDO').text.split(' • ')
			time = (datetime.datetime.strptime(time, '%H:%M') + datetime.timedelta(minutes=10)).strftime('%H:%M')
			try:
				home, away = match.find_element(By.CSS_SELECTOR, ".sc-orrg5d-0.kcWJAW").text.split(' - ')
			except:
				continue

			if league not in leagues:
				leagues.append(league)

			matches.append({
				'home': home,
				'away': away,
				'time': time,
				'league': league
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
					'home': match["home"],
					'away': match["away"],
					'time': match["time"]
					})
		games.append(league)

	return games

if __name__ == '__main__':

	date = input("Podaj datę (YYYY-MM-DD):")
	filename = 'scraped/'+ date + '_PolsatBoxGo.json'
	os.makedirs(os.path.dirname(filename), exist_ok=True)
	with open(filename, 'w', encoding='utf-8') as f:
		matches = getMatches(date)
		json.dump(matches, f, ensure_ascii=False, indent=4)
	print("Wyeksportuj wygenerowany plik do bazy danych")
	input()
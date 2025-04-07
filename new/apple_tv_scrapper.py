from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import datetime
import pytz
from time import sleep
import json
import os

tzWarsaw = pytz.timezone('Europe/Warsaw')

def getMatches(custom_date):
	options = webdriver.ChromeOptions()
	options.add_argument('--headless')
	options.add_argument('--window-size=1920,1080')
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	options.add_argument('log-level=3')
	options.add_argument('--disable-search-engine-choice-screen')
	driver = webdriver.Chrome(service=ChromeService(), options=options)

	url = "https://tv.apple.com/pl/channel/tvs.sbd.7000"
	driver.get(url)

	wait = WebDriverWait(driver, 10)

	#MLS
	try:
		wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[text()='Live']")))
		MLS = 'Live'
	except:
		wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[text()='Schedule']")))
		MLS = 'Schedule'
	finally:
		driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
		driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)

	#MLS NEXT Pro
	try:
		wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[text()='Live: MLS NEXT Pro']")))
		nextPro = 'Live: MLS NEXT Pro'
	except:
		try:
			wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[text()='Live: MLS NEXT Pro Playoffs']")))
			nextPro = 'Live: MLS NEXT Pro Playoffs'
		except:
			pass


	shelfs = driver.find_elements(By.CSS_SELECTOR, ".shelf-grid")
	count = 0
	matchesLine, freeLine, MLSNEXTPROLine = 0, 0, 0
	for shelf in shelfs:
		if MLS == shelf.text.split()[0]:
			matchesLine = count
		elif "Free Matches" in shelf.text:
			freeLine = count
		elif nextPro in shelf.text:
			MLSNEXTPROLine = count
		count += 1

	while True:
		try:
			nextBtn = driver.find_elements(By.CSS_SELECTOR, ".shelf-grid-nav__arrow.shelf-grid-nav__arrow--next")
			if nextBtn[matchesLine].is_enabled():
				nextBtn[matchesLine].click()
			else:
				break
		except:
			break

	while True:
		try:
			nextBtn = driver.find_elements(By.CSS_SELECTOR, ".shelf-grid-nav__arrow.shelf-grid-nav__arrow--next")
			if nextBtn[freeLine].is_enabled():
				nextBtn[freeLine].click()
			else:
				break
		except:
			break

	while True:
		try:
			nextBtn = driver.find_elements(By.CSS_SELECTOR, ".shelf-grid-nav__arrow.shelf-grid-nav__arrow--next")
			if nextBtn[MLSNEXTPROLine].is_enabled():
				nextBtn[MLSNEXTPROLine].click()
			else:
				break
		except:
			break

	events = shelfs[matchesLine].find_elements(By.CSS_SELECTOR, ".shelf-grid__list-item")
	# events = driver.find_element(By.CSS_SELECTOR, ".infinite-grid__body").find_elements(By.TAG_NAME, "div")
	matches = []
	leagues = []

	# count = 0
	for match in events:
		# count += 1
		# if count%2==0:
		# 	continue
		try:
			home, away = match.find_element(By.CSS_SELECTOR, '.typ-subhead.text-truncate').text.split(' vs. ')
			league = match.find_element(By.CSS_SELECTOR, '.typ-footnote.clr-secondary-text.text-truncate').text
			link = match.find_element(By.TAG_NAME, "a").get_attribute("href")
			timedate = match.find_element(By.TAG_NAME, 'time').get_attribute("datetime")
			timedate_str = pytz.utc.localize(datetime.datetime.strptime(timedate, '%Y-%m-%dT%H:%M:00.000Z')).astimezone(tzWarsaw)
			time = timedate_str.strftime('%H:%M')

			if timedate_str < tzWarsaw.localize(datetime.datetime.fromisoformat(custom_date)):
				continue
			elif timedate_str >= tzWarsaw.localize(datetime.datetime.fromisoformat(custom_date)) + datetime.timedelta(days=1):
				break
		except:
			continue

		if league not in leagues:
			leagues.append(league)

		matches.append({
			'home': home,
			'away': away,
			'time': time,
			'league': league,
			'link': link,
			'isFree': False
			})

	if freeLine:
		freeEvents = shelfs[freeLine].find_elements(By.CSS_SELECTOR, ".shelf-grid__list-item")
		for freeMatch in freeEvents:
			try:
				timedate = freeMatch.find_element(By.TAG_NAME, 'time').get_attribute("datetime")
			except:
				continue
			home, away = freeMatch.find_element(By.CSS_SELECTOR, '.typ-subhead.text-truncate').text.split(' vs. ')
			league = freeMatch.find_element(By.CSS_SELECTOR, '.typ-footnote.clr-secondary-text.text-truncate').text
			link = freeMatch.find_element(By.TAG_NAME, "a").get_attribute("href")
			timedate_str = pytz.utc.localize(datetime.datetime.strptime(timedate, '%Y-%m-%dT%H:%M:00.000Z')).astimezone(tzWarsaw)
			time = timedate_str.strftime('%H:%M')

			if timedate_str < tzWarsaw.localize(datetime.datetime.fromisoformat(custom_date)) :
				continue
			elif timedate_str >= tzWarsaw.localize(datetime.datetime.fromisoformat(custom_date)) + datetime.timedelta(days=1):
				break

			freeGame = {
			'home': home,
			'away': away,
			'time': time,
			'league': league,
			'link': link,
			'isFree': False
			}

			if freeGame in matches:
				matches[matches.index(freeGame)]['isFree'] = True

	if MLSNEXTPROLine:
		nextProEvents = shelfs[MLSNEXTPROLine].find_elements(By.CSS_SELECTOR, ".shelf-grid__list-item")
		for match in nextProEvents:
			home, away = match.find_element(By.CSS_SELECTOR, '.typ-subhead.text-truncate').text.split(' vs. ')
			league = match.find_element(By.CSS_SELECTOR, '.typ-footnote.clr-secondary-text.text-truncate').text
			link = match.find_element(By.TAG_NAME, "a").get_attribute("href")
			timedate = match.find_element(By.TAG_NAME, 'time').get_attribute("datetime")
			timedate_str = pytz.utc.localize(datetime.datetime.strptime(timedate, '%Y-%m-%dT%H:%M:00.000Z')).astimezone(tzWarsaw)
			time = timedate_str.strftime('%H:%M')

			if timedate_str < tzWarsaw.localize(datetime.datetime.fromisoformat(custom_date)):
				continue
			elif timedate_str >= tzWarsaw.localize(datetime.datetime.fromisoformat(custom_date)) + datetime.timedelta(days=1):
				break

			if league not in leagues:
				leagues.append(league)

			matches.append({
				'home': "NEXT PRO " + home,
				'away': "NEXT PRO " + away,
				'time': time,
				'league': league,
				'link': link,
				'isFree': False
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
					'time': match["time"],
					'link': match["link"],
					'isFree': match["isFree"]
					})
		games.append(league)

	return games

if __name__ == '__main__':
	date = input("Podaj datę (YYYY-MM-DD):")
	filename = 'scraped/'+ date + '_AppleTV.json'
	os.makedirs(os.path.dirname(filename), exist_ok=True)
	with open(filename, 'w', encoding='utf-8') as f:
		matches = getMatches(date)
		json.dump(matches, f, ensure_ascii=False, indent=4)
	print("Wyeksportuj wygenerowany plik do bazy danych")
	input()
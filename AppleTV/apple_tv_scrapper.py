from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import datetime
import pytz
import json
import pyperclip
from time import sleep

tzWarsaw = pytz.timezone('Europe/Warsaw')

def getMatches(custom_date):
	options = webdriver.ChromeOptions()
	options.add_argument('--headless')
	options.add_argument('--window-size=1920,1080')
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	options.add_argument('log-level=3')
	options.add_argument('--disable-search-engine-choice-screen')
	driver = webdriver.Chrome(service=ChromeService(), options=options)

	# url = "https://tv.apple.com/pl/channel/tvs.sbd.7000"
	url = "https://tv.apple.com/pl/collection/live/edt.col.6754a13a-c8e1-4a44-b2ea-0f257d32b815?ctx_cvs=edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47&ctx_shelf=edt.shelf.66c8ce4b-897e-48e9-b42c-9b1b9ce6caea&ctx_brand=tvs.sbd.7000"
	driver.get(url)

	wait = WebDriverWait(driver, 10)

	driver.find_element(By.TAG_NAME, 'body').click()
	driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
	sleep(1)
	driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

	# sleep(1)
	# driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)
	# sleep(3)
	# driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
	# sleep(1)
	# driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)

	# #MLS
	# try:
	# 	wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[text()='Live']")))
	# 	MLS = 'Live'
	# except:
	# 	wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[text()='Rivalry Week: Live']"))) #Schedule #Live Matches <- change event line #Rivalry Week: Live
	# 	MLS = 'Rivalry Week: Live'
	# finally:
	# 	driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
	# 	driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)

	# #MLS NEXT Pro
	# try:
	# 	wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[text()='Live: MLS NEXT Pro']")))
	# 	nextPro = 'Live: MLS NEXT Pro'
	# except:
	# 	try:
	# 		wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[text()='Live: MLS NEXT Pro Playoffs']")))
	# 		nextPro = 'Live: MLS NEXT Pro Playoffs'
	# 	except:
	# 		pass


	# shelfs = driver.find_elements(By.CSS_SELECTOR, ".shelf-grid")
	# count = 0
	# matchesLine, freeLine, MLSNEXTPROLine = 0, 0, 0
	# for shelf in shelfs:
	# 	if MLS == shelf.text.split()[0]:
	# 		matchesLine = count
	# 	elif "Free Matches" in shelf.text:
	# 		freeLine = count
	# 	elif nextPro in shelf.text:
	# 		MLSNEXTPROLine = count
	# 	count += 1

	# while True:
	# 	try:
	# 		nextBtn = driver.find_elements(By.CSS_SELECTOR, ".shelf-grid-nav__arrow.shelf-grid-nav__arrow--next")
	# 		if nextBtn[matchesLine].is_enabled():
	# 			nextBtn[matchesLine].click()
	# 		else:
	# 			break
	# 	except:
	# 		break

	# while True:
	# 	try:
	# 		nextBtn = driver.find_elements(By.CSS_SELECTOR, ".shelf-grid-nav__arrow.shelf-grid-nav__arrow--next")
	# 		if nextBtn[freeLine].is_enabled():
	# 			nextBtn[freeLine].click()
	# 		else:
	# 			break
	# 	except:
	# 		break

	# while True:
	# 	try:
	# 		nextBtn = driver.find_elements(By.CSS_SELECTOR, ".shelf-grid-nav__arrow.shelf-grid-nav__arrow--next")
	# 		if nextBtn[MLSNEXTPROLine].is_enabled():
	# 			nextBtn[MLSNEXTPROLine].click()
	# 		else:
	# 			break
	# 	except:
	# 		break

	# events = shelfs[matchesLine].find_elements(By.CSS_SELECTOR, ".shelf-grid__list-item")
	# events = driver.find_element(By.CSS_SELECTOR, ".infinite-grid__body").find_elements(By.TAG_NAME, "div")
	sleep(3)
	elements = driver.find_elements(By.XPATH, "//li[@data-testid='grid-item']")
	matches = []
	leagues = []

	for match in elements:

		if ' · ' in match.text:
			continue

		home, away = match.find_element(By.XPATH, ".//p[@data-testid='title']").text.split(' vs. ')
		league = match.find_element(By.XPATH, ".//span[@data-testid='metadata-list']").text

		# home, away = match.find_element(By.CSS_SELECTOR, '.typ-subhead.text-truncate').text.split(' vs. ')
		# league = match.find_element(By.CSS_SELECTOR, '.typ-footnote.clr-secondary-text.text-truncate').text

		link = match.find_element(By.TAG_NAME, "a").get_attribute("href")
		timedate = match.find_element(By.TAG_NAME, 'time').get_attribute("datetime")
		timedate_str = pytz.utc.localize(datetime.datetime.strptime(timedate, '%Y-%m-%dT%H:%M:00.000Z')).astimezone(tzWarsaw)
		time = timedate_str.strftime('%H:%M')

		day_offset = datetime.timedelta(hours=6)

		if timedate_str < tzWarsaw.localize(datetime.datetime.fromisoformat(custom_date)) + day_offset:
			continue
		elif timedate_str >= tzWarsaw.localize(datetime.datetime.fromisoformat(custom_date)) + day_offset + datetime.timedelta(days=1):
			break

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

	# MLS NEXT PRO
	url = "https://tv.apple.com/pl/collection/live-mls-next-pro/edt.col.66e101d5-444e-4090-8828-fc08c9c1ac9d?ctx_cvs=edt.cvs.63b51506-dbce-42de-bff0-4a0b7a757f47&ctx_shelf=edt.shelf.64344473-a184-44f4-9d4d-c2fd7076e83f&ctx_brand=tvs.sbd.7000"
	driver.get(url)

	sleep(3)
	driver.find_element(By.TAG_NAME, 'body').click()
	driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
	sleep(1)
	driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
	elements = driver.find_elements(By.XPATH, "//li[@data-testid='grid-item']")

	for match in elements:

		if ' · ' in match.text:
			continue

		home, away = match.find_element(By.XPATH, ".//p[@data-testid='title']").text.split(' vs. ')
		league = match.find_element(By.XPATH, ".//span[@data-testid='metadata-list']").text
		link = match.find_element(By.TAG_NAME, "a").get_attribute("href")
		timedate = match.find_element(By.TAG_NAME, 'time').get_attribute("datetime")
		timedate_str = pytz.utc.localize(datetime.datetime.strptime(timedate, '%Y-%m-%dT%H:%M:00.000Z')).astimezone(tzWarsaw)
		time = timedate_str.strftime('%H:%M')

		day_offset = datetime.timedelta(hours=6)

		if timedate_str < tzWarsaw.localize(datetime.datetime.fromisoformat(custom_date)) + day_offset:
			continue
		elif timedate_str >= tzWarsaw.localize(datetime.datetime.fromisoformat(custom_date)) + day_offset + datetime.timedelta(days=1):
			break

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

	# if freeLine:
	# 	freeEvents = shelfs[freeLine].find_elements(By.CSS_SELECTOR, ".shelf-grid__list-item")
	# 	for freeMatch in freeEvents:
	# 		try:
	# 			timedate = freeMatch.find_element(By.TAG_NAME, 'time').get_attribute("datetime")
	# 		except:
	# 			continue
	# 		home, away = freeMatch.find_element(By.CSS_SELECTOR, '.typ-subhead.text-truncate').text.split(' vs. ')
	# 		league = freeMatch.find_element(By.CSS_SELECTOR, '.typ-footnote.clr-secondary-text.text-truncate').text
	# 		link = freeMatch.find_element(By.TAG_NAME, "a").get_attribute("href")
	# 		timedate_str = pytz.utc.localize(datetime.datetime.strptime(timedate, '%Y-%m-%dT%H:%M:00.000Z')).astimezone(tzWarsaw)
	# 		time = timedate_str.strftime('%H:%M')

	# 		day_offset = datetime.timedelta(hours=6)

	# 		if timedate_str < tzWarsaw.localize(datetime.datetime.fromisoformat(custom_date)) + day_offset:
	# 			continue
	# 		elif timedate_str >= tzWarsaw.localize(datetime.datetime.fromisoformat(custom_date)) + day_offset + datetime.timedelta(days=1):
	# 			break

	# 		freeGame = {
	# 		'home': home,
	# 		'away': away,
	# 		'time': time,
	# 		'league': league,
	# 		'link': link,
	# 		'isFree': False
	# 		}

	# 		if freeGame in matches:
	# 			matches[matches.index(freeGame)]['isFree'] = True

	# if MLSNEXTPROLine:
	# 	nextProEvents = shelfs[MLSNEXTPROLine].find_elements(By.CSS_SELECTOR, ".shelf-grid__list-item")
	# 	for match in nextProEvents:
	# 		home, away = match.find_element(By.CSS_SELECTOR, '.typ-subhead.text-truncate').text.split(' vs. ')
	# 		league = match.find_element(By.CSS_SELECTOR, '.typ-footnote.clr-secondary-text.text-truncate').text
	# 		link = match.find_element(By.TAG_NAME, "a").get_attribute("href")
	# 		timedate = match.find_element(By.TAG_NAME, 'time').get_attribute("datetime")
	# 		timedate_str = pytz.utc.localize(datetime.datetime.strptime(timedate, '%Y-%m-%dT%H:%M:00.000Z')).astimezone(tzWarsaw)
	# 		time = timedate_str.strftime('%H:%M')

	# 		day_offset = datetime.timedelta(hours=6)

	# 		if timedate_str < tzWarsaw.localize(datetime.datetime.fromisoformat(custom_date)) + day_offset:
	# 			continue
	# 		elif timedate_str >= tzWarsaw.localize(datetime.datetime.fromisoformat(custom_date)) + day_offset + datetime.timedelta(days=1):
	# 			break

	# 		if league not in leagues:
	# 			leagues.append(league)

	# 		matches.append({
	# 			'home': "NEXT PRO " + home,
	# 			'away': "NEXT PRO " + away,
	# 			'time': time,
	# 			'league': league,
	# 			'link': link,
	# 			'isFree': False
	# 			})

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

def show(matches, date):

	output = ''
	f = open('config.json', 'r', encoding='utf-8')
	config = json.load(f)
	f.close()

	sort = [x["name_apple"] for x in config["leagues"]]

	for league in matches:
		if league['name'] not in sort:
			print("Dodaj", league['name'], "do configa")
	matches = list(filter(lambda i: i['name'] in sort, matches))

	matches = sorted(matches, key=lambda x: sort.index(x["name"]))
	for league in matches:
		new_league = next((sub for sub in config["leagues"] if sub["name_apple"] == league["name"]), None)

		if new_league["show"]:
			output += r'<img class="aligncenter wp-image-' + str(new_league["wp_img"]) + r'" src="' + new_league["img"] + r'" alt="" width="' + str(new_league["img_w"]) + r'" height="' + str(new_league["img_h"]) + r'" />' + '\n'
			output += r'<h2 style="text-align: center;"><span style="font-size: 18pt;"><strong>' + new_league["name_matchday"].upper() + r'</strong></span></h2>' + '\n'
			addComm = False
			freeNote = False
			for match in league["matches"]:
				if match["home"] in config["translate"]:
					home = config["translate"][match["home"]]
				else:
					home = match["home"]
				if match["away"] in config["translate"]:
					away = config["translate"][match["away"]]
				else:
					away = match["away"]
				output += match["time"]
				if not addComm:
					addComm, dayInfo = isNextDay(match["time"], date)
				if addComm:
					output += r'*'
				output += r' - <strong>' + home.upper() + r' - ' +  away.upper() + r'</strong>' + '\n'
				output += r'<span style="font-size: 10pt;"><img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f4fa.svg" alt="📺" /> '
				output += r'<a href="' + match['link'] + r'" target="_blank" rel="noopener">AppleTV</a>'
				if match['isFree']:
					output += r'\*\*'
					freeNote = True
				output += r' <img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f399.svg" alt="🎙" width="16" height="16" /> ' + new_league["lang"] + r'</span>' + '\n'
				output += '\n'
			if addComm:
				output += r'<span style="font-size: 10pt;"><em>*W nocy z ' + dayInfo + r'</em></span>' + '\n'
			if freeNote:
				output += r'<span style="font-size: 10pt;"><em>\*\*Transmisja darmowa</em></span>' + '\n'
			if new_league["comm"]:
				output += r'<span style="font-size: 10pt;"><em>' + new_league["comm"] + r'</em></span>' + '\n'
				output += '\n'
			output += r'<hr />' + '\n'
	pyperclip.copy(output)

def isNextDay(time, date):
	current = datetime.datetime.strptime(time, '%H:%M')
	todayDays = ["poniedziałku", "wtorku", "środy", "czwartku", "piątku", "soboty", "niedzieli"]
	tomorrowDays = ["poniedziałek", "wtorek", "środę", "czwartek", "piątek", "sobotę", "niedzielę"]
	dayInfo = ''
	if current.time() >= datetime.time(hour=0) and current.time() < datetime.time(hour=6):
		date = datetime.datetime.fromisoformat(date)
		today = date.weekday()
		tomorrow = (date + datetime.timedelta(days=1)).weekday()
		dayInfo = todayDays[today] + " na " + tomorrowDays[tomorrow]
		return True, dayInfo
	else:
		return False, dayInfo

if __name__ == '__main__':
	date = input("Podaj datę (YYYY-MM-DD):")
	matches = getMatches(date)
	show(matches, date)
	print("Rozpiska została skopiowana do schowka")
	input()

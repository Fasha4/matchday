from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException, TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta, time
from time import sleep
import json
import pyperclip


def getMatches(custom_date):
	options = webdriver.ChromeOptions()
	options.add_argument('--headless')
	options.add_argument('--window-size=1920,1080')
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	options.add_argument('log-level=3')
	global driver
	driver = webdriver.Chrome(service=ChromeService(), options=options)

	url = "https://onefootball.com/en/matches?date=" + custom_date + "&only_watchable=true"
	goToNewSite(url)

	elements = driver.find_elements(By.CSS_SELECTOR, ".xpaLayoutContainerFullWidth--matchCardsList")

	matches = []
	leagues = []

	try:
		matches, leagues = getDayInfo(elements, matches, leagues, 'gt')
	except TimeoutException:
		print("[INFO] Brak meczów dnia", custom_date)

	try:
		tomorrow = datetime.fromisoformat(custom_date) + timedelta(days=1)
		url = "https://onefootball.com/en/matches?date=" + str(tomorrow.date()) + "&only_watchable=true"
		goToNewSite(url)

		elements = driver.find_elements(By.CSS_SELECTOR, ".xpaLayoutContainerFullWidth--matchCardsList")
		matches, leagues = getDayInfo(elements, matches, leagues, 'lt')
	except NoSuchElementException:
		print("[INFO] Brak meczów dnia", str(tomorrow.date()))

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
					'link': match["link"]
					})
		games.append(league)

	return games


# limit: gt -> >= 6:00, lt -> < 6:00
def getDayInfo(elements, matches, leagues, limit):
	for country in elements:
		broadcasts = country.find_elements(By.CSS_SELECTOR, ".MatchCard_matchCard__LynP5")
		league = country.find_element(By.CSS_SELECTOR, ".screen-reader-only").text

		for broadcast in broadcasts:
			home = broadcast.find_elements(By.CSS_SELECTOR, '.SimpleMatchCardTeam_simpleMatchCardTeam__name__cmh6q')[0].text
			away = broadcast.find_elements(By.CSS_SELECTOR, '.SimpleMatchCardTeam_simpleMatchCardTeam__name__cmh6q')[1].text
			try:
				time = broadcast.find_element(By.CSS_SELECTOR, '.SimpleMatchCard_simpleMatchCard__infoMessage__ypUgN').text
			except:
				time = 'brak'
			link = broadcast.get_attribute("href")

			match = {
				'home': home,
				'away': away,
				'time': time,
				'league': league,
				'link': link
				}
			if (limit == 'lt' and int(time.split(':')[0]) < 6) or (limit == 'gt' and int(time.split(':')[0]) >= 6):
				if league not in leagues:
					leagues.append(league)

				matches.append(match)

	return matches, leagues


def goToNewSite(url):
	driver.get(url)

	driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
	sleep(3)


def show(matches):

	output = ''
	f = open('config.json', 'r', encoding='utf-8')
	config = json.load(f)
	f.close()

	sort = [x["name_onefoot"] for x in config["leagues"]]

	for league in matches:
		if league['name'] not in sort:
			print("Dodaj", league['name'], "do configa")
	matches = list(filter(lambda i: i['name'] in sort, matches))


	matches = sorted(matches, key=lambda x: sort.index(x["name"]))
	for league in matches:
		new_league = next((sub for sub in config["leagues"] if sub["name_onefoot"] == league["name"]), None)

		if new_league["show"]:
			output += r'<img class="aligncenter wp-image-' + str(new_league["wp_img"]) + r'" src="' + new_league["img"] + r'" alt="" width="' + str(new_league["img_w"]) + r'" height="' + str(new_league["img_h"]) + r'" />' + '\n'
			output += r'<h2 style="text-align: center;"><span style="font-size: 18pt;"><strong>' + new_league["name_matchday"].upper() + r'</strong></span></h2>' + '\n'
			addComm = False
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
				output += r'<a href="' + match['link'] + r'" target="_blank" rel="noopener">OneFootball</a> '
				output += r'<img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f399.svg" alt="🎙" width="16" height="16" /> ' + new_league["lang"] + r'</span>' + '\n'
				output += '\n'
			if addComm:
				output += r'<span style="font-size: 10pt;"><em>*W nocy z ' + dayInfo + r'</em></span>' + '\n'
			if new_league["comm"]:
				output += r'<span style="font-size: 10pt;"><em>' + new_league["comm"] + r'</em></span>' + '\n'
				output += '\n'
			output += r'<hr />' + '\n'
	pyperclip.copy(output)


def isNextDay(match_time, date):
	current = datetime.strptime(match_time, '%H:%M')
	todayDays = ["poniedziałku", "wtorku", "środy", "czwartku", "piątku", "soboty", "niedzieli"]
	tomorrowDays = ["poniedziałek", "wtorek", "środę", "czwartek", "piątek", "sobotę", "niedzielę"]
	dayInfo = ''
	if current.time() >= time(hour=0) and current.time() < time(hour=6):
		date = datetime.fromisoformat(date)
		today = date.weekday()
		tomorrow = (date + timedelta(days=1)).weekday()
		dayInfo = todayDays[today] + " na " + tomorrowDays[tomorrow]
		return True, dayInfo
	else:
		return False, dayInfo


if __name__ == '__main__':
	date = input("Podaj datę (YYYY-MM-DD):")
	matches = getMatches(date)
	show(matches)
	print("Rozpiska została skopiowana do schowka")
	input()
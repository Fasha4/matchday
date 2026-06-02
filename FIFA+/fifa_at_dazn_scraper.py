from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, timedelta, time
import json
import pyperclip

def getMatches(custom_date):
	options = webdriver.ChromeOptions()
	options.add_argument('--headless')
	options.add_argument('--window-size=1920,1080')
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	options.add_argument('log-level=3')
	options.add_argument('--disable-search-engine-choice-screen')
	global driver
	driver = webdriver.Chrome(service=ChromeService(), options=options)

	url = "https://www.dazn.com/en-PL/competition/Competition:50kvbmxi5r9amj2e39hznggqj?tab=schedule"
	driver.get(url)

	global wait
	wait = WebDriverWait(driver, 10)

	cookies = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler")))
	cookies.click()

	matches = []
	leagues = []

	try:
		day = wait.until(EC.visibility_of_element_located((By.XPATH, './/div[@title="' + custom_date + '"]')))
		day.click()
		matches, leagues = getDayInfo(matches, leagues, 'gt')
	except TimeoutException:
		print("[INFO] Brak meczów dnia", custom_date)

	try:
		tomorrow = datetime.fromisoformat(custom_date) + timedelta(days=1)
		next_day = driver.find_element(By.XPATH, './/div[@title="' + str(tomorrow.date()) + '"]')
		next_day.click()
		matches, leagues = getDayInfo(matches, leagues, 'lt')
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
					})
		games.append(league)

	return games


# limit: gt -> >= 6:00, lt -> < 6:00
def getDayInfo(matches, leagues, limit):
	wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'article')))
	broadcasts = driver.find_elements(By.TAG_NAME, 'article')

	for broadcast in broadcasts:
		time = broadcast.find_element(By.CSS_SELECTOR, '.MatchCard__status-text___2PuYM').text
		home = broadcast.find_element(By.CSS_SELECTOR, '.MatchCard__team-name___3_9jo.MatchCard__team-one-name___2vN4J').text
		away = broadcast.find_element(By.CSS_SELECTOR, '.MatchCard__team-name___3_9jo.MatchCard__team-two-name___19p8a').text
		league = broadcast.find_element(By.CSS_SELECTOR, '.MatchCard__competition-label___3wq5P').text

		match = {
			'home': home,
			'away': away,
			'time': time,
			'league': league,
			}
		if match in matches:
			continue
		else:
			if (limit == 'lt' and int(time.split(':')[0]) < 6) or (limit == 'gt' and int(time.split(':')[0]) >= 6):
				if league not in leagues:
					leagues.append(league)

				matches.append(match)

	return matches, leagues


def show(matches, date):
	output = ''
	f = open('config.json', 'r', encoding='utf-8')
	config = json.load(f)
	f.close()

	sort = [x["name_fifa"] for x in config["leagues"]]

	for league in matches:
		if league['name'] not in sort:
			print("Dodaj", league['name'], "do configa")
	matches = list(filter(lambda i: i['name'] in sort, matches))

	matches = sorted(matches, key=lambda x: sort.index(x["name"]))
	for league in matches:
		new_league = next((sub for sub in config["leagues"] if sub["name_fifa"] == league["name"]), None)

		if new_league["show"]:
			output += r'<img class="aligncenter wp-image-' + str(new_league["wp_img"]) + r'" src="' + new_league["img"] + r'" alt="" width="' + str(new_league["img_w"]) + r'" height="' + str(new_league["img_h"]) + r'" />' + '\n'
			output += r'<h2 style="text-align: center;"><span style="font-size: 18pt;"><strong>' + new_league["name_matchday"].upper() + r'</strong></span></h2>' + '\n'
			addComm = False
			for match in league["matches"]:
				home = match["home"]
				away = match["away"]
				output += match["time"]
				if not addComm:
					addComm, dayInfo = isNextDay(match["time"], date)
				if addComm:
					output += r'*'
				output += r' - <strong>' + home.upper() + r' - ' +  away.upper() + r'</strong>' + '\n'
				output += r'<span style="font-size: 10pt;"><img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f4fa.svg" alt="📺" /> '
				output += r'<a href="https://www.dazn.com/en-PL/competition/Competition:50kvbmxi5r9amj2e39hznggqj" target="_blank" rel="noopener">FIFA+ na DAZN</a> '
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
	show(matches, date)
	print("Rozpiska została skopiowana do schowka")
	input()
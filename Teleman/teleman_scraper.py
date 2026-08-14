from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException, TimeoutException, WebDriverException
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
	driver = webdriver.Chrome(service=ChromeService(), options=options)

	url = "https://www.teleman.pl/sport/pilka-nozna?live=1&stations=all"
	driver.get(url)

	wait = WebDriverWait(driver, 10)

	today = datetime.fromisoformat(custom_date)

	cookies = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".fc-button.fc-cta-consent.fc-primary-button")))
	cookies.click()

	months_translate = {'stycznia': '1', 'lutego': '2', 'marca': '3', 'kwietnia': '4', 'maja': '5', 'czerwca': '6',
		'lipca': '7', 'sierpnia': '8', 'września': '9', 'października': '10', 'listopada': '11', 'grudnia': '12'}

	matches = []
	leagues = []

	while True:

		broadcasts = driver.find_elements(By.TAG_NAME, "tr")

		for broadcast in broadcasts:
			if not ' - ' in broadcast.text:
				continue

			details = broadcast.find_elements(By.TAG_NAME, "td")
			if not details:
				continue

			date = details[0].text.split(', ')[-1]
			time = details[1].text
			for x,y in months_translate.items():
				date = date.replace(x,y)

			now = datetime.now()
			if now.month == 12 and date.split()[-1] == '1':
				now += timedelta(weeks=20)
			date += ' ' + str(now.year)
			date = datetime.strptime(date + ", " + time, "%d %m %Y, %H:%M")

			if date < today + timedelta(hours=6):
				continue
			elif date >= today + timedelta(days=1, hours=6):
				break


			channel = details[2].text
			league, game = details[3].text.split(' \n')
			league = league.split('Piłka nożna: ')[-1]
			home, away = game.split(': ')[-1].split(' - ')

			if league not in leagues:
				leagues.append(league)

			match = {
				'home': home,
				'away': away,
				'time': time,
				'league': league,
				'channel': channel
				}

			matches.append(match)

		if date >= today + timedelta(days=1, hours=6):
			break

		nextBtn = wait.until(EC.element_to_be_clickable((By.XPATH, './/span[@class="next"]')))
		nextBtn.click()

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
					'channel': match["channel"]
					})
		games.append(league)

	games = reduce_channels(games)

	return games


def reduce_channels(games):

	for league in games:
		i = 0
		prev_home, prev_away, prev_time, prev_channel = '', '', '', ''
		to_delete = []
		league["matches"] = sorted(league["matches"], key=lambda d: (d["time"], d["channel"]))
		for match in league["matches"]:
			if match["home"] == prev_home and match["away"] == prev_away and match["time"] == prev_time:
				match["channel"] = prev_channel + ', ' + match["channel"]
				to_delete.append(i-1)
				prev_home, prev_away, prev_time, prev_channel = match["home"], match["away"], match["time"], match["channel"]

			prev_home, prev_away, prev_time, prev_channel = match["home"], match["away"], match["time"], match["channel"]

			i += 1
		if to_delete:
			for item in reversed(to_delete):
				league["matches"].pop(item)

	return games


def show(matches, date):

	output = ''
	f = open('config.json', 'r', encoding='utf-8')
	config = json.load(f)
	f.close()

	sort = [x["name_teleman"] for x in config["leagues"]]

	for league in matches:
		if league['name'] not in sort:
			print("Dodaj", league['name'], "do configa")
	matches = list(filter(lambda i: i['name'] in sort, matches))

	matches = sorted(matches, key=lambda x: sort.index(x["name"]))
	for league in matches:
		new_league = next((sub for sub in config["leagues"] if sub["name_teleman"] == league["name"]), None)

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
				output += match["channel"] + '\n'
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
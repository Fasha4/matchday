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

	url = "https://sport.tvp.pl/transmisje"
	driver.get(url)

	wait = WebDriverWait(driver, 10)

	cookies = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".tvp-covl__ab")))
	cookies.click()

	all_dates = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".epg-calendar__switch-toggle-button")))
	all_dates.click()

	days = driver.find_elements(By.CSS_SELECTOR, ".epg-day-set")
	months_translate = {'stycznia': '1', 'lutego': '2', 'marca': '3', 'kwietnia': '4', 'maja': '5', 'czerwca': '6',
		'lipca': '7', 'sierpnia': '8', 'września': '9', 'października': '10', 'listopada': '11', 'grudnia': '12'}

	matches = []
	leagues = []

	for day in days:
		date = day.find_element(By.CSS_SELECTOR, ".epg-day-set__date").text
		for x,y in months_translate.items():
			date = date.replace(x,y)

		today = datetime.fromisoformat(custom_date)
		tomorrow = today + timedelta(days=1)
		if datetime.strptime(date, "%d %m %Y") == today or datetime.strptime(date, "%d %m %Y") == tomorrow:
			broadcasts = day.find_elements(By.CSS_SELECTOR, '.epg-item')

			try:
				if datetime.strptime(date, "%d %m %Y") == today:
					matches, leagues = getDayInfo(broadcasts, matches, leagues, 'gt')
				elif datetime.strptime(date, "%d %m %Y") == tomorrow:
					matches, leagues = getDayInfo(broadcasts, matches, leagues, 'lt')
			except TimeoutException:
				print("[INFO] Brak meczów dnia", custom_date)

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
def getDayInfo(broadcasts, matches, leagues, limit):
	for broadcast in broadcasts:
		try:
			time = broadcast.find_element(By.CSS_SELECTOR, '.epg-item__hour').text
		except:
			# take previous time
			pass
		title = broadcast.find_element(By.CSS_SELECTOR, '.epg-item__title').text
		if ':' not in title or any(w in title for w in ['atmosfera', 'kibice', 'analityczna', 'ławka']): continue
		if "Mundial 2026" in title.split(': ', 1)[-1]:
			teams, league = title.split(': ', 1)
		else:
			league, teams = title.split(': ', 1)
		if '–' not in teams and '-' not in teams: continue
		try:
			home, away = teams.split(' – ')
		except ValueError:
			home, away = teams.split(' - ')
		link = broadcast.get_attribute("href")

		league = league
		if league not in leagues:
			leagues.append(league)

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


def show(matches, date):

	output = ''
	f = open('config.json', 'r', encoding='utf-8')
	config = json.load(f)
	f.close()

	sort = [x["name_tvp"] for x in config["leagues"]]

	for league in matches:
		if league['name'] not in sort:
			print("Dodaj", league['name'], "do configa")
	matches = list(filter(lambda i: i['name'] in sort, matches))

	matches = sorted(matches, key=lambda x: sort.index(x["name"]))
	for league in matches:
		new_league = next((sub for sub in config["leagues"] if sub["name_tvp"] == league["name"]), None)

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
				output += r'<a href="' + match['link'] + r'" target="_blank" rel="noopener">sport.tvp.pl</a> '
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
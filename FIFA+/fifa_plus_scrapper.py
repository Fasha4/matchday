from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import datetime
import json
import pyperclip
import re

def getMatches(custom_date):
	options = webdriver.ChromeOptions()
	options.add_argument('--headless')
	options.add_argument('--window-size=1920,1080')
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	options.add_argument('log-level=3')
	options.add_argument('--disable-search-engine-choice-screen')
	driver = webdriver.Chrome(service=ChromeService(), options=options)

	url = "https://www.plus.fifa.com/en/live-schedule/time?gl=pl&date=" + custom_date
	driver.get(url)

	wait = WebDriverWait(driver, 10)

	cookies = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler")))
	cookies.click()

	elements = driver.find_elements(By.CSS_SELECTOR, ".sc-iEXKAA.gzITyf")
	driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

	ad = wait.until(EC.element_to_be_clickable((By.ID, "modal-button-close")))
	ad.click()

	driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

	wait.until(EC.visibility_of_element_located((By.ID, "content-scroll-anchor")))
	container = driver.find_element(By.ID, 'content-scroll-anchor')

	#show all matches
	while True:
		driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
		new_elements = container.find_elements(By.XPATH, ".//a[starts-with(@data-id, 'match_card')]")

		if len(new_elements) == len(elements):
			break
		else:
			elements = new_elements
			[driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END) for i in range(20)]

	matches = []
	leagues = []

	for match in elements:
		try:
			home, away = match.find_element(By.XPATH, ".//span[@data-id='next-matches-rail-match-title']").text.split(' v ')
		except:
			home = match.find_element(By.XPATH, ".//span[@data-id='next-matches-rail-match-title']").text
			away = ""
		league = match.find_element(By.XPATH, ".//span[@data-id='next-matches-rail-match-title']/following-sibling::p[1]").text.split(' | ')[0]
		try:
			country = match.find_element(By.XPATH, ".//div[@data-id='next-matches-rail-match-subtitle']").text.split('\n')[-1]
		except:
			country = ""
		league = country + " " + league
		try:
			time = match.find_element(By.XPATH, ".//div[@data-id='next-matches-rail-match-time-patch']").text
		except:
			continue
		link = match.get_attribute("href")

		if time[-2:] == '15' or time[-2:] == '45':
			temp_time = datetime.datetime.strptime(time, '%H:%M') + datetime.timedelta(minutes=15)
			time = temp_time.strftime('%H:%M')
		elif time[-2:] == '05' or time[-2:] == '20' or time[-2:] == '35' or time[-2:] == '50':
			temp_time = datetime.datetime.strptime(time, '%H:%M') + datetime.timedelta(minutes=10)
			time = temp_time.strftime('%H:%M')
		elif time[-2:] == '55':
			temp_time = datetime.datetime.strptime(time, '%H:%M') + datetime.timedelta(minutes=5)
			time = temp_time.strftime('%H:%M')

		if int(time.split(':')[0]) < 6 and int(time.split(':')[0]) >= 0:
			continue

		league = re.sub(r'\s((20[0-9][0-9]/20[0-9][0-9])|(20[0-9][0-9][/-][0-9][0-9])|(20[0-9][0-9])|(2[5-9])|([3-9][0-9]))', "", league)
		league = league.strip(' - ')

		if league not in leagues:
			leagues.append(league)

		matches.append({
			'home': home,
			'away': away,
			'time': time,
			'league': league,
			'link': link
			})

	tomorrow = datetime.datetime.fromisoformat(custom_date) + datetime.timedelta(days=1)

	url = "https://www.plus.fifa.com/en/live-schedule/time?gl=pl&date=" + str(tomorrow)
	driver.get(url)

	[driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END) for i in range(20)]

	container = driver.find_element(By.ID, 'content-scroll-anchor')
	elements = container.find_elements(By.XPATH, ".//a[starts-with(@data-id, 'match_card')]")

	for match in elements:
		try:
			home, away = match.find_element(By.XPATH, ".//span[@data-id='next-matches-rail-match-title']").text.split(' v ')
		except:
			home = match.find_element(By.XPATH, ".//span[@data-id='next-matches-rail-match-title']").text
			away = ""
		league = match.find_element(By.XPATH, ".//span[@data-id='next-matches-rail-match-title']/following-sibling::p[1]").text.split(' | ')[0]
		try:
			country = match.find_element(By.XPATH, ".//div[@data-id='next-matches-rail-match-subtitle']").text.split('\n')[-1]
		except:
			country = ""
		league = country + " " + league
		time = match.find_element(By.XPATH, ".//div[@data-id='next-matches-rail-match-time-patch']").text
		link = match.get_attribute("href")

		if time[-2:] == '15' or time[-2:] == '45':
			temp_time = datetime.datetime.strptime(time, '%H:%M') + datetime.timedelta(minutes=15)
			time = temp_time.strftime('%H:%M')
		elif time[-2:] == '20' or time[-2:] == '50':
			temp_time = datetime.datetime.strptime(time, '%H:%M') + datetime.timedelta(minutes=10)
			time = temp_time.strftime('%H:%M')
		elif time[-2:] == '55':
			temp_time = datetime.datetime.strptime(time, '%H:%M') + datetime.timedelta(minutes=5)
			time = temp_time.strftime('%H:%M')

		if int(time.split(':')[0]) >= 6 or int(time.split(':')[0]) == 0:
			continue

		league = re.sub(r'\s((20[0-9][0-9]/20[0-9][0-9])|(20[0-9][0-9][/-][0-9][0-9])|(20[0-9][0-9])|(2[5-9])|([3-9][0-9]))', "", league)
		league = league.strip(' - ')

		if league not in leagues:
			leagues.append(league)

		matches.append({
			'home': home,
			'away': away,
			'time': time,
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
					'home': match["home"],
					'away': match["away"],
					'time': match["time"],
					'link': match["link"]
					})
		games.append(league)

	return games

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
				output += r'<a href="' + match['link'] + r'" target="_blank" rel="noopener">FIFA+</a> '
				output += r'<img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f399.svg" alt="🎙" width="16" height="16" /> ' + new_league["lang"] + r'</span>' + '\n'
				output += '\n'
			if addComm:
				output += r'<span style="font-size: 10pt;"><em>*W nocy z ' + dayInfo + r'</em></span>' + '\n'
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
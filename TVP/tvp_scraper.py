from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
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

		if datetime.fromisoformat(custom_date) == datetime.strptime(date, "%d %m %Y"):
			broadcasts = day.find_elements(By.CSS_SELECTOR, '.epg-item')

			for broadcast in broadcasts:
				time = broadcast.find_element(By.CSS_SELECTOR, '.epg-item__hour').text
				title = broadcast.find_element(By.CSS_SELECTOR, '.epg-item__title').text
				if ':' not in title: continue
				league, teams = title.split(':')
				if '–' not in teams: continue
				home, away = teams.strip().split(' – ')
				link = broadcast.get_attribute("href")

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
			for match in league["matches"]:
				home = match["home"]
				away = match["away"]
				output += match["time"]
				output += r' - <strong>' + home.upper() + r' - ' +  away.upper() + r'</strong>' + '\n'
				output += r'<span style="font-size: 10pt;"><img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f4fa.svg" alt="📺" /> '
				output += r'<a href="' + match['link'] + r'" target="_blank" rel="noopener">sport.tvp.pl</a> '
				output += r'<img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f399.svg" alt="🎙" width="16" height="16" /> ' + new_league["lang"] + r'</span>' + '\n'
				output += '\n'
			if new_league["comm"]:
				output += r'<span style="font-size: 10pt;"><em>' + new_league["comm"] + r'</em></span>' + '\n'
				output += '\n'
			output += r'<hr />' + '\n'
	pyperclip.copy(output)

if __name__ == '__main__':
	date = input("Podaj datę (YYYY-MM-DD):")
	matches = getMatches(date)
	show(matches, date)
	print("Rozpiska została skopiowana do schowka")
	input()
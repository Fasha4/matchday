from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import datetime
import json
import pyperclip
from time import sleep

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
			date = day.find_element(By.CSS_SELECTOR, ".sc-1nb07ih-1.llbBHD")
			date = datetime.datetime.strptime(date.text + str(datetime.date.today().year), '%d.%m%Y').date()
		except:
			date = day.find_element(By.CSS_SELECTOR, ".sc-orrg5d-0.kBMkMn")
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
			time, league = match.find_element(By.CSS_SELECTOR, '.sc-orrg5d-0.dtmHkV').text.split(' • ')
			time = (datetime.datetime.strptime(time, '%H:%M') + datetime.timedelta(minutes=10)).strftime('%H:%M')
			try:
				home, away = match.find_element(By.CSS_SELECTOR, ".sc-orrg5d-0.iEbmMX").text.split(' - ')
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

def show(matches, date):

	output = ''
	f = open('config.json', 'r', encoding='utf-8')
	config = json.load(f)
	f.close()

	sort = [x["name_polsat"] for x in config["leagues"]]

	for league in matches:
		if league['name'] not in sort:
			print("Dodaj", league['name'], "do configa")
	matches = list(filter(lambda i: i['name'] in sort, matches))

	matches = sorted(matches, key=lambda x: sort.index(x["name"]))
	for league in matches:
		new_league = next((sub for sub in config["leagues"] if sub["name_polsat"] == league["name"]), None)

		if new_league["show"]:
			output += r'<img class="aligncenter wp-image-' + str(new_league["wp_img"]) + r'" src="' + new_league["img"] + r'" alt="" width="' + str(new_league["img_w"]) + r'" height="' + str(new_league["img_h"]) + r'" />' + '\n'
			output += r'<h2 style="text-align: center;"><span style="font-size: 18pt;"><strong>' + new_league["name_matchday"].upper() + r'</strong></span></h2>' + '\n'
			for match in league["matches"]:
				output += match["time"] + r' - <strong>' + match["home"].upper() + r' - ' +  match["away"].upper() + r'</strong>' + '\n'
				output += r'<span style="font-size: 10pt;"><img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f4fa.svg" alt="📺" /> '
				output += r'Polsat Box Go'
				output += r' <img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f399.svg" alt="🎙" width="16" height="16" /> brak</span>' + '\n'
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
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
from time import sleep

def getMatches(custom_date):
	options = webdriver.ChromeOptions()
	options.add_argument('--headless')
	options.add_argument('--window-size=1920,1080')
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	options.add_argument('log-level=3')
	options.add_argument('--disable-search-engine-choice-screen')
	driver = webdriver.Chrome(service=ChromeService(), options=options)

	url = "https://pzpnplus.pl/playlist/254/DEFAULT/Ju%C5%BC%20wkr%C3%B3tce?componentId=760"
	driver.get(url)

	wait = WebDriverWait(driver, 10)

	today = datetime.fromisoformat(custom_date)

	shadow_root = wait.until(EC.presence_of_element_located((By.ID, "usercentrics-cmp-ui")))

	cookies = driver.execute_script('return arguments[0].shadowRoot', shadow_root).find_element(By.CSS_SELECTOR, ".uc-deny-button")
	cookies.click()


	try:
		moreBtn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".MediaButton.MediaButton--transparent.MediaButton--middle")))
		moreBtn.click()
		sleep(1)
	except:
		pass

	eventCards = driver.find_elements(By.CSS_SELECTOR, ".ListComponentItemFrame")

	matches = []
	leagues = []


	for i in range(len(eventCards)):
		try:
			if i != 0:
				try:
					moreBtn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".MediaButton.MediaButton--transparent.MediaButton--middle")))
					moreBtn.click()
					sleep(1)
				except:
					pass

				wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ListComponentItemFrame")))
				eventCards = driver.find_elements(By.CSS_SELECTOR, ".ListComponentItemFrame")

			driver.execute_script("arguments[0].scrollIntoView(true);", eventCards[i])
			sleep(0.3)

			eventCards[i].click()

			wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".start-date")))
			date = datetime.strptime(driver.find_element(By.CSS_SELECTOR, ".start-date").text, "%d.%m.%Y")

			if date < today:
				driver.back()
				continue
			elif date > today:
				break

			details = driver.find_element(By.XPATH, './/button[text()="Szczegóły"]')
			details.click()
			try:
				comm = driver.find_element(By.CSS_SELECTOR, ".MediaPeople__director").text.split(': ')[-1]
			except:
				comm = ''

			teams = driver.find_elements(By.CSS_SELECTOR, ".MatchTeamHeader__name")
			home, away = teams[0].text, teams[1].text
			league = driver.find_element(By.CSS_SELECTOR, ".match-league-info__name").text
			time = (datetime.strptime(driver.find_element(By.CSS_SELECTOR, ".start-time").text, "%H:%M") + timedelta(minutes=10)).strftime("%H:%M")
			link = driver.current_url

			if league not in leagues:
				leagues.append(league)

			match = {
				'home': home,
				'away': away,
				'time': time,
				'league': league,
				'comm': comm,
				'link': link
				}

			matches.append(match)

			driver.back()
		except:
			break

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
					'comm': match["comm"],
					'link': match["link"]
					})
		games.append(league)

	return games


def show(matches, date):

	output = ''
	f = open('config.json', 'r', encoding='utf-8')
	config = json.load(f)
	f.close()

	sort = [x["name_pzpn"] for x in config["leagues"]]

	for league in matches:
		if league['name'] not in sort:
			print("Dodaj", league['name'], "do configa")
	matches = list(filter(lambda i: i['name'] in sort, matches))

	matches = sorted(matches, key=lambda x: sort.index(x["name"]))
	for league in matches:
		new_league = next((sub for sub in config["leagues"] if sub["name_pzpn"] == league["name"]), None)

		if new_league["show"]:
			output += r'<img class="aligncenter wp-image-' + str(new_league["wp_img"]) + r'" src="' + new_league["img"] + r'" alt="" width="' + str(new_league["img_w"]) + r'" height="' + str(new_league["img_h"]) + r'" />' + '\n'
			output += r'<h2 style="text-align: center;"><span style="font-size: 18pt;"><strong>' + new_league["name_matchday"].upper() + r'</strong></span></h2>' + '\n'
			for match in league["matches"]:
				home = match["home"]
				away = match["away"]
				output += match["time"]
				output += r' - <strong>' + home.upper() + r' - ' +  away.upper() + r'</strong>' + '\n'
				output += r'<span style="font-size: 10pt;"><img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f4fa.svg" alt="📺" /> '
				output += r'<a href="' + match['link'] + r'" target="_blank" rel="noopener">PZPN+</a> '
				output += r'<img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f399.svg" alt="🎙" width="16" height="16" /> '
				output += match["comm"] + new_league["lang"] + r'</span>' + '\n'
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
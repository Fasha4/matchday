from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException, TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import json
import pyperclip

def getMatches(date):
	options = webdriver.ChromeOptions()
	options.add_argument('--headless')
	options.add_argument('--window-size=1920,1080')
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	options.add_argument('log-level=3')
	driver = webdriver.Chrome(service=ChromeService(), options=options)

	url = "https://onefootball.com/en/matches?date=" + date + "&only_watchable=true"
	driver.get(url)

	driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
	sleep(3)

	elements = driver.find_elements(By.CSS_SELECTOR, ".xpaLayoutContainerFullWidth--matchCardsList")

	games = []

	for country in elements:
		matches = country.find_elements(By.CSS_SELECTOR, ".MatchCard_matchCard__iOv4G")
		leagues = country.find_element(By.CSS_SELECTOR, ".screen-reader-only").text

		league = {
		'name': leagues,
		'matches': []
		}

		for match in matches:
			home = match.find_elements(By.CSS_SELECTOR, '.SimpleMatchCardTeam_simpleMatchCardTeam__name__7Ud8D')[0].text
			away = match.find_elements(By.CSS_SELECTOR, '.SimpleMatchCardTeam_simpleMatchCardTeam__name__7Ud8D')[1].text
			time = match.find_element(By.CSS_SELECTOR, '.SimpleMatchCard_simpleMatchCard__infoMessage___NJqW').text
			link = match.get_attribute("href")
			league["matches"].append({
				'home': home,
				'away': away,
				'time': time,
				'link': link
				})

		games.append(league)

	return games

def show(matches):

	output = ''
	f = open('config.json', 'r', encoding='utf-8')
	config = json.load(f)
	f.close()

	sort = [x["name_onefoot"] for x in config["leagues"]]
	matches = sorted(matches, key=lambda x: sort.index(x["name"]))

	for league in matches:
		new_league = next((sub for sub in config["leagues"] if sub["name_onefoot"] == league["name"]), None)

		if new_league["show"]:
			output += r'<img class="aligncenter wp-image-' + str(new_league["wp_img"]) + r'" src="' + new_league["img"] + r'" alt="" width="' + str(new_league["img_w"]) + r'" height="' + str(new_league["img_h"]) + r'" />' + '\n'
			output += r'<h2 style="text-align: center;"><span style="font-size: 18pt;"><strong>' + new_league["name_matchday"].upper() + r'</strong></span></h2>' + '\n'
			for match in league["matches"]:
				if match["home"] in config["translate"]:
					home = config["translate"][match["home"]]
				else:
					home = match["home"]
				if match["away"] in config["translate"]:
					away = config["translate"][match["away"]]
				else:
					away = match["away"]
				output += match["time"] + r' - <strong>' + home.upper() + r' - ' +  away.upper() + r'</strong>' + '\n'
				output += r'<span style="font-size: 10pt;"><img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f4fa.svg" alt="📺" /> '
				output += r'<a href="' + match['link'] + r'" target="_blank" rel="noopener">OneFootball</a> '
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
	show(matches)
	print("Rozpiska została skopiowana do schowka")
	input()
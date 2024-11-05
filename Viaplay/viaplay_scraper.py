from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException, TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import datetime
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

	url = "https://viaplay.pl/sport"
	driver.get(url)
	wait = WebDriverWait(driver, 10)

	original_window = driver.current_window_handle

	cookies = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler")))
	cookies.click()

	date_diff = datetime.date.fromisoformat(custom_date) - datetime.date.today()
	for i in range(5):
		driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

	for i in range(date_diff.days):
		driver.find_element(By.CSS_SELECTOR, ".SportScheduleNavigation_next__ul0Wp").click()

	#schedule wrapper
	section = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".SportScheduleBlockWrapper_schedule__LtLbg")))
	#matches
	elements = section.find_elements(By.CSS_SELECTOR, ".Item_sportsListItem__9PQ44")
	ActionChains(driver).scroll_by_amount(0, -10000).perform()

	matches = []
	leagues = []

	for match in elements:
		home, away, other, time, league, comment = 6*['']
		try:
			home, away = match.find_element(By.CSS_SELECTOR, ".SportMeta_title__kj1xI").text.split(' - ')
		except:
			other = match.find_element(By.CSS_SELECTOR, ".SportMeta_title__kj1xI").text

		time = match.find_element(By.CSS_SELECTOR, ".Badge_start__dU5U3").text
		league = match.find_element(By.CSS_SELECTOR, ".SportMeta_logo___uXpn").get_attribute("alt")
		link = match.find_element(By.CSS_SELECTOR, ".Item_link__zRSeq").get_attribute("href")
		if match.find_element(By.CSS_SELECTOR, ".SportMeta_secondarytitle__HHMXz").text == "Piłka ręczna":
			league += " piłka ręczna"
		if league not in leagues:
			leagues.append(league)
		ActionChains(driver).move_to_element_with_offset(match, 140, -70).perform()
		wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".Tooltip_container__sAdMQ")))
		try:
			comment = driver.find_element(By.CSS_SELECTOR, ".MetaWithIcon_text__J7PTM").text
			comment = ", ".join(comment.split(' & '))
		except:
			comment = ""
		ActionChains(driver).move_by_offset(-50, 0).perform()

		matches.append({
				'event': other,
				'home': home,
				'away': away,
				'time': time,
				'league': league,
				'link': link,
				'comment': comment
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
					'event': match["event"],
					'home': match["home"],
					'away': match["away"],
					'time': match["time"],
					'link': match["link"],
					'comment': match["comment"]
					})
		games.append(league)

	return games

def correct_time(matches, custom_date):
	options = webdriver.ChromeOptions()
	options.add_argument('--headless')
	options.add_argument('--window-size=1920,1080')
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	options.add_argument('log-level=3')
	options.add_argument('--disable-search-engine-choice-screen')
	driver = webdriver.Chrome(service=ChromeService(), options=options)

	driver.get("https://www.flashscore.pl/")

	wait = WebDriverWait(driver, 10)
	cookies = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler")))
	cookies.click()

	date_diff = datetime.date.fromisoformat(custom_date) - datetime.date.today()
	for i in range(date_diff.days):
		wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.calendar__navigation--tomorrow')))
		driver.find_element(By.CSS_SELECTOR, ".calendar__navigation--tomorrow").click()
	wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'pokaż spotkania')]")))

	expand = driver.find_elements(By.XPATH, "//*[contains(text(), 'pokaż spotkania')]")
	for button in expand:
		button.click()

	f = open('config.json', 'r', encoding='utf-8')
	config = json.load(f)
	f.close()

	matches_fs = driver.find_elements(By.CSS_SELECTOR, '.event__match.event__match--twoLine')

	correct_matches = []

	for match in matches_fs:
		try:
			home = match.find_element(By.CSS_SELECTOR, '.event__homeParticipant').text
			away = match.find_element(By.CSS_SELECTOR, '.event__awayParticipant').text
			try:
				matchtime = match.find_element(By.CSS_SELECTOR, '.event__time').text
			except:
				matchtime = "brak"
			if home in config["flashscore"]:
				home = config["flashscore"][home]
			if away in config["flashscore"]:
				away = config["flashscore"][away]
			correct_matches.append({
				'home': home,
				'away': away,
				'time': matchtime})
		except:
			pass

	for correct_match in correct_matches:
		for league in matches:
			for match in league["matches"]:
				if match["home"] == correct_match["home"] and match["away"] == correct_match["away"]:
					match["time"] = correct_match["time"]

	return matches


def show(matches):

	output = ''
	f = open('config.json', 'r', encoding='utf-8')
	config = json.load(f)
	f.close()

	sort = [x["name_viaplay"] for x in config["leagues"]]

	for league in matches:
		if league['name'] not in sort:
			print("Dodaj", league['name'], "do configa")
	matches = list(filter(lambda i: i['name'] in sort, matches))

	matches = sorted(matches, key=lambda x: sort.index(x["name"]))
	for league in matches:
		if [x['home'] for x in league['matches']] == ['']:
			continue
		new_league = next((sub for sub in config["leagues"] if sub["name_viaplay"] == league["name"]), None)

		if new_league["show"]:
			output += r'<img class="aligncenter wp-image-' + str(new_league["wp_img"]) + r'" src="' + new_league["img"] + r'" alt="" width="' + str(new_league["img_w"]) + r'" height="' + str(new_league["img_h"]) + r'" />' + '\n'
			output += r'<h2 style="text-align: center;"><span style="font-size: 18pt;"><strong>' + new_league["name_matchday"].upper() + r'</strong></span></h2>' + '\n'
			for match in league["matches"]:
				if match["event"] in config["ignore"] or "(" in match["home"] or "(" in match["away"]:
					continue
				if match["home"]:
					if match["home"] in config["translate"]:
						home = config["translate"][match["home"]]
					else:
						home = match["home"]
					if match["away"] in config["translate"]:
						away = config["translate"][match["away"]]
					else:
						away = match["away"]
					output += match["time"] + r' - <strong>' + home.upper() + r' - ' +  away.upper() + r'</strong>' + '\n'
				elif match["event"]:
					output += match["time"] + r' - <strong>' + match["event"].upper() + r'</strong>' + '\n'

				output += r'<span style="font-size: 10pt;"><img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f4fa.svg" alt="📺" /> '
				output += r'<a href="' + match['link'] + r'" target="_blank" rel="noopener">Viaplay</a> '
				if match["comment"] == "Transmisja bez komentarza":
					match["comment"] = 'brak'
				if ' ' not in match["comment"]:
					match["comment"] = match["comment"].lower() #podany tylko język
				output += r'<img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f399.svg" alt="🎙" width="16" height="16" /> ' + match["comment"] + r'</span>' + '\n'
				output += '\n'
			if new_league["comm"]:
				output += r'<span style="font-size: 10pt;"><em>' + new_league["comm"] + r'</em></span>' + '\n'
				output += '\n'
			output += r'<hr />' + '\n'
	pyperclip.copy(output)


if __name__ == '__main__':
	date = input("Podaj datę (YYYY-MM-DD):")
	matches = getMatches(date)
	try:
		matches = correct_time(matches, date)
	except:
		print("Nie udało się zsynchronizować meczów")
	show(matches)
	print("Rozpiska została skopiowana do schowka")
	input()
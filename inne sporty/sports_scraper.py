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

	driver.get("https://www.flashscore.pl/hokej/")

	wait = WebDriverWait(driver, 10)
	cookies = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler")))
	cookies.click()

	date_diff = datetime.date.fromisoformat(custom_date) - datetime.date.today()
	for i in range(date_diff.days):
		wait.until(EC.element_to_be_clickable((By.XPATH, './/button[@data-day-picker-arrow="next"]')))
		driver.find_element(By.XPATH, './/button[@data-day-picker-arrow="next"]').click()
	# wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'pokaż spotkania')]")))

	# expand = driver.find_elements(By.XPATH, "//*[contains(text(), 'pokaż spotkania')]")
	# for button in expand:
	# 	button.click()
	sleep(5)

	f = open('config.json', 'r', encoding='utf-8')
	config = json.load(f)
	f.close()

	matches = driver.find_elements(By.XPATH, './/div[@data-event-row="true"]')

	games = []

	for match in matches:
		home = match.find_element(By.CSS_SELECTOR, '.event__participant--home').text
		away = match.find_element(By.CSS_SELECTOR, '.event__participant--away').text
		try:
			matchtime = match.find_element(By.CSS_SELECTOR, '.event__time').text
		except:
			matchtime = "brak"
		games.append({
			'home': home,
			'away': away,
			'time': matchtime})

	return games

def show(matches):

	output = ''
	f = open('config.json', 'r', encoding='utf-8')
	config = json.load(f)
	f.close()

	# sort = [x["name_flashscore"] for x in config["leagues"]]

	# for league in matches:
	# 	if league['name'] not in sort:
	# 		print("Dodaj", league['name'], "do configa")
	# matches = list(filter(lambda i: i['name'] in sort, matches))

	# matches = sorted(matches, key=lambda x: sort.index(x["name"]))
	# for league in matches:
	# 	if [x['home'] for x in league['matches']] == ['']:
	# 		continue
	# 	new_league = next((sub for sub in config["leagues"] if sub["name_flashscore"] == league["name"]), None)

	# 	if new_league["show"]:
	# 		output += r'<img class="aligncenter wp-image-' + str(new_league["wp_img"]) + r'" src="' + new_league["img"] + r'" alt="" width="' + str(new_league["img_w"]) + r'" height="' + str(new_league["img_h"]) + r'" />' + '\n'
	# 		output += r'<h2 style="text-align: center;"><span style="font-size: 18pt;"><strong>' + new_league["name_matchday"].upper() + r'</strong></span></h2>' + '\n'
	for match in matches:
		# if match["event"] in config["ignore"] or "(" in match["home"] or "(" in match["away"]:
		# 	continue
		# if match["home"]:
		# 	if match["home"] in config["translate"]:
		# 		home = config["translate"][match["home"]]
		# 	else:
		home = match["home"]
		# 	if match["away"] in config["translate"]:
		# 		away = config["translate"][match["away"]]
		# 	else:
		away = match["away"]
		output += match["time"] + r' - <strong>' + home.upper() + r' - ' +  away.upper() + r'</strong>' + '\n'
		# elif match["event"]:
		# 	output += match["time"] + r' - <strong>' + match["event"].upper() + r'</strong>' + '\n'

		output += r'<span style="font-size: 10pt;"><img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f4fa.svg" alt="📺" /> '
		output += r'<a href="https://www.dazn.com/en-PL/schedule" target="_blank" rel="noopener">DAZN</a> (płatne)'
		# if match["comment"] == "Transmisja bez komentarza":
		# 	match["comment"] = 'brak'
		# if ' ' not in match["comment"]:
		# 	match["comment"] = match["comment"].lower() #podany tylko język
		output += r'<img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f399.svg" alt="🎙" width="16" height="16" /> angielski/brak</span>' + '\n'
		output += '\n'
			# if new_league["comm"]:
			# 	output += r'<span style="font-size: 10pt;"><em>' + new_league["comm"] + r'</em></span>' + '\n'
			# 	output += '\n'
			# output += r'<hr />' + '\n'
	pyperclip.copy(output)


if __name__ == '__main__':
	date = input("Podaj datę (YYYY-MM-DD):")
	# try:
	matches = getMatches(date)
	# except:
	# 	print("Nie udało się zsynchronizować meczów")
	show(matches)
	print("Rozpiska została skopiowana do schowka")
	input()
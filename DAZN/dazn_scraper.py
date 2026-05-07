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
from time import sleep

def getMatches(custom_date):
	options = webdriver.ChromeOptions()
	options.add_argument('--headless')
	options.add_argument('--window-size=1920,1080')
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	options.add_argument('log-level=3')
	options.add_argument('--disable-search-engine-choice-screen')
	global driver
	driver = webdriver.Chrome(service=ChromeService(), options=options)

	url = "https://www.dazn.com/en-PL/schedule"
	driver.get(url)

	wait = WebDriverWait(driver, 10)

	cookies = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler")))
	cookies.click()

	# sleep(5)
	wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.schedule__schedule-container___24S6E')))
	football_filter = wait.until(EC.element_to_be_clickable((By.XPATH, './/li[@data-test-id="SPORTFILTER_LIST_ITEM"]/span[text()="Football"]')))
	football_filter.click()

	[driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END) for x in range(10)]

	matches = []
	leagues = []

	try:
		day = wait.until(EC.visibility_of_element_located((By.XPATH, './/section[@date="' + custom_date + '"]')))
		matches, leagues = getDayInfo(day, matches, leagues, 'gt')
	except TimeoutException:
		print("[INFO] Brak meczów dnia", custom_date)

	try:
		tomorrow = datetime.fromisoformat(custom_date) + timedelta(days=1)
		next_day = driver.find_element(By.XPATH, './/section[@date="' + str(tomorrow.date()) + '"]')
		matches, leagues = getDayInfo(next_day, matches, leagues, 'lt')
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
					'link': match["link"]
					})
		games.append(league)

	return games


# limit: gt -> >= 6:00, lt -> < 6:00
def getDayInfo(day, matches, leagues, limit):
	nextBtn = day.find_element(By.CSS_SELECTOR, ".custom-swiper-button-next")

	while True:
		broadcasts = day.find_elements(By.XPATH, './/div[@aria-hidden="false"]')

		for broadcast in broadcasts:
			time = broadcast.find_element(By.CSS_SELECTOR, '.tile-labels__label___3lzBB.tile-labels__date-and-time___3AK7b').text
			title = broadcast.find_element(By.CSS_SELECTOR, '.tile__title___3VcYJ').text
			try:
				home, away = title.split(' vs. ')
			except ValueError:
				home = title
				away = ''
			league = broadcast.find_element(By.CSS_SELECTOR, '.tile__subtitle-container___2DukV').text
			link = broadcast.find_element(By.CSS_SELECTOR, '.tile__link___vuQG1').get_attribute("href")

			match = {
				'home': home,
				'away': away,
				'time': time,
				'league': league,
				'link': link
				}
			if match in matches:
				continue
			else:
				if (limit == 'lt' and int(time.split(':')[0]) < 6) or (limit == 'gt' and int(time.split(':')[0]) >= 6):
					if league not in leagues:
						leagues.append(league)

					matches.append(match)

		if nextBtn.is_enabled():
			scroll_origin = ScrollOrigin.from_element(nextBtn)
			ActionChains(driver).scroll_from_origin(scroll_origin, 0, 150).perform()
			nextBtn.click()
			# content needs to load a bit
			sleep(1)
		else:
			return matches, leagues


def show(matches, date):
	output = ''
	f = open('config.json', 'r', encoding='utf-8')
	config = json.load(f)
	f.close()

	sort = [x["name_dazn"] for x in config["leagues"]]

	for league in matches:
		if league['name'] not in sort:
			print("Dodaj", league['name'], "do configa")
	matches = list(filter(lambda i: i['name'] in sort, matches))

	matches = sorted(matches, key=lambda x: sort.index(x["name"]))
	for league in matches:
		new_league = next((sub for sub in config["leagues"] if sub["name_dazn"] == league["name"]), None)

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
				output += r'<a href="' + match['link'] + r'" target="_blank" rel="noopener">DAZN</a> '
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
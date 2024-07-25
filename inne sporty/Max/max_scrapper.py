from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import datetime
import json
import pyperclip
import time

def getMatches(custom_date):
	options = webdriver.ChromeOptions()
	options.add_argument('--headless')
	options.add_argument('--window-size=1920,1080')
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	options.add_argument('log-level=3')
	driver = webdriver.Chrome(service=ChromeService(), options=options)

	url = "https://www.max.com/pl/pl/olympics/sports"
	driver.get(url)

	wait = WebDriverWait(driver, 10)

	original_window = driver.current_window_handle

	cookies = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
	cookies.click()

	sports = driver.find_elements(By.CSS_SELECTOR, ".pictograms")

	sports_names = []
	sports_links = [x.find_element(By.TAG_NAME, "a").get_attribute("href") for x in sports]

	matches = []

	for link in sports_links:
		driver.get(link)

		events_container = driver.find_elements(By.CSS_SELECTOR, ".react-multi-carousel-track.content-tray-slider")
		events = events_container[1].find_elements(By.TAG_NAME, "li")
		for event in events:
			details = event.find_element(By.TAG_NAME, "a").get_attribute("aria-label").split(' | ')
			try:
				det_offset, day, time, _ = details[-1].split(',')
			except:
				det_offset, time, _ = details[-1].split(',')
				day = datetime.datetime.now().strftime('%m %d').replace("7", "Lip").replace("8", "Sie")
			href = event.find_element(By.TAG_NAME, "a").get_attribute("href")
			sport = details[0].replace("Bez reklam", "").strip()
			name = (' '.join(details[1:-1]) + det_offset).replace("Polski komentarz", "").replace("Angielski komentarz", "").replace("Bez reklam", "").replace("Igrzyska Olimpijskie", "")

			timedate = datetime.datetime.strptime("2024 " + day.strip().replace("Lip", "7").replace("Sie", "8") + time, '%Y %m %d %I:%M%p')
			time = (timedate + datetime.timedelta(hours=2)).strftime('%H:%M')


			if timedate.date() == datetime.datetime.fromisoformat(custom_date).date():
				matches.append({
					'name': name,
					'time': time,
					'sport': sport,
					'link': href
					})

				if sport not in sports_names:
					sports_names.append(sport)

			elif timedate.date() > datetime.datetime.fromisoformat(custom_date).date():
				break

	games = []

	for event in sports_names:
		sport = {
			'name': event,
			'matches': []
			}

		for match in matches:
			if match["sport"] == event:
				sport["matches"].append({
					'name': match["name"],
					'time': match["time"],
					'link': match["link"]
					})
		games.append(sport)

	return games

def show(matches):
	output = ''

	for league in matches:
		output += r'<h2 style="text-align: center;"><span style="font-size: 18pt;"><strong>' + league["name"].upper() + r'</strong></span></h2>' + '\n'
		for match in league["matches"]:
			output += match["time"] + r' - <strong>' + match["name"].upper() + r'</strong>' + '\n'
			output += r'<span style="font-size: 10pt;"><img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f4fa.svg" alt="📺" /> '
			output += r'<a href="' + match['link'] + r'" target="_blank" rel="noopener">MAX</a> '
			output += r'<img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f399.svg" alt="🎙" width="16" height="16" /> brak </span>' + '\n'
			output += '\n'
		output += r'<hr />' + '\n'
	pyperclip.copy(output)


if __name__ == '__main__':
	date = input("Podaj datę (YYYY-MM-DD):")
	matches = getMatches(date)
	show(matches)
	print("Rozpiska została skopiowana do schowka")
	input()

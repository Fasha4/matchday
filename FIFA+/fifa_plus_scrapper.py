from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
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

	url = "https://www.plus.fifa.com/en/showcase/1472c76e-0e28-44bf-8b28-b05229545879"
	driver.get(url)

	wait = WebDriverWait(driver, 10)

	original_window = driver.current_window_handle

	cookies = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler")))
	cookies.click()

	elements = driver.find_elements(By.CSS_SELECTOR, ".content-items-showcase")
	driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

	ad = wait.until(EC.element_to_be_clickable((By.ID, "modal-button-close")))
	ad.click()

	driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

	#show all matches
	while True:
		driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
		new_elements = driver.find_elements(By.CSS_SELECTOR, ".content-items-showcase")

		if len(new_elements) == len(elements):
			break
		else:
			elements = new_elements
			[driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END) for i in range(10)]

	matches = []
	leagues = []
	events = [x.text for x in elements]
	links = [x.find_element(By.TAG_NAME, "a").get_attribute("href") for x in elements]
	counter = 0

	for match in events:
		home, away, time, league, link = 5*['']

		link = links[counter]
		counter += 1

		driver.get(link)

		try:
			timedate = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".sc-aXZVg.lmkGNG.typography.info__event__startDate")))
		except:
			continue
		timedate_clean = timedate.text.replace("1st", "1").replace("2nd", "2").replace("3rd", "3").replace("th", "")
		try:
			timedate_str = datetime.datetime.strptime(timedate_clean, '%d %B %Y, %H:%M')
		except:
			timedate_str = datetime.datetime.strptime(timedate_clean, '%d %B %Y')
		time = timedate_str.strftime('%H:%M')
		if time[-2:] == '15' or time[-2:] == '45':
			temp_time = datetime.datetime.strptime(time, '%H:%M') + datetime.timedelta(minutes=15)
			time = temp_time.strftime('%H:%M')
		elif time[-2:] == '20' or time[-2:] == '50':
			temp_time = datetime.datetime.strptime(time, '%H:%M') + datetime.timedelta(minutes=10)
			time = temp_time.strftime('%H:%M')
		elif time[-2:] == '55':
			temp_time = datetime.datetime.strptime(time, '%H:%M') + datetime.timedelta(minutes=5)
			time = temp_time.strftime('%H:%M')

		day_offset = datetime.timedelta(hours=6)

		if timedate_str < datetime.datetime.fromisoformat(custom_date) + day_offset:
			continue
		elif timedate_str >= datetime.datetime.fromisoformat(custom_date) + day_offset + datetime.timedelta(days=1):
			break

		details = match.split(' | ')
		try:
			home, away = details[0].split(' v ')
		except:
			home = details[0]
		if details[-1] in ['Costa Rica', 'Saint Kitts and Nevis', 'Grenada', 'Turks and Caicos']:
			league = details[-2] + ' ' + details[-1]
		elif ' ' not in details[-1] or details[-1] in ['Live Stream']:
			league = details[-2]
		else:
			league = details[-1]
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
				output += match["time"] + r' - <strong>' + home.upper() + r' - ' +  away.upper() + r'</strong>' + '\n'
				output += r'<span style="font-size: 10pt;"><img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f4fa.svg" alt="📺" /> '
				output += r'<a href="' + match['link'] + r'" target="_blank" rel="noopener">FIFA+</a> '
				output += r'<img class="emoji" role="img" draggable="false" src="https://s.w.org/images/core/emoji/14.0.0/svg/1f399.svg" alt="🎙" width="16" height="16" /> ' + new_league["lang"] + r'</span>' + '\n'
				output += '\n'
				if not addComm:
					addComm, dayInfo = isNextDay(match["time"], date)
			if addComm:
				output += r'<span style="font-size: 10pt;"><em>W nocy z ' + dayInfo + r'</em></span>' + '\n'
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
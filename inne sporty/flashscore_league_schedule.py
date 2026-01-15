from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import datetime
import json
import pyperclip

def getMatches(url):
	options = webdriver.ChromeOptions()
	options.add_argument('--headless')
	options.add_argument('--window-size=1920,1080')
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	options.add_argument('log-level=3')
	options.add_argument('--disable-search-engine-choice-screen')
	driver = webdriver.Chrome(service=ChromeService(), options=options)

	driver.get(url)

	wait = WebDriverWait(driver, 5)
	cookies = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler")))
	cookies.click()

	while True:
		try:
			showMore = wait.until(EC.visibility_of_element_located((By.XPATH, ".//a[@data-testid='wcl-buttonLink']")))
			ActionChains(driver).move_to_element(showMore).perform()
			sleep(1)
			showMore.click()
		except:
			break

	matches = driver.find_elements(By.XPATH, './/div[@data-event-row="true"]')

	games = []
	year = datetime.datetime.now().year
	prev_month = ''

	for match in matches:
		if "Przeł." in match.text:
			continue

		home = match.find_element(By.CSS_SELECTOR, '.event__participant--home').text
		away = match.find_element(By.CSS_SELECTOR, '.event__participant--away').text

		matchtime = match.find_element(By.CSS_SELECTOR, '.event__time').text
		date, time = matchtime.split()
		date = datetime.datetime.strptime(f"{date}{year}", "%d.%m.%Y")
		if date.month == 1 and prev_month == 12:
			year = year + 1
			date = date.replace(year=year)
		print(date)
		prev_month = date.month
		games.append({
			'home': home,
			'away': away,
			'date': date,
			'time': time})

	return games


def show(matches):

	output = ''
	prev_date = ''

	for match in matches:
		date = match["date"]
		if date != prev_date:
			if datetime.time.fromisoformat(match["time"]) < datetime.time(hour=6):
				if prev_date != date - datetime.timedelta(days=1):
					output += r'<h2>' + (date - datetime.timedelta(days=1)).strftime("%d.%m.") + r'</h2>'
					prev_date = date - datetime.timedelta(days=1)
			else:
				output += r'<h2>' + date.strftime("%d.%m.") + r'</h2>'
				prev_date = date

		output += match["time"] + ' '
		if datetime.time.fromisoformat(match["time"]) < datetime.time(hour=6):
			output += dayChange(match["date"])
		home = match["home"]
		away = match["away"]
		output += r' - <strong>' + home.upper() + r' - ' +  away.upper() + r'</strong>' + '\n'
	pyperclip.copy(output)


def dayChange(date):
	days = ["pn", "wt", "śr", "czw", "pt", "sb", "nd"]
	today = date.weekday()
	yesterday = (date - datetime.timedelta(days=1)).weekday()

	return "(" + days[yesterday] + "/" + days[today] + ")"


if __name__ == '__main__':
	url = input("Podaj url z flashscore -> liga -> mecze:")
	matches = getMatches(url)
	show(matches)
	print("Rozpiska została skopiowana do schowka")
	input()
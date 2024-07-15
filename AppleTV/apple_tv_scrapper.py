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
	driver = webdriver.Chrome(service=ChromeService(), options=options)

	url = "https://tv.apple.com/pl/channel/tvs.sbd.7000"
	driver.get(url)

	wait = WebDriverWait(driver, 10)

	sleep(5)
	while True:
		try:
			nextBtn = driver.find_elements(By.CSS_SELECTOR, ".shelf-grid-nav__arrow.shelf-grid-nav__arrow--next")
			nextBtn[1].click()
		except:
			break

	shelf = driver.find_elements(By.CSS_SELECTOR, ".shelf-grid__body")[1]
	matches = shelf.find_elements(By.CSS_SELECTOR, ".shelf-grid__list-item")
	for match in matches[5:]:
		# print(match.text)
		try:
			teams = match.find_element(By.CSS_SELECTOR, '.typ-subhead.text-truncate')
			league = match.find_element(By.CSS_SELECTOR, '.typ-footnote.clr-secondary-text.text-truncate')
			print(teams.text, league.text)
		except:
			continue
			# try:

			# 	print(info.text)
			# except:
			# 	continue

		# sleep(3)
		# nextBtn = driver.find_elements(By.CSS_SELECTOR, ".shelf-grid-nav__arrow.shelf-grid-nav__arrow--next")
		# nextBtn[1].click()
		# except:
		# 	break

	# for match in matches:
	# 	teams = match.find_element(By.CSS_SELECTOR, ".typ-subhead.text-truncate")
	# 	print(teams.text)
	# 	try:
	# 		time = match.find_element(By.TAG_NAME, "time").get_attribute(datetime)
	# 		print(time.text)
	# 	except:
	# 		continue


	# freeMatches = elements[2].find_elements(By.CSS_SELECTOR, ".typ-subhead.text-truncate")
	# for freeMatch in freeMatches:
	# 	print(freeMatch.text)

if __name__ == '__main__':
	#date = input("Podaj datę (YYYY-MM-DD):")
	date = '2024-07-14'
	matches = getMatches(date)
	# show(matches, date)
	# print("Rozpiska została skopiowana do schowka")
	# input()
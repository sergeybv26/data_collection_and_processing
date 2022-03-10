"""
Написать программу, которая собирает входящие письма из своего или тестового почтового ящика
и сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
Логин тестового ящика: study.ai_172@mail.ru
Пароль тестового ящика: NextPassword172#
"""
import time

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

CLIENT_DB = MongoClient('127.0.0.1', 27017)
DB = CLIENT_DB['mail']

service = Service(executable_path="./chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.get('https://mail.ru/')

enter_button = driver.find_element(By.XPATH, "//button[@data-testid='enter-mail-primary']")
enter_button.click()

wait = WebDriverWait(driver, 30)

login_frame = wait.until(EC.presence_of_element_located((By.XPATH,
                                                         "//iframe[@class='ag-popup__frame__layout__iframe']")))
driver.switch_to.frame(login_frame)
username = wait.until(EC.presence_of_element_located((By.NAME, 'username')))
username.send_keys('study.ai_172')
username.submit()

time.sleep(1)

password = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
password.send_keys('NextPassword172#')
password.submit()

driver.switch_to.default_content()

mail_set = set()

while True:
    driver.implicitly_wait(10)
    mail_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'llc')]")
    if mail_elements[-1].get_attribute('href') in mail_set:
        break
    for elem in mail_elements:
        mail_link = elem.get_attribute('href')
        mail_set.add(mail_link)
    action = ActionChains(driver)
    action.move_to_element(mail_elements[-1])
    action.perform()
    time.sleep(2)

mail_info_list = []

for elem in mail_set:
    mail_dict = {}
    if elem is None:
        continue
    driver.get(elem)
    sender = driver.find_element(By.XPATH, "//div[@class='letter__author']/span")
    mail_dict['_id'] = elem.split('/')[4][2: -2]
    mail_dict['sender'] = sender.get_attribute('title')
    mail_dict['topic'] = driver.find_element(By.XPATH, "//h2").text
    mail_dict['message'] = driver.find_element(By.XPATH, "//div[@class='letter__body']").text
    mail_dict['date'] = driver.find_element(By.XPATH, "//div[@class='letter__date']").text

    mail_info_list.append(mail_dict)

error_list = []
database = DB.mail
for el in mail_info_list:
    try:
        database.insert_one(el)
    except DuplicateKeyError:
        error_list.append(el)

print(error_list)

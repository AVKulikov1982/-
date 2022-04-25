import os
import time
import requests
import logging
from bs4 import BeautifulSoup


logger = logging.getLogger('__name__')

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0'}
session = requests.Session()

HOST = '' # хост
URL = HOST + '/client/bills'
link = HOST + '/login?view=login'

data = {
	"login": "",  #  логин пользователя
	"password": "",  #  пароль пользователя
	"form_action": "login",
	"enter": "Войти"
}

response = session.post(link, data=data, headers=HEADERS)
time.sleep(1)


def get_response_bills(url: str) -> requests.Response:
	'''
	Функция на вход получает url, возвращает Response объект.
	:param url: url
	:return: 
	'''
	response_bills = session.get(url, headers=HEADERS)
	return response_bills


def get_pages_count(soup) -> int:
	'''
	Функция — обработчик пагинации; на вход получает объект soup, возвращает количество страниц.
	:param soup: object BeautifulSoup
	:return:
	'''
	pagination_to = soup.find('div', class_='PageSelector')
	pages_count = 1
	if pagination_to:
		pagination = pagination_to.find_all('a')
		last_href = pagination[-1].get('href')
		pages_count = int(last_href.split('&')[0].split('=')[-1])
	return pages_count


def parse():
	'''
	Функция парсер.
	:return:
	'''
	response_bills = get_response_bills(URL) #  получаем объект Response
	soup = BeautifulSoup(response_bills.text, 'html.parser') #  получаем объект BeautifulSoup
	pages_count = get_pages_count(soup) #  получаем количество страниц (пагинация)
	for page in range(1, pages_count + 1):
		logger.info(f'Парсинг страницы {page} {pages_count} {URL}...')
		html = session.get(URL, headers=HEADERS, params={'page': page})
		soup = BeautifulSoup(html.text, 'html.parser')
		bills = soup.find_all('a', class_='list_item')
		for bill in bills:
			bill_date = bill.find_all('div', class_='managers_lists_container_block')[1].get_text().replace(' ', '_')
			response_to_bill = session.get(HOST + bill.get('href'), headers=HEADERS)
			soup_bill = BeautifulSoup(response_to_bill.text, 'html.parser')
			list_links = soup_bill.find('div', id='page_buttons_container').find_all('a', class_='success')
			list_data = list(
				map(lambda x: x.get_text().strip(), soup_bill.find_all('div', class_='customer_overall_block_right')))
			time.sleep(1)
			for doc_link in list_links:
				path = doc_link.get('href').split('id=')[-1] + '-' + bill_date
				if 'Счет на предоплату' in list_data:
					path += '_предоплата'
				if 'За счет предоплаты' in list_data:
					path += '_оплачено_предоплатой'
				if 'С бонусного счета' in list_data:
					path += '_оплачено_бонусами'
				if path not in os.listdir():
					os.mkdir(path)

				response_to_doc_link = session.get(HOST + doc_link.get('href'), headers=HEADERS)
				try:
					if 'счета' in doc_link.get_text():
						f = open(path + '/bill.pdf', 'wb')
					elif 'детализации' in doc_link.get_text():
						f = open(path + '/detail.xlsx', 'wb')
					elif 'акта' in doc_link.get_text():
						f = open(path + '/act.pdf', 'wb')
					else:
						raise ValueError
					f.write(response_to_doc_link.content)
					f.close()
					time.sleep(1)
				except:
					logger.error(f'Error parser')


if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO, filename='bot.log', filemode='a',
						format='%(asctime)s - %(levelname)s - %(message)s',
						datefmt='%d-%b-%y %H:%M:%S')
	logger.info(f'Start parser')
	parse()

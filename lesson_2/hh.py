import json
from pprint import pprint
import requests
from bs4 import BeautifulSoup as bs
jobs_input_name = input('Job: ')

def get_url(page):
    url = f'https://spb.hh.ru/search/vacancy?search_' \
          f'field=name&search_field=company_name&search_' \
          f'field=description&text={jobs_input_name}&page={page}&hhtmFrom=vacancy_search_list'

    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/96.0.4664.110 Safari/537.36'}
    response = requests.get(url, headers=headers)
    dom = bs(response.text, 'html.parser')
    jobs = dom.find_all('div', {'class': 'vacancy-serp-item-body'})
    selector = dom.find_all('a', {'data-qa': 'pager-next'})
    return jobs, selector

jobs_list = []


def scrap_info(page=0):
    jobs, selector = get_url(page)
    for job in jobs:
        jobs_data = {}
        job_name = job.find('a', {'class': 'bloko-link'}).contents[0]
        job_link = job.find('a', {'class': 'bloko-link'})['href']
        salary = job.find('span', {'data-qa': 'vacancy-serp__vacancy-'
                                              'compensation'})

        if salary is None:
            min_salary = None
            max_salary = None
            currency = None
            jobs_data['job_name'] = job_name
            jobs_data['job_link'] = job_link
            jobs_data['min_salary'] = min_salary
            jobs_data['max_salary'] = max_salary
            jobs_data['currency'] = currency
            jobs_list.append(jobs_data)

        else:
            if len(salary.contents) == 7:
                word = salary.contents[0]
                if word == 'от ':
                    min_salary = int(str(salary.contents[2]).replace('\u202f', ''))
                    currency = str(salary.contents[6])
                    jobs_data['job_name'] = job_name
                    jobs_data['job_link'] = job_link
                    jobs_data['min_salary'] = min_salary
                    jobs_data['max_salary'] = None
                    jobs_data['currency'] = currency
                    jobs_list.append(jobs_data)
                elif word == ' до':
                    max_salary = int(str(salary.contents[0]).replace('\u202f', ''))
                    currency = str(salary.contents[6])
                    jobs_data['job_name'] = job_name
                    jobs_data['job_link'] = job_link
                    jobs_data['min_salary'] = None
                    jobs_data['max_salary'] = max_salary
                    jobs_data['currency'] = currency
                    jobs_list.append(jobs_data)

            if len(salary.contents) == 3:
                all_price = str(salary.contents[0]).replace('\u202f', '')\
                    .split('–')
                min_salar = int(all_price[0].replace(' ', ''))
                max_salar = int(all_price[1].replace(' ', ''))
                currency = str(salary.contents[2])
                jobs_data['job_name'] = job_name
                jobs_data['job_link'] = job_link
                jobs_data['min_salary'] = min_salar
                jobs_data['max_salary'] = max_salar
                jobs_data['currency'] = currency
                jobs_list.append(jobs_data)
    if selector:
        return scrap_info(page+1)

    with open(f'{jobs_input_name}.json', 'w') as f:
        json.dump(jobs_list, f, indent=2, ensure_ascii=False)

scrap_info(0)
pprint(jobs_list)

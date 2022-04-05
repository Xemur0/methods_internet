from pprint import pprint
from pymongo.errors import DuplicateKeyError
import requests
from bs4 import BeautifulSoup as Bs
from pymongo import MongoClient

jobs_input_name = input('Job: ')
headhunter = MongoClient('localhost', 27017)
database_for_jobs = headhunter[f'{jobs_input_name}']

jobs_collection = database_for_jobs.jobs
jobs_collection.create_index("job_id", unique=True)
index_list = sorted(list(jobs_collection.index_information()))
print(index_list)

jobs_list = []


def insert_job(jobs_data, job_name, job_link, min_salary, max_salary,
               currency):
    jobs_data['job_name'] = job_name
    jobs_data['job_link'] = job_link
    jobs_data['min_salary'] = min_salary
    jobs_data['max_salary'] = max_salary
    jobs_data['currency'] = currency
    jobs_data['job_id'] = job_link[26:33]


def get_url(page):
    url = f'https://spb.hh.ru/search/vacancy?text={jobs_input_name}&' \
          f'salary=&currency_code=RUR&experience=doesNotMatter&order_by=' \
          f'relevance&search_period=0&items_on_page=20&no_magic=true&L_' \
          f'save_area=true&page={page}&hhtmFrom=vacancy_search_list'

    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/96.0.4664.110 Safari/537.36'}

    response = requests.get(url, headers=headers)
    dom = Bs(response.text, 'html.parser')
    jobs = dom.find_all('div', {'class': 'vacancy-serp-item-body'})
    selector = dom.find_all('a', {'data-qa': 'pager-next'})
    return jobs, selector


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
            insert_job(jobs_data, job_name, job_link, min_salary, max_salary,
                       currency)
            jobs_list.append(jobs_data)
            try:
                jobs_collection.insert_one(jobs_data)
            except DuplicateKeyError:
                print(f'Job {jobs_data["job_id"]} is already EXIST')

        else:
            if len(salary.contents) == 7:
                word = salary.contents[0]
                if word == 'от ':
                    min_salary = int(str(salary.contents[2])
                                     .replace('\u202f', ''))
                    currency = str(salary.contents[6])
                    insert_job(jobs_data, job_name, job_link, min_salary,
                               None, currency)
                    jobs_list.append(jobs_data)
                    try:
                        jobs_collection.insert_one(jobs_data)
                    except DuplicateKeyError:
                        print(f'Job {jobs_data["job_id"]} is already EXIST')

                elif word == ' до':
                    max_salary = int(str(salary.contents[0])
                                     .replace('\u202f', ''))
                    currency = str(salary.contents[6])
                    insert_job(jobs_data, job_name, job_link, None,
                               max_salary, currency)
                    jobs_list.append(jobs_data)
                    try:
                        jobs_collection.insert_one(jobs_data)
                    except DuplicateKeyError:
                        print(f'Job {jobs_data["job_id"]} is already EXIST')

            if len(salary.contents) == 3:
                all_price = str(salary.contents[0]).replace('\u202f', '') \
                    .split('–')
                min_salar = int(all_price[0].replace(' ', ''))
                max_salar = int(all_price[1].replace(' ', ''))
                currency = str(salary.contents[2])
                insert_job(jobs_data, job_name, job_link, min_salar,
                           max_salar, currency)
                jobs_list.append(jobs_data)

                try:
                    jobs_collection.insert_one(jobs_data)
                except DuplicateKeyError:
                    print(f'Job {jobs_data["job_id"]} is already EXIST')

    if selector:
        return scrap_info(page + 1)


scrap_info(0)

for doc in jobs_collection.find({}):
    pprint(doc)

salary_info = int(input('Введите желаемую зарплату в рублях: '))

cur_USD = 83
cur_EUR = 91

for doc in jobs_collection.find({'$or': [{'currency': 'руб.'},
                                         {'currency': 'USD'},
                                         {'currency': 'EUR'},
                                         ]
                                 },
                                ):
    if doc['currency'] == 'руб.':
        if doc['min_salary'] is not None and doc['min_salary'] > salary_info \
                or doc['max_salary'] is not None and \
                doc['max_salary'] > salary_info:
            pprint(doc)
    elif doc['currency'] == 'USD':
        if doc['min_salary'] is not None and (doc['min_salary']) * \
                cur_USD > salary_info or doc['max_salary'] is not None \
                and (doc['max_salary']) * cur_USD > salary_info:
            pprint(doc)
    elif doc['currency'] == 'EUR':
        if doc['min_salary'] is not None and (doc['min_salary']) \
                * cur_EUR > salary_info or doc['max_salary'] is not None \
                and (doc['max_salary']) * cur_EUR > salary_info:
            pprint(doc)
    else:
        continue

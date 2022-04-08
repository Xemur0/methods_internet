import requests
from pprint import pprint
from lxml import html
from datetime import datetime
from pymongo import MongoClient

url = 'https://news.mail.ru/'

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/96.0.4664.110 Safari/537.36'}


def scrap_news_mail():
    response = requests.get(url, headers=headers)
    dom = html.fromstring(response.text)

    picture_news = dom.xpath("//div[contains(@class, 'daynews__item')]")

    news = dom.xpath('//ul[contains(@class, "list")]'
                     '/li[contains(@class, "list__item")]/a[position()=1]')

    news_list = []

    for item in news:
        element = {}

        news_name = item.xpath('.//text()')
        element['name'] = str(news_name[0]).replace(u'\xa0', u' ')

        # Либо можно так получить текст
        # ибо получили уже элемент и можно так с ним взаимодействовать
        # но так как тема икспас, будет икспас! :)
        # news_link = item.text

        news_link = item.xpath('../a/@href')

        element['link'] = str(news_link[0])

        response = requests.get(element['link'], headers=headers)
        dom = html.fromstring(response.text)

        news_date = dom.xpath('//span/@datetime')
        news_date = datetime.strptime(str(news_date[0]), '%Y-%m-%dT%H:%M:%S%z')
        element['date'] = news_date.strftime('%Y-%m-%d %H:%M')

        news_source = dom.xpath('//span[contains(@class, "note")]/*'
                                '/span[contains(@class, "link__text")]/text()')
        element['source'] = str(news_source[0])

        news_list.append(element)

    for item in picture_news:
        element = {}

        news_name = item.xpath('.//text()')
        element['name'] = str(news_name[0]).replace(u'\xa0', u' ')

        news_link = item.xpath('./a/@href')
        element['link'] = str(news_link[0])

        response = requests.get(element['link'], headers=headers)
        dom = html.fromstring(response.text)
        news_date = dom.xpath('//span/@datetime')
        news_date = datetime.strptime(str(news_date[0]),
                                      '%Y-%m-%dT%H:%M:%S%z')
        element['date'] = news_date.strftime('%Y-%m-%d %H:%M')
        news_list.append(element)

    return news_list


def main():
    news_list = scrap_news_mail()

    client = MongoClient('localhost', 27017)
    db = client['news']
    news = db.news

    for item in news_list:
        news.insert_one(item)
        pprint(item)
        print('news successfully add to DB')


main()

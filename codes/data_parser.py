from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime


def data_parser(stock_item, start_date):
    """

    :param stock_item: stock item id number
    :param start_date: start date parsing term
    :return: ['date', 'open', 'high', 'low', 'close', 'volume']
    """
    stock_item = str(stock_item)
    fmt = "%Y.%m.%d"
    start_date = datetime.strptime(start_date, fmt).date()
    url = 'http://finance.naver.com/item/sise_day.nhn?code=' + stock_item
    html = urlopen(url)
    source = BeautifulSoup(html.read(), "html.parser")

    max_page = source.find_all("table", align="center")
    mp = max_page[0].find_all("td", class_="pgRR")
    mpNum = int(mp[0].a.get('href')[-3:])

    data_list = list()

    for page in range(1, mpNum + 1):
        url = 'http://finance.naver.com/item/sise_day.nhn?code=' + stock_item + '&page=' + str(page)
        html = urlopen(url)
        source = BeautifulSoup(html.read(), "html.parser")
        srlists = source.find_all("tr")
        is_check_none = None

        for i in range(1, len(srlists) - 1):
            if srlists[i].span != is_check_none:
                date = datetime.strptime(srlists[i].find_all("td", align="center")[0].text, fmt).date()
                date_checker = date >= start_date
                if not date_checker:
                    return data_list
                close_price = srlists[i].find_all("td", class_="num")[0].text
                open_price = srlists[i].find_all("td", class_="num")[2].text
                high_price = srlists[i].find_all("td", class_="num")[3].text
                low_price = srlists[i].find_all("td", class_="num")[4].text
                volume = srlists[i].find_all("td", class_="num")[5].text
                data_list.append((date, open_price, high_price, low_price, close_price, volume))


if __name__ == "__main__":
    data_list = data_parser('005930', '2017.09.20')
    for data in data_list:
        print(data)

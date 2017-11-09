from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime


class FinanceDataParser:
    def __init__(self):
        self._url = 'http://finance.naver.com/item/sise_day.nhn?code='
        self._start_date = '2014.01.01'

    def historical_finance(self, stock_item, start_date=None):
        """
        parse historical finance data from start-date to present
        :param stock_item: stock item id number
        :param start_date: start date parsing term
        :return: ['date', 'open', 'high', 'low', 'close', 'volume']
        """
        if start_date is None:
            start_date = self._start_date
        fmt = "%Y.%m.%d"
        start_date = datetime.strptime(start_date, fmt).date()
        url = self._url + str(stock_item)
        html = urlopen(url)
        source = BeautifulSoup(html.read(), "html.parser")

        max_page = source.find_all("table", align="center")
        mp = max_page[0].find_all("td", class_="pgRR")
        mpNum = int(mp[0].a.get('href')[-3:])

        finanace_data = list()
        for page in range(1, mpNum + 1):
            url = self._url + str(stock_item) + '&page=' + str(page)
            html = urlopen(url)
            source = BeautifulSoup(html.read(), "html.parser")
            srlists = source.find_all("tr")
            is_check_none = None
            for i in range(1, len(srlists) - 1):
                if srlists[i].span != is_check_none:
                    date = datetime.strptime(srlists[i].find_all("td", align="center")[0].text, fmt).date()
                    if not date >= start_date:
                        return finanace_data
                    close_price = srlists[i].find_all("td", class_="num")[0].text
                    open_price = srlists[i].find_all("td", class_="num")[2].text
                    high_price = srlists[i].find_all("td", class_="num")[3].text
                    low_price = srlists[i].find_all("td", class_="num")[4].text
                    volume = srlists[i].find_all("td", class_="num")[5].text
                    finanace_data.append((date, open_price, high_price, low_price, close_price, volume))


if __name__ == "__main__":
    parser = FinanceDataParser()
    data_list = parser.historical_finance('005930')
    for data in data_list:
        print(data)

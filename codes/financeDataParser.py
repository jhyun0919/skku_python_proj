from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime
import locale
import numpy as np

__author__ = "Park Jee Hyun"
__copyright__ = "N.A."
__credits__ = ["Park Jee Hyun"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Park Jee Hyun"
__email__ = "jhyun19@gmail.com"
__status__ = "Production"


class FinanceDataParser:
    def __init__(self):
        self._url = 'http://finance.naver.com/item/sise_day.nhn?code='
        self._start_date = '2017.01.01'
        self._dtype = {'names': ['date', 'open', 'high', 'low', 'close', 'volume'],
                       'formats': ['object', 'f4', 'f4', 'f4', 'f4', 'f4']}
        self._stock_items_dict = {'005930': 'naver',
                                  '035720': 'kakao',
                                  '036570': 'ncsoft',
                                  '005390': 'posco',
                                  '004020': '현대제철',
                                  '000660': 'sk하이닉스',
                                  '034730': 'sk',
                                  '017670': 'skt',
                                  '030200': 'kt',
                                  '066570': 'lg전자',
                                  '032640': 'lg-Uplus',
                                  '000150': '두산',
                                  '000880': '한화',
                                  '023530': '롯데쇼핑',
                                  '002270': '롯데푸드',
                                  '005380': '현대차'}

    def quotes_historical_finance(self, start_date=None):
        """
        parse historical finance data of the stock-items during the period from start-date to present
        :param start_date: start date parsing term
        :return: quotes ['date', 'open', 'high', 'low', 'close', 'volume']
        """
        stock_items, names = np.array(sorted(self._stock_items_dict.items())).T
        quotes = list()
        num = 0
        for stock_item in stock_items:
            num += 1
            print('{step}.'.format(step=num), end='\t')
            print('fetching quote history for \"{stock_item}\"'.format(stock_item=self._stock_items_dict[stock_item]))
            quotes.append(FinanceDataParser._retry(self._historical_finance)(stock_item, start_date))
        return np.array(quotes, dtype=self._dtype)

    def _historical_finance(self, stock_item, start_date=None):
        """
        parse historical finance data of the stock-item during the period from start-date to present
        :param stock_item: stock item id number
        :param start_date: start date parsing term
        :return: quote ['date', 'open', 'high', 'low', 'close', 'volume']
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

        finance_data = list()
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
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
                        return finance_data
                    close_price = float(locale.atof(srlists[i].find_all("td", class_="num")[0].text))
                    open_price = float(locale.atof(srlists[i].find_all("td", class_="num")[2].text))
                    high_price = float(locale.atof(srlists[i].find_all("td", class_="num")[3].text))
                    low_price = float(locale.atof(srlists[i].find_all("td", class_="num")[4].text))
                    volume = float(locale.atof(srlists[i].find_all("td", class_="num")[5].text))
                    finance_data.append((date, open_price, high_price, low_price, close_price, volume))

    @staticmethod
    def _retry(f, n_attempts=3):
        """
        Wrapper function to retry function calls in case of exceptions
        :param f:
        :param n_attempts:
        :return:
        """

        def wrapper(*args, **kwargs):
            for i in range(n_attempts):
                try:
                    return f(*args, **kwargs)
                except Exception:
                    if i == n_attempts - 1:
                        raise

        return wrapper

    def get_stock_items(self):
        stock_items, _ = np.array(sorted(self._stock_items_dict.items())).T
        return stock_items

    def get_names(self):
        _, names = np.array(sorted(self._stock_items_dict.items())).T
        return names


if __name__ == "__main__":
    pass

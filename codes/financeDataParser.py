from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime
import locale
import numpy as np

__author__ = "Park Jee Hyun", "Mun Hyun Gyu", "Ahn ho geun"
__copyright__ = "Copyright 2017, SKKU Term Project"
__credits__ = ["Park Jee Hyun", "Mun Hyun Gyu", "Ahn ho geun"]
__license__ = "BSD 3 clause"
__version__ = "2.0.0"
__maintainer__ = "Park Jee Hyun"
__email__ = "jhyun19@gmail.com"

__reference__ = "http://estenpark.tistory.com/353", \
                "http://scikit-learn.org/stable/auto_examples/applications/plot_stock_market.html"


class FinanceDataParser:
    def __init__(self):
        self._url = 'http://finance.naver.com/item/sise_day.nhn?code='
        self._start_date = '2017.01.01'
        self._dtype = {'names': ['date', 'open', 'high', 'low', 'close', 'volume'],
                       'formats': ['object', 'f4', 'f4', 'f4', 'f4', 'f4']}
        self._stock_items_dict = {'042660': '대우조선해양',
                                  '010140': '삼성중공업',
                                  '009540': '현대중공업',
                                  '096770': 'sk이노베이션',
                                  '010950': 'S오일',
                                  '051910': 'LG화학',
                                  '051900': 'LG생활건강',
                                  '090430': '아모레퍼시픽',
                                  '035420': '네이버',
                                  '035720': '카카오',
                                  '036570': 'ncsoft',
                                  '004020': '현대제철',
                                  '000660': 'sk하이닉스',
                                  '034730': 'SK',
                                  '017670': 'SKT',
                                  '030200': 'KT',
                                  '066570': 'LG전자',
                                  '032640': 'LG유플러스',
                                  '000150': '두산',
                                  '000880': '한화',
                                  '005380': '현대차',
                                  '000270': '기아차',
                                  '005930': '삼성전자',
                                  '008770': '호텔신라',
                                  '068270': '셀트리온',
                                  '068760': '셀트리온제약',
                                  '047810': '한국한공우주',
                                  '004800': '효성',
                                  '001040': 'CJ',
                                  '097950': 'CJ제일제당',
                                  '007310': '오뚜기',
                                  '069960': '현대백화점',
                                  '004170': '신세계',
                                  '055550': '신한지주',
                                  '105560': 'KB금융',
                                  '029780': '삼성카드',
                                  '024110': '기업은행',
                                  '139480': '이마트',
                                  '071840': '하이마트',
                                  '041510': 'sm엔터',
                                  '035900': 'JYP엔터',
                                  '034220': 'LG디스플레이',
                                  '009830': '한화케미칼',
                                  '003490': '대한항공',
                                  '020560': '아시아나항공'}

    def quotes_historical_finance(self, start_date=None):
        """
        parse historical finance data of the stock-items
         during the period from start-date to present
        :param start_date: start date parsing term
        :return: quotes ['date', 'open', 'high', 'low', 'close', 'volume']
        """
        items = self.get_stock_items()
        quotes = list()

        # get quote data of each company
        print('> parsing historical finance data')
        num = 0
        for item in items:
            print('\t- index_num : {step}.'.format(step=num), end='\t')
            num += 1
            print('fetching quote history of', end=' ')
            print('\"{stock_item}\"'.format(stock_item=self._stock_items_dict[item]))
            quote = self._retry(self._historical_finance)(item, start_date)
            quotes.append(quote)

        return np.array(quotes, dtype=self._dtype)

    def _historical_finance(self, stock_item, start_date=None):
        """
        parse historical finance data of the stock-item
         during the period from start-date to present
        :param stock_item: stock item id number
        :param start_date: start date parsing term
        :return: quote ['date', 'open', 'high', 'low', 'close', 'volume']
        """
        # set date info
        if start_date is None:
            start_date = self._start_date
        fmt = "%Y.%m.%d"
        start_date = datetime.strptime(start_date, fmt).date()

        # read data from the source
        url = self._url + str(stock_item)
        html = urlopen(url)
        source = BeautifulSoup(html.read(), "html.parser")

        # get max page number
        max_page = source.find_all("table", align="center")
        mp = max_page[0].find_all("td", class_="pgRR")
        mpNum = int(mp[0].a.get('href')[-3:])

        # parse selective data
        quote = list()
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        for page in range(1, mpNum + 1):
            url = self._url + str(stock_item) + '&page=' + str(page)
            html = urlopen(url)
            source = BeautifulSoup(html.read(), "html.parser")
            src_list = source.find_all("tr")

            for i in range(1, len(src_list) - 1):
                data_checker = src_list[i].span
                if data_checker is not None:
                    raw_date = src_list[i].find_all("td", align="center")[0].text
                    date = datetime.strptime(raw_date, fmt).date()
                    if not date >= start_date:
                        return quote

                    raw_close = src_list[i].find_all("td", class_="num")[0].text
                    close_p = float(locale.atof(raw_close))
                    raw_open = src_list[i].find_all("td", class_="num")[2].text
                    open_p = float(locale.atof(raw_open))
                    raw_high = src_list[i].find_all("td", class_="num")[3].text
                    high_p = float(locale.atof(raw_high))
                    raw_low = src_list[i].find_all("td", class_="num")[4].text
                    low_p = float(locale.atof(raw_low))
                    raw_volume = src_list[i].find_all("td", class_="num")[5].text
                    volume = float(locale.atof(raw_volume))

                    quote.append((date, open_p, high_p, low_p, close_p, volume))

    @staticmethod
    def _retry(f, n_attempts=3):
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

    def get_stock_names(self):
        _, names = np.array(sorted(self._stock_items_dict.items())).T
        return names


if __name__ == "__main__":
    pass

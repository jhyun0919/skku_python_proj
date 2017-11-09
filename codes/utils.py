from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime
import numpy as np
import pandas as pd
import locale
import plotly.graph_objs as go
from sklearn import cluster, covariance, manifold
from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt

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
                                  '036570': 'ncsoft'}

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


class DataDecorator:
    def __init__(self):
        pass

    @staticmethod
    def set_dataframe(idx, quotes):
        market_dates = np.vstack([q['date'] for q in quotes])
        open_prices = np.vstack([q['open'] for q in quotes])
        high_prices = np.vstack([q['high'] for q in quotes])
        low_prices = np.vstack([q['low'] for q in quotes])
        close_prices = np.vstack([q['close'] for q in quotes])
        volume = np.vstack([q['volume'] for q in quotes])

        data_dictionary = {'market_dates': list(market_dates[idx]),
                           'open_prices': list(open_prices[idx]),
                           'high_prices': list(high_prices[idx]),
                           'low_prices': list(low_prices[idx]),
                           'close_prices': list(close_prices[idx]),
                           'volume': list(volume[idx])}
        df = pd.DataFrame(data_dictionary)
        df = df.sort_values(by='market_dates')
        df = df.set_index('market_dates')

        return df

    @staticmethod
    def set_candelstick_data(df):
        trace = go.Candlestick(x=df.index,
                               open=df.open_prices,
                               high=df.high_prices,
                               low=df.low_prices,
                               close=df.close_prices)
        return [trace]

    @staticmethod
    def show_cluster(edge_model, embedding, names, n_labels, labels):
        # Visualization
        plt.figure(1, facecolor='w', figsize=(10, 8))
        plt.clf()
        ax = plt.axes([0., 0., 1., 1.])
        plt.axis('off')

        # Display a graph of the partial correlations
        partial_correlations = edge_model.precision_.copy()
        d = 1 / np.sqrt(np.diag(partial_correlations))
        partial_correlations *= d
        partial_correlations *= d[:, np.newaxis]
        non_zero = (np.abs(np.triu(partial_correlations, k=1)) > 0.02)

        # Plot the nodes using the coordinates of our embedding
        plt.scatter(embedding[0], embedding[1], s=100 * d ** 2, c=labels,
                    cmap=plt.cm.spectral)

        # Plot the edges
        start_idx, end_idx = np.where(non_zero)
        # a sequence of (*line0*, *line1*, *line2*), where::
        #            linen = (x0, y0), (x1, y1), ... (xm, ym)
        segments = [[embedding[:, start], embedding[:, stop]]
                    for start, stop in zip(start_idx, end_idx)]
        values = np.abs(partial_correlations[non_zero])
        lc = LineCollection(segments,
                            zorder=0, cmap=plt.cm.hot_r,
                            norm=plt.Normalize(0, .7 * values.max()))
        lc.set_array(values)
        lc.set_linewidths(15 * values)
        ax.add_collection(lc)

        # Add a label to each node. The challenge here is that we want to
        # position the labels to avoid overlap with other labels
        for index, (name, label, (x, y)) in enumerate(
                zip(names, labels, embedding.T)):

            dx = x - embedding[0]
            dx[index] = 1
            dy = y - embedding[1]
            dy[index] = 1
            this_dx = dx[np.argmin(np.abs(dy))]
            this_dy = dy[np.argmin(np.abs(dx))]
            if this_dx > 0:
                horizontalalignment = 'left'
                x = x + .002
            else:
                horizontalalignment = 'right'
                x = x - .002
            if this_dy > 0:
                verticalalignment = 'bottom'
                y = y + .002
            else:
                verticalalignment = 'top'
                y = y - .002
            plt.text(x, y, name, size=10,
                     horizontalalignment=horizontalalignment,
                     verticalalignment=verticalalignment,
                     bbox=dict(facecolor='w',
                               edgecolor=plt.cm.spectral(label / float(n_labels)),
                               alpha=.6))

        plt.xlim(embedding[0].min() - .15 * embedding[0].ptp(),
                 embedding[0].max() + .10 * embedding[0].ptp(), )
        plt.ylim(embedding[1].min() - .03 * embedding[1].ptp(),
                 embedding[1].max() + .03 * embedding[1].ptp())

        plt.show()


class Cluster:
    def __init__(self):
        pass

    @staticmethod
    def affinity(quotes):
        # the daily variations of the quotes
        open_prices = np.vstack([q['open'] for q in quotes])
        close_prices = np.vstack([q['close'] for q in quotes])
        variation = close_prices - open_prices
        # the names
        names = FinanceDataParser().get_names()

        # Learn a graphical structure from the correlations
        edge_model = covariance.GraphLassoCV()
        # standardize the time series: using correlations rather than covariance
        # is more efficient for structure recovery
        X = variation.copy().T
        X /= X.std(axis=0)
        edge_model.fit(X)

        # Cluster using affinity propagation
        _, labels = cluster.affinity_propagation(edge_model.covariance_)
        n_labels = labels.max()
        for i in range(n_labels + 1):
            print('Cluster %i: %s' % ((i + 1), ', '.join(names[labels == i])))

        # the nodes (the stocks) on a 2D plane

        # We use a dense eigen_solver to achieve reproducibility (arpack is
        # initiated with random vectors that we don't control). In addition, we
        # use a large number of neighbors to capture the large-scale structure.
        node_position_model = manifold.LocallyLinearEmbedding(n_components=2,
                                                              eigen_solver='dense',
                                                              n_neighbors=6)

        embedding = node_position_model.fit_transform(X.T).T

        return edge_model, embedding, names, n_labels, labels


if __name__ == "__main__":
    parser = FinanceDataParser()
    print(parser.quotes_historical_finance())

import pandas as pd
import numpy as np
import plotly.graph_objs as go
from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt
import matplotlib

__author__ = "Park Jee Hyun"
__copyright__ = "N.A."
__credits__ = ["Park Jee Hyun"]
__license__ = "BSD 3 clause"
__version__ = "1.0.2"
__maintainer__ = "Park Jee Hyun"
__email__ = "jhyun19@gmail.com"
__status__ = "Production"


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
        df = df[['close_prices', 'open_prices', 'high_prices', 'low_prices', 'volume']]

        return df

    @staticmethod
    def set_candelstick_data(df, name, stock_item):
        trace = go.Candlestick(x=df.index,
                               open=df.open_prices,
                               high=df.high_prices,
                               low=df.low_prices,
                               close=df.close_prices)

        layout = go.Layout(
            title=name + ' : ' + stock_item
        )
        data = [trace]

        return go.Figure(data=data, layout=layout)

    @staticmethod
    def show_cluster(edge_model, embedding, names, n_labels, labels):
        matplotlib.rc('font', family="AppleGothic")
        # Visualization
        plt.figure(1, facecolor='w', figsize=(13, 10))
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
        for index, (name, label, (x, y)) in enumerate(zip(names, labels, embedding.T)):
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


if __name__ == "__main__":
    pass

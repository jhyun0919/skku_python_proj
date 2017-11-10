import numpy as np
from sklearn import cluster, covariance, manifold
from financeDataParser import FinanceDataParser

__author__ = "Park Jee Hyun"
__copyright__ = "N.A."
__credits__ = ["Park Jee Hyun"]
__license__ = "BSD 3 clause"
__version__ = "1.0.2"
__maintainer__ = "Park Jee Hyun"
__email__ = "jhyun19@gmail.com"
__status__ = "Production"


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
        names = FinanceDataParser().get_stock_names()

        # learn a graphical structure from the correlations
        edge_model = covariance.GraphLassoCV()
        X = variation.copy().T
        X /= X.std(axis=0)
        edge_model.fit(X)

        # cluster using affinity propagation
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
    pass

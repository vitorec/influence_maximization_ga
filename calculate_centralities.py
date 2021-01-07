import argparse
import os

import igraph as ig
import numpy as np
import pandas as pd
from sklearn import preprocessing

from utils import load, parse_file_path

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


def main():
	parser = argparse.ArgumentParser(description='Calculate the centralities of the network')
	parser.add_argument('-n', '--network', type=str, required=True, help='The network file path')

	args = parser.parse_args()
	network = args.network
	print(network)
	path, name, extension, uri = parse_file_path(network)

	centralities_path = 'centralities/'
	g = None
	try:
		if extension == 'pkl':
			g = load(network)
		else:
			g = ig.Graph.Read_GML(network)
	except IOError as error:
		print('Cannot load the file ' + network)
		print(error)
		exit()

	ig.summary(g)
	print('---------------------')

	directed = g.is_directed()

	df = pd.DataFrame()
	scaler = preprocessing.MinMaxScaler()

	print('grau')
	degree = np.array(g.degree())
	scaled = scaler.fit_transform(degree.reshape(-1, 1))
	df['degree'] = scaled.reshape(1, -1)[0]

	print('eigenvector')
	eigenvector = np.array(g.evcent(directed=directed, scale=True))
	scaled = scaler.fit_transform(eigenvector.reshape(-1, 1))
	df['eigenvector'] = scaled.reshape(1, -1)[0]

	print('pagerank')
	pagerank = np.array(g.pagerank(directed=directed))
	scaled = scaler.fit_transform(pagerank.reshape(-1, 1))
	df['pagerank'] = scaled.reshape(1, -1)[0]

	print('betweenness')
	betweenness = np.array(g.betweenness(directed=directed))
	scaled = scaler.fit_transform(betweenness.reshape(-1, 1))
	df['betweenness'] = scaled.reshape(1, -1)[0]

	print('closeness')
	closeness = np.array(g.closeness(normalized=True))
	scaled = scaler.fit_transform(closeness.reshape(-1, 1))
	df['closeness'] = scaled.reshape(1, -1)[0]

	print(df.describe())
	df.to_pickle(centralities_path + name + '.pkl',  compression='xz', protocol=-1)


if __name__ == "__main__":
	main()

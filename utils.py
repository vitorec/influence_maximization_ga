import bz2
import os
import pickle
from functools import reduce
from os import sep as separator
from typing import Any

import leidenalg as la
from igraph import Graph, VertexClustering
from pandas import DataFrame


def parse_file_path(filepath: str) -> tuple:
	path = os.path.dirname(filepath).replace('/', separator)
	name = os.path.basename(filepath).rsplit('.', 1)[0]
	extension = filepath.rsplit('.', 1)[1]
	uri = path + separator + name
	return path, name, extension, uri


def get_neighbors(g: Graph, seeds: list, in_seeds: bool = False, distance: int = 1) -> list:
	"""
	Find the neighbors of a list of nodes

	:param g: A graph instance from igraph
	:type g: Graph
	:param seeds: A list of nodes on which the neighbors is found
	:type seeds: list
	:param in_seeds: Whether to consider the neighbors already in `seeds` (default: False)
	:type in_seeds: bool
	:param distance: The neighborhood distance (default: 1)
	:type distance: int

	:returns nb: List of neighbors of all nodes in `seeds`
	:rtype nb: list
	"""
	neighborhood = g.neighborhood(seeds, mindist=distance)
	nb_set = set(reduce(lambda x, y: x + y, neighborhood))
	if not in_seeds:
		nb_set = list(nb_set - set(seeds))
	nb = sorted(list(nb_set))
	return nb


def reverse_edges(g: Graph):
	"""
	Reverse the edges direction inplace on a directed graph

	:param g: A graph instance from igraph
	:type g: Graph
	"""

	edges = []
	attrs = {key: [] for key in g.es.attributes()}
	for e in g.es:
		edges.append((e.target, e.source))
		for key, value in e.attributes().items():
			attrs[key].append(value)
	g.delete_edges(None)
	g.add_edges(edges)
	for key, value in attrs.items():
		g.es[key] = value


def community_newman(g: Graph):
	"""
	Find the communities partition of the graph using the Newman algorithm

	:param g: A graph instance from igraph
	:type g: Graph

	:returns communities: A vertex clustering element containing the communities
	:rtype communities: VertexClustering
	"""
	communities = la.find_partition(g, la.ModularityVertexPartition)
	improv = 1
	optimiser = la.Optimiser()
	while improv > 0:
		improv = optimiser.optimise_partition(communities)
	return communities


def load_communities(g: Graph, attr: str):
	"""
	Load the communities of the graph by an attribute assigned to the nodes

	:param g: A graph instance from igraph
	:type g: Graph
	:param attr: The name of the attribute assigned to the community id
	:type attr: str

	:returns communities: A vertex clustering element containing the communities
	:rtype communities: VertexClustering
	"""
	if attr not in g.vs.attributes():
		return None
	print('Loading partitions by {} attribute...'.format(attr))
	partition = []
	for v in g.vs:
		partition.append(int(v[attr]))
	communities = VertexClustering(g, membership=partition)
	communities.recalculate_modularity()
	return communities


def create_indices_matrix(frame: DataFrame):
	"""
	Generate a dataframe containing the indices of the sorted values from the original dataframe

	:param frame: The name
	:type frame: Dataframe

	:returns df: The dataframe of indices
	"""
	df = DataFrame(columns=frame.columns)
	for column in frame.columns:
		indices = frame[column].to_numpy().argsort()[::-1]
		df[column] = indices
	return df


def save(filename: str, obj: Any):
	"""
	Save an object using pickle

	:param filename: The name
	:type filename: str
	:param obj: The object to save
	:type obj: Any

	:raises IOError: If the file cannot be written
	"""

	try:
		f = bz2.BZ2File(filename, 'wb')
		pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
		f.close()
		print('File written successfuly\n')
	except IOError as error:
		print('File ' + filename + ' cannot be written')
		print(error)


def load(filename: str):
	"""
	Load an object from filename using pickle

	:param filename: The name of file to load from
	:type filename: str

	:returns obj: The loaded object
	:rtype obj: Any

	:raises IOError
	"""

	try:
		f = bz2.BZ2File(filename, 'rb')
		obj = pickle.load(f)
		f.close()
		print('Object loaded successfully\n')
		return obj
	except IOError as error:
		print('File ' + filename + ' cannot be read\n')
		print(error)
		exit()


import random

import igraph as ig
import numpy as np
import pandas as pd


def icm(graph, seeds, p):
	"""
	Calculate the spreading through Independent Cascade Model

	:param graph: A igraph graph
	:param seeds: The set of initial active nodes
	:param p: The activation probability

	:return: The indexes of activated nodes
	"""
	g = graph.copy()
	activations = set(seeds)
	activated = set(seeds)

	while len(activated) > 0:
		new_activated = set()
		for v in activated:
			for u in set(g.neighbors(v, mode=ig.OUT)) - activations:
				prob = random.random()
				if p >= prob:
					new_activated.add(u)
		activated = set(new_activated)
		activations |= activated

	return activations


def ltm(graph, seeds):
	"""
	Calculate the spreading through Linear Threshold Model

	:param graph: A igraph graph
	:param seeds: The set of initial active nodes

	:return: The indexes of activated nodes
	"""
	g = graph.copy()
	prepare_graph(g)
	activations = set(seeds)
	new_activated = seeds
	threshold = g.vs['threshold']
	adj = np.array(g.get_adjlist())
	m = g.get_adjacency(attribute='weight')
	while len(new_activated) > 0:
		active_nodes = set()
		for i in adj[list(activations)]:
			active_nodes |= set(i) - activations
		inactivated = list(active_nodes)
		new_activated = []
		for v in inactivated:
			activated = np.array(list(activations | set(new_activated)))
			weights = [m[i:i + 1, v][0] for i in activated if m[i:i + 1, v][0] != 0]
			if sum(weights) >= threshold[v]:
				new_activated.append(v)
		activations |= set(new_activated)

	return activations


def calculate_spreading(g, seeds, model, config, p=0.01):
	"""

	:param g: An ig.Graph object
	:param seeds: The set of initial active nodes
	:param model: The diffusion model ('icm', 'ltm')
	:param config: Running configuration parameters (iterations, start, stop, step)
	:param p: The activation probability (used only when model is 'icm')

	:return The number of activated nodes of each
	"""
	iterations, start, stop, step = config
	length = len(seeds)

	activations = dict()
	for i in range(start, stop + 1, step):
		if i > length:
			break

		activations[i] = []
		for j in range(iterations):
			if model == 'icm':
				activated = icm(g, seeds[0:i], p)
			else:
				prepare_graph(g)
				activated = ltm(g, seeds[0:i])
			activations[i].append(len(activated))

	return activations


def prepare_graph(g, uniform_weights=True):
	"""
	Prepare the graph for run the Linear Threshold.
	A 'threshold' attribute is set for each node and a 'weight' attribute is
	set for each edge (u, v) incident in
	:param g:
	:param uniform_weights:
	"""
	if not g.is_directed():
		g.to_directed()

	# if 'threshold' not in g.vertex_attributes():
	g.vs['threshold'] = [random.uniform(0, 1) for _ in g.vs]

	if uniform_weights:
		for v in g.vs():
			edges = g.incident(v, mode=ig.IN)
			for e in edges:
				g.es[e]['weight'] = 1.0 / len(edges)




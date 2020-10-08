import random
from operator import itemgetter
from statistics import mean, stdev

import numpy as np

from diffusion import icm, ltm
from utils import get_occurrences


def calculate_fitness(g, seeds, model, iterations=10, p=0.01):
	"""
	Calculate the fitness for a set of seeds

	:param g: An ig.Graph object
	:param seeds: The set of initial active nodes
	:param model: The diffusion model ('icm', 'ltm')
	:param iterations: The number of iterations
	:param p: The activation probability (used only when model is 'icm')

	:return: The statistics of the diffusion (mean, min, max, standard deviation)
	"""
	if model == 'icm':
		influence_model = icm
		params = {'graph': g, 'seeds': seeds, 'p': p}
	elif model == 'ltm':
		influence_model = ltm
		params = {'graph': g, 'seeds': seeds}

	activations = []
	# Performs the IC or LT
	for i in range(iterations):
		fitness = influence_model(**params)
		activations.append(len(fitness))

	return mean(activations), min(activations), max(activations), stdev(activations)


def get_unranked_nodes(g, seeds=None):
	n = len(g.vs)
	d = g.degree()
	vindex = [i for i in range(n)]
	cut = np.percentile(d, 75)
	vertices = sorted(zip(vindex, d), key=lambda x: x[1], reverse=True)
	indices = [i[0] for i in vertices if i[1] >= cut]
	if seeds:
		indices = list(set(indices) - set(seeds))
	random.shuffle(indices)
	return indices


def replace_duplicates(chromossome, mapping, seeds, vertices):
	duplicates = [(idx, item) for idx, item in enumerate(chromossome) if item in chromossome[:idx]]
	used_seeds = [v for v in chromossome if v in seeds]
	used_vertices = [v for v in chromossome if v in vertices]
	seeds = list(set(seeds) - set(used_seeds))
	vertices = list(set(vertices) - set(used_vertices))
	for idx, v in duplicates:
		if mapping[idx] == 0:
			v = random.choice(vertices)
			vertices.remove(v)
		else:
			v = random.choice(seeds)
			seeds.remove(v)
		chromossome[idx] = v


def replace_gene(chromossome, idx, seeds, vertices):
	used_seeds = [v for v in chromossome if v in seeds]
	used_vertices = [v for v in chromossome if v in vertices]
	seeds = list(set(seeds) - set(used_seeds))
	vertices = list(set(vertices) - set(used_vertices))
	if chromossome.mapping[idx] == 0:
		if len(vertices) > 0:
			v = random.choice(vertices)
			vertices.remove(v)
		else:
			v = random.choice(seeds)
			seeds.remove(v)
	else:
		if len(seeds) > 0:
			v = random.choice(seeds)
			seeds.remove(v)
		else:
			v = random.choice(vertices)
			vertices.remove(v)
	chromossome[idx] = v


def fitness_eletism(population, ch1, ch2):
	fitness = [(idx, c.fit) for idx, c in enumerate(population.chromossomes)]
	new_individuals = sorted([(ch1.fit, ch1), (ch2.fit, ch2)], key=itemgetter(0))

	for fit, ch in new_individuals:
		if any(fit > f for idx, f in fitness):
			lowest = min(fitness, key=itemgetter(1))
			fitness.remove(min(fitness, key=itemgetter(1)))
			population.chromossomes[lowest[0]] = ch


def parents_eletism(population, ch1, ch2, idx1, idx2):
	population.chromossomes[idx1] = ch1
	population.chromossomes[idx2] = ch2


def edv(g, seeds, p):
	dv = len(seeds)
	occurrences = get_occurrences(g, seeds)
	for v, tau in occurrences.items():
		dv += 1 - (1 - p) ** tau
	return dv

import os
from collections import Counter
from functools import reduce
from os import sep as separator


def parse_file_path(filepath):
	path = os.path.dirname(filepath).replace('/', separator)
	name = os.path.basename(filepath).rsplit('.', 1)[0]
	extension = filepath.rsplit('.', 1)[1]
	uri = path + separator + name
	return path, name, extension, uri


def binary_search(item_list, item):
	first = 0
	last = len(item_list) - 1
	found = False
	while first <= last and not found:
		mid = (first + last) // 2
		if item_list[mid] == item:
			found = True
		else:
			if item < item_list[mid]:
				last = mid - 1
			else:
				first = mid + 1
	return found


def get_neighbors(g, seeds, in_seeds=False, distance=1):
	neighborhood = g.neighborhood(seeds, mindist=distance)
	nb_set = set(reduce(lambda x, y: x + y, neighborhood))
	if not in_seeds:
		nb_set = list(nb_set - set(seeds))
	nb = sorted(list(nb_set))
	return nb


def get_occurrences(g, seeds, in_seeds=False, distance=1):
	neighborhood = g.neighborhood(seeds, mindist=distance)
	c = Counter(x for xs in neighborhood for x in xs)
	if not in_seeds:
		for seed in seeds:
			if seed in c:
				c.pop(seed)
	occurrences = dict(sorted(c.items(), key=lambda i: i[0]))
	return occurrences

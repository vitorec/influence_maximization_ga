import argparse
import os
import time
from datetime import timedelta

import igraph as ig

from utils import parse_file_path, community_newman, reverse_edges, load, save

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


def main():
	parser = argparse.ArgumentParser(description='Network file preprocessing')
	parser.add_argument('-n', '--network', type=str, required=True, help='The network file path')
	parser.add_argument('-d', '--directed', action='store_true', help='Directed network')
	parser.add_argument('-r', '--reverse_edges', action='store_true', help='Reverses the direction of the edges')
	parser.add_argument('-o', '--output', type=str, choices=['gml', 'pkl'], default='', required=False, help='Specify the ou')

	args = parser.parse_args()
	network = args.network
	path, name, extension, uri = parse_file_path(network)

	print(network)
	try:
		extension = 'edgelist' if extension == 'txt' else extension
		if extension == 'pkl':
			g = load(network)
		else:
			g = ig.Graph.Read(network, format=extension)
		if not args.directed:
			g.to_undirected()
		if args.reverse_edges:
			print('Reversing graph edges...')
			reverse_edges(g)
	except IOError as error:
		print('Cannot load the file ' + network)
		print(error)
		exit()

	# Extract the giant component
	g = g.clusters(mode='WEAK').giant()
	g.simplify(combine_edges='sum')

	# Detect the communities of the graph
	start_time = time.perf_counter()
	partitions = community_newman(g)
	seconds = time.perf_counter() - start_time
	print('Execution time: {}\n'.format(timedelta(seconds=seconds)))

	# Assign id and name to the nodes
	g.vs['id'] = [i for i in range(len(g.vs))]
	g.vs['name'] = [i for i in range(len(g.vs))]

	# Assign the communities IDs to the nodes
	for i, community in enumerate(partitions.subgraphs()):
		for v in community.vs:
			g.vs.select(int(v['id']))['partition'] = i
	g['communities'] = len(partitions.subgraphs())

	ig.summary(g)
	if args.output == '' or 'gml' in args.output:
		g.write_gml(path + '/' + name + '.gml')
	if args.output == '' or 'pkl' in args.output:
		save(path + '/' + name + '.pkl', g)


if __name__ == "__main__":
	main()

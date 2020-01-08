import ga
from diffusion import *
from utils import parse_file_path

networks = [
	'datasets/karate.gml',
	'datasets/mis.gml',
	'datasets/soc-hamsterster.gml',
	'datasets/ego-facebook.gml',
	'datasets/CA-GrQc.gml',
	'datasets/CA-HepTh.gml',
	'datasets/CA-HepPh.gml',
	'datasets/CA-AstroPh.gml',
	'datasets/CA-CondMat.gml',
	'datasets/soc-gemsec-RO.gml',
	'datasets/soc-gemsec-HR.gml',
	'datasets/soc-facebook-wosn.gml',
	'datasets/livemocha.gml',
]

centralities_path = 'centralities/'
seeds_path = 'seeds/'

network = networks[2]

print(network)

path, name, extension, uri = parse_file_path(network)

g = ig.Graph.Read_GML(network)
ig.summary(g)

if 'id' in g.vs.attributes():
	g.vs['id'] = list(map(int, g.vs['id']))

print('---------------------')

n = len(g.vs)

genes = 50
population = 50

# porcentagem de sementes aleatorias
random_seeds = 0.6

# 'icm' ou 'ltm'
model = 'icm'

# iteracoes do modelo
it = 10

# modo de selecao:
# 'parents' -> elimina os pais apos o crossover e os filhos assumem seus lugares
# 'fitness' -> elimina os dois individuos de menor fitness na populacao
selection = 'parents'

# numero de geracoes
ngen = 10

# probabilidade de difusao
p = 0.01

# probabilidade de mutacao
pm = 0.05

# carregando as sementes
df = pd.read_pickle(seeds_path + name + '.pkl')

# colunas do Dataframe: '0_degree', '1_betweennes', '2_pagerank', '3_closeness', '4_eigenvector', '5_pca', 'random'
seeds = list(df['0_degree'][:genes])

ag = ga.GA()

# configurando o AG
ag.properties(g, seeds, genes, population, random_seeds, model=model, selection=selection, iterations=it, ngen=ngen, p=p, pm=pm)

# executando o AG para um conjunto de sementes
ag.run()




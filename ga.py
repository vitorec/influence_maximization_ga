from ga_helper import *


class Chromossome(list):

	def __init__(self, values=[], mapping=[], generation=1):
		super(Chromossome, self).__init__(values)
		self.fit = -1
		self.min = 0
		self.max = 0
		self.std = 0
		self.generation = generation
		self.mapping = mapping

	def calculate_fitness(self, g, model, iterations=10, p=0.01):
		fitness = calculate_fitness(g, self, model, iterations=iterations, p=p)
		self.fit = fitness[0]
		self.min = fitness[1]
		self.max = fitness[2]
		self.std = fitness[3]

	def __str__(self):
		fit, min, max, std = self.fit, self.min, self.max, self.std
		if self.__len__() <= 20:
			return '{:<20} {:^10} {:<10.2f} {:<10.2f} {:<10.2f} {:>6.3f} {:>10}'.format(super().__str__(), '->', fit, min, max, std, self.generation)
		return '{:<20} {:^10} {:<10.2f} {:<10.2f} {:<10.2f} {:>6.3f} {:>15}'.format(str(self[:7] + self[-7:]), '->', fit, min, max, std, self.generation)


class Population:

	def __init__(self):
		self.chromossomes = []

	def initialize(self, chromossomes):
		self.chromossomes = chromossomes

	def get_chromossome(self, index):
		return self.chromossomes[index]

	def calculate_fitness(self, g, model, iterations=10, p=0.01):
		for i, chromossome in enumerate(self.chromossomes):
			if self.chromossomes[i].fit == -1:
				fitness = calculate_fitness(g, chromossome, model, iterations=iterations, p=p)
				self.chromossomes[i].fit = fitness[0]
				self.chromossomes[i].min = fitness[1]
				self.chromossomes[i].max = fitness[2]
				self.chromossomes[i].std = fitness[3]

	def get_fitness(self, index=None):
		if index:
			return self.chromossomes[index].fit
		fitness = []
		for i, chromossome in enumerate(self.chromossomes):
			fitness.append((i, chromossome.fit))
		return fitness

	def set_fitness(self, index, fitness):
		self.chromossomes[index].fitness = fitness

	def show(self):
		print('----------------------- Population -----------------------')
		print('# {:<20} {:<10} {:>10} {:>10} {:>10} {:>10} {:>10}'.format('seeds', '->', 'mean', 'min', 'max', 'stddev', 'gen'))
		for i, chromossome in enumerate(self.chromossomes):
			print(i, chromossome)

	def statistics(self):
		fitness = [c.fit for c in self.chromossomes]
		best = max(fitness)
		worst = min(fitness)
		avg = mean(fitness)
		std = stdev(fitness)
		print('----------------------- Statistics -----------------------')
		print('{:<15} {:<15} {:<15} {:<15}'.format('max', 'min', 'mean', 'stddev'))
		print('{:<15.2f} {:<15.2f} {:<15.2f} {:<15.2f}'.format(best, worst, avg, std))
		print('----------------------------------------------------------')


class GA(object):

	def __init__(self):

		self.g = None
		self.n = 0
		self.p = 0.01
		self.pm = 0.05
		self.model = 'icm'
		self.iterations = 10
		self.population = Population()
		self.population_fitness = []
		self.bests = []
		self.best_individual = Chromossome()
		self.seeds = []
		self.reserved_seeds = []
		self.vertices = []
		self.genes = 5
		self.iterations = 10
		self.ngen = 50
		self.random_seeds = 0.0
		self.population_size = 50
		self.replacements = 0
		self.eletism_method = 'fitness'

	def initialize(self):
		"""
		Creates the initial population and shows it
		"""
		self.initial_population()
		self.evaluation()
		self.population.show()

	# set the details of this problem
	def properties(self, g, seeds, genes, population_size, random_seeds=0.6, model='icm', selection='fitness', iterations=10, ngen=50, p=0.01, pm=0.05):
		"""
		Initialize the properties of the GA.

		Parameters
		----------
			g (ig.Graph) : An igraph graph object
			seeds (list of int) : The list of seeds
			genes (int) : The number of genes (the size of each chromossome)
			population_size (int) : The size of the population
			random_seeds (float) : The proportion of random seeds
			model (str) : The diffusion model ('icm' or 'ltm')
			iterations (int) : The number of iterations of the model
			ngen (int) : The number of generations of the GA
			p (float) : The probability of diffusion (used only when model is 'icm')
			pm (float) : The probability of mutation
		"""

		self.g = g
		self.n = len(g.vs)
		self.model = model
		self.seeds = seeds
		self.genes = genes
		self.vertices = get_unranked_nodes(self.g, self.seeds)
		self.population_size = population_size
		self.random_seeds = random_seeds
		self.iterations = iterations
		self.eletism_method = selection
		self.ngen = ngen
		self.p = p
		self.pm = pm
		self.initialize()

	def initial_population(self):
		"""
		Creates the initial population.
		"""

		chromossomes = []
		population = Population()
		individuals = 0

		while individuals < self.population_size:
			chromossome = Chromossome()
			seeds = self.seeds[:]
			vertices = self.vertices[:]

			rand = 0
			seed = 0
			for j in range(self.genes):
				r = random.random()
				if r <= self.random_seeds:
					v = random.choice(vertices)
					vertices.remove(v)
					rand += 1
					chromossome.mapping.append(0)
				else:
					v = random.choice(seeds)
					seeds.remove(v)
					seed += 1
					chromossome.mapping.append(1)
				chromossome.append(v)
			if not self.has(chromossome):
				chromossomes.append(chromossome)
				individuals += 1
		population.initialize(chromossomes)
		self.population = population

	def fitness(self):
		"""
		Calculates the fitness of the entire population saving the best individual.
		"""

		self.population.calculate_fitness(self.g, self.model, iterations=self.iterations, p=self.p)
		self.population_fitness = self.population.get_fitness()
		best = max(self.population_fitness, key=itemgetter(1))
		self.bests.append(best[1])
		if best[1] > self.best_individual.fit:
			self.best_individual = self.population.chromossomes[best[0]]

	def evaluation(self):
		"""
		Calculates the inital fitness of the entire population
		"""

		self.population.calculate_fitness(self.g, self.model, iterations=self.iterations, p=self.p)
		self.population_fitness = self.population.get_fitness()
		best = max(self.population_fitness, key=itemgetter(1))
		self.bests.append(best[1])
		self.best_individual = self.population.chromossomes[best[0]]

	def mutation(self, ch: Chromossome):
		"""
		Performs the mutation on an individual by gene replacement

		Parameters
		----------
			ch (Chromossome) : An single individual
		"""

		for i in range(len(ch)):
			pm = random.uniform(0, 1)
			if pm <= self.pm:
				replace_gene(ch, i, self.seeds, self.vertices)

		return ch

	def crossover(self, parent1, parent2, generation):
		"""
		Performs the crossover of two individuals

		Args:
		----------
			parent1 (Chromossome) : An single individual
			parent2 (Chromossome) : An single individual

		Returns:
		----------
			c
		"""
		threshold = random.randint(1, self.genes - 1)

		ch1, ch2 = list(parent1), list(parent2)
		m1, m2 = parent1.mapping, parent2.mapping

		ch1[threshold:], ch2[threshold:] = ch2[threshold:], ch1[threshold:]
		m1[threshold:], m2[threshold:] = m2[threshold:], m1[threshold:]

		replace_duplicates(ch1, m1, self.seeds, self.vertices)
		replace_duplicates(ch2, m2, self.seeds, self.vertices)

		child1 = Chromossome(ch1)
		child2 = Chromossome(ch2)

		return child1, child2

	def parents_selection(self, k=2):
		"""
		Selects the best of the k individuals the be the next parents

		Args:
			k (int): the number of competitors

		Returns:
			parent1 (Chromossome): the first parent individual
			idx1 (Chromossome): the index of the first parent individual
			parent2 (Chromossome): the second parent individual
			idx2 (Chromossome): the index of the second parent individual
		"""

		candidates = self.population_fitness[:]
		competitors = random.sample(candidates, k)
		winner = max(competitors, key=itemgetter(1))
		parent1, idx1 = self.population.chromossomes[winner[0]], winner[0]
		candidates.remove(winner)

		competitors = random.sample(candidates, k)
		winner = max(competitors, key=itemgetter(1))
		parent2, idx2 = self.population.chromossomes[winner[0]], winner[0]
		return parent1, idx1, parent2, idx2

	def run(self):
		"""
		Run the GA and shows the results
		"""

		gen = 0
		while max(self.bests) < self.n and gen < self.ngen:
			gen += 1
			print("-- Generation %i --" % gen)

			parent1, idx1, parent2, idx2 = self.parents_selection(k=2)

			child1 = self.population.chromossomes[0]
			child2 = self.population.chromossomes[1]

			# avoid duplications of individuals in the population
			while self.has(child1) and self.has(child2):
				child1, child2 = self.crossover(parent1, parent2, gen)

				# mutation of the new individuals
				self.mutation(child1)
				self.mutation(child2)

				child1.calculate_fitness(self.g, self.model, self.iterations, self.p)
				child2.calculate_fitness(self.g, self.model, self.iterations, self.p)

			self.eletism(child1, child2, idx1, idx2)
			self.fitness()
			self.population.statistics()

		print('Final population')
		self.population.show()
		print('-------------------------\n')
		print('')
		print(list(set(self.bests)))
		print('-------------------------\n')
		print('Best individual')
		print('# {:<30} {:>40} {:>10} {:>10} {:>10} {:>10} {:>10}'.format('seeds', '->', 'mean', 'min', 'max', 'stddev', 'gen'))
		print(self.best_individual)

	def eletism(self, ch1, ch2, idx1=None, idx2=None):
		if self.eletism_method == 'fitness':
			fitness_eletism(self.population, ch1, ch2)
		else:
			parents_eletism(self.population, ch1, ch2, idx1=idx1, idx2=idx2)

	def has(self, ch):
		"""
		Check if the population has an individual

		Args:
			ch (list of int or Chromossome): The individual

		Returns:
			True if the population has ch
		"""
		return ch in self.population.chromossomes

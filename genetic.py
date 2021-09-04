from __future__ import annotations

from random import choice, randint, random, sample
from statistics import NormalDist
from typing import Callable, Optional, Tuple
from utils import clamp, grouper  # allow type hints without ''


class Gene:
    MIN = 0
    MAX = 1
    """A floating-point number in the range [0, 1)"""
    def __init__(self, value: Optional[float] = None):
        self.value: float = value or random()

    def copy(self) -> Gene:
        return Gene(self.value)


class Agent:
    """A collection of genes"""
    def __init__(self, genes: Optional[list[Gene]] = None):
        self.genes: list[Gene] = genes or []

    def copy(self) -> Agent:
        return Agent([g.copy() for g in self.genes])

    def __str__(self):
        genes = ', '.join([f'{g.value:.2f}' for g in self.genes])
        return f'Agent([{genes}])'


class GeneticAlgorithm:
    def __init__(self,
                 fitness_function: Callable[[Agent], float],
                 population: list[Agent],
                 mutation_chance: Optional[float] = None):
        if not population:
            raise ValueError("population is empty")
        if len(population) % 2 != 0:
            raise ValueError("population has an odd number of agents")

        self.fitness_function = fitness_function
        self.population = population
        self.mutation_chance = mutation_chance or 1 / len(population[0].genes)

    def run(self, iterations: int = 1) -> Tuple[Agent, float]:
        best = None
        for generation in range(iterations):
            population, scores = self.run_single_iteration()

            # get best performing agent from population
            agent, score = sorted(zip(population, scores), key = lambda x: x[1])[-1]
            if best == None or score > best[1]:
                best = (agent, score)
        return best


    def run_single_iteration(self) -> Tuple[list[Agent], list[float]]:
        scores = [fitness(c) for c in self.population]
        parents = [
            tournament_selection(self.population, scores)
            for _ in range(len(self.population))
        ]

        children = []  # next generation
        for p1, p2 in grouper(parents, 2):
            for child in crossover(p1, p2):
                self.mutate(child)
                children.append(child)

        # replace population
        prev_generation = self.population
        self.population = children

        return prev_generation, scores

    def mutate(self, child):
        for gene in child.genes:
            if random() < self.mutation_chance:
                mutate(child, gene)


def create_candiate():
    return Agent([random() for i in range(10)])



def tournament_selection(pop: list[Agent],
                         scores: list[float],
                         k=3) -> Agent:
    """
    Tournament selection algorithm. 
    Randomly pick k agents and return the best one as our winner.
    """
    # pick k agents from population
    selection = sample(list(zip(pop, scores)), k)
    # best one is our winner
    winner = sorted(selection, key=lambda c: c[1])[-1]
    return winner[0]


def crossover(p1: Agent,
              p2: Agent,
              cross_rate: float = 0.9) -> Tuple[Agent, Agent]:
    """
    Crossover two parents to create two children.
    The crossover rate cross_rate defines how often crossover is performed.
    """
    c1, c2 = p1.copy(), p2.copy()
    if random() < cross_rate:
        pt = randint(0, len(p1.genes))  # pick crossover point

        # swap all genes after the crossover point
        c1.genes[:pt], c2.genes[:pt] = c2.genes[:pt], c1.genes[:pt]
    return c1, c2


def mutate(agent: Agent, gene: Gene, reset_rate: float = 0.1):
    """
    Randomly mutate a gene.
    The reset_rate determines how often a gene is replaced with a completely
    random one. Otherwise the new gene is generated from the gauss
    distribution of the agent's genes.
    """
    if random() < reset_rate:
        gene.value = random()
    else:
        distribution = NormalDist.from_samples(g.value for g in agent.genes)
        gene.value = clamp(distribution.samples(1)[0])


def random_selection(pop: list[Agent]) -> Agent:
    """Random selection algorithm"""
    return choice(pop)

if __name__ == '__main__':

    def fitness(agent: Agent) -> float:
        middle = len(agent.genes) // 2
        genes = [g.value for g in agent.genes]
        lhs, rhs = genes[:middle], genes[middle:]
        return sum(lhs) - sum(rhs)
    simulation = GeneticAlgorithm(
        fitness, [Agent([Gene() for _ in range(10)]) for _ in range(50)]
    )

    iterations = 1
    while True:
        agent, score = simulation.run(iterations)
        print(f'High score: {score}\nAgent: {agent}')
        try:
            iterations = int(input('iterations?: '))
        except Exception:
            break
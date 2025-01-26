import random
import math
from models import CVRPInstance, CVRPSolution


class GeneticSolver:
    def __init__(self, instance: CVRPInstance, 
                 pop_size=50, 
                 elite_size=5,
                 mutation_rate=0.3,
                 generations=100):
        self.instance = instance
        self.pop_size = pop_size
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.generations = generations
        
    def solve(self) -> CVRPSolution:
        population = self._initialize_population()
        
        for _ in range(self.generations):
            population = self._evolve(population)
            
        return min(population, key=lambda x: x.cost())
    
    def _initialize_population(self) -> list:
        population = []
        # Генерация допустимых решений
        while len(population) < self.pop_size:
            if random.random() < 0.5:
                sol = self._greedy_initial()
            else:
                sol = self._random_initial()
            try:
                sol.validate()
                population.append(sol)
            except:
                continue
        return population
    
    def _greedy_initial(self) -> CVRPSolution:
        unvisited = [n for n in self.instance.demands if n != self.instance.depot]
        routes = []
        
        while unvisited:
            route = []
            current = self.instance.depot
            load = 0
            
            while True:
                candidates = [
                    n for n in unvisited 
                    if self.instance.demands[n] + load <= self.instance.capacity
                ]
                if not candidates:
                    break
                    
                # Find nearest candidate
                nearest = min(candidates, key=lambda x: 
                    math.hypot(
                        self.instance.coords[x][0] - self.instance.coords[current][0],
                        self.instance.coords[x][1] - self.instance.coords[current][1]
                    )
                )
                route.append(nearest)
                load += self.instance.demands[nearest]
                unvisited.remove(nearest)
                current = nearest
                
            if route:
                routes.append(route)
                
        return CVRPSolution(routes, self.instance)

    def _random_initial(self) -> CVRPSolution:
        nodes = [n for n in self.instance.demands if n != self.instance.depot]
        random.shuffle(nodes)
        
        routes = []
        current_route = []
        load = 0
        
        for node in nodes:
            demand = self.instance.demands[node]
            if load + demand > self.instance.capacity:
                routes.append(current_route)
                current_route = []
                load = 0
            current_route.append(node)
            load += demand
            
        if current_route:
            routes.append(current_route)
            
        return CVRPSolution(routes, self.instance)
    
    def _evolve(self, population: list) -> list:
        # Отбор
        fitness = [1/(s.cost()+1) for s in population]
        total_fitness = sum(fitness)
        probabilities = [f/total_fitness for f in fitness]
        
        # Элитизм
        elite = sorted(population, key=lambda x: x.cost())[:self.elite_size]
        
        # Скрещивание
        children = []
        while len(children) < self.pop_size - self.elite_size:
            parent1, parent2 = random.choices(population, weights=probabilities, k=2)
            child = self._crossover(parent1, parent2)
            child = self._mutate(child)
            try:
                child.validate()
                children.append(child)
            except:
                continue
                
        return elite + children
    
    def _crossover(self, parent1: CVRPSolution, parent2: CVRPSolution) -> CVRPSolution:
        # Упорядоченный кроссовер с проверкой
        flat1 = [n for route in parent1.routes for n in route]
        flat2 = [n for route in parent2.routes for n in route]
        
        start = random.randint(0, len(flat1)-2)
        end = random.randint(start+1, len(flat1)-1)
        segment = set(flat1[start:end])
        
        child = []
        for n in flat2:
            if n not in segment:
                child.append(n)
        child = flat1[start:end] + child
        
        return self._decode(child)
    
    def _mutate(self, solution: CVRPSolution) -> CVRPSolution:
        if random.random() > self.mutation_rate:
            return solution
            
        # Безопасные мутации
        for _ in range(10):  # Максимум 10 попыток
            mutator = random.choice([self._swap_mutation, self._reverse_mutation])
            mutated = mutator(solution.copy())
            try:
                mutated.validate()
                return mutated
            except:
                continue
        return solution
    
    def _swap_mutation(self, solution: CVRPSolution) -> CVRPSolution:
        # Обмен с проверкой грузоподъемности
        routes = [r.copy() for r in solution.routes if r]
        if len(routes) < 2:
            return solution
            
        r1_idx, r2_idx = random.sample(range(len(routes)), 2)
        r1 = routes[r1_idx]
        r2 = routes[r2_idx]
        
        if not r1 or not r2:
            return solution
        
        i = random.randint(0, len(r1)-1)
        j = random.randint(0, len(r2)-1)
        
        # Проверка грузоподъемности
        new_load_r1 = sum(self.instance.demands[n] for n in r1) - self.instance.demands[r1[i]] + self.instance.demands[r2[j]]
        new_load_r2 = sum(self.instance.demands[n] for n in r2) - self.instance.demands[r2[j]] + self.instance.demands[r1[i]]
        
        if new_load_r1 <= self.instance.capacity and new_load_r2 <= self.instance.capacity:
            r1[i], r2[j] = r2[j], r1[i]
            
        return CVRPSolution(routes, self.instance)
    
    def _reverse_mutation(self, solution: CVRPSolution) -> CVRPSolution:
        # Реверсирование сегмента
        routes = [r.copy() for r in solution.routes]
        route = random.choice(routes)
        if len(route) < 2:
            return solution
            
        i = random.randint(0, len(route)-2)
        j = random.randint(i+1, len(route)-1)
        route[i:j+1] = reversed(route[i:j+1])
        
        return CVRPSolution(routes, self.instance)
    
    def _decode(self, chromosome: list) -> CVRPSolution:
        # Декодирование с гарантией допустимости
        routes = []
        current_route = []
        load = 0
        
        for node in chromosome:
            demand = self.instance.demands[node]
            if load + demand > self.instance.capacity:
                routes.append(current_route)
                current_route = []
                load = 0
            current_route.append(node)
            load += demand
            
        if current_route:
            routes.append(current_route)
            
        return CVRPSolution(routes, self.instance)
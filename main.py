from models import CVRPInstance
from genetic import GeneticSolver
import time
import os


def read_sol(name: str) -> int:
    with open(f'{name}.sol', 'r') as f:
        data = f.readlines()
        for s in data:
            if 'Cost' in s:
                return int(s[5:])


def main():
    pth = './Data/P'
    files = os.listdir(pth)
    mean = 0
    for file in files:
        if file[0] == '.' or file[-3:] == 'sol':
            continue

        cost = read_sol(os.path.join(pth, file[:-4]))

        instance = CVRPInstance(os.path.join(pth, file))
        
        start_time = time.time()
        solver = GeneticSolver(instance, 
                            pop_size=75,
                            elite_size=10,
                            mutation_rate=0.19,
                            generations=10000)
        solution = solver.solve()
        
        print(f"Time: {time.time()-start_time:.2f}s")
        print(f"Best cost: {solution.cost():.2f}")
        d = (solution.cost()-cost)/cost*100
        print(f"Optimal: {cost} → Deviation: {d:.2f}%")
        mean += d
    print(f"Mean: {mean/(len(files) / 2)}")
if __name__ == "__main__":
    main()
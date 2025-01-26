import math
import random
from typing import List, Dict, Tuple

class CVRPInstance:
    def __init__(self, file_path: str):
        self.name = ""
        self.dimension = 0
        self.capacity = 0
        self.depot = 0
        self.coords: Dict[int, Tuple[float, float]] = {}
        self.demands: Dict[int, int] = {}
        
        with open(file_path, 'r') as f:
            section = None
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith("NAME"):
                    self.name = line.split(":")[1].strip()
                elif line.startswith("DIMENSION"):
                    self.dimension = int(line.split(":")[1].strip())
                elif line.startswith("CAPACITY"):
                    self.capacity = int(line.split(":")[1].strip())
                elif line.startswith("NODE_COORD_SECTION"):
                    section = "COORDS"
                elif line.startswith("DEMAND_SECTION"):
                    section = "DEMANDS"
                elif line.startswith("DEPOT_SECTION"):
                    section = "DEPOT"
                elif line == "EOF":
                    break
                else:
                    if section == "COORDS":
                        parts = line.split()
                        node = int(parts[0])
                        x, y = map(float, parts[1:])
                        self.coords[node] = (x, y)
                    elif section == "DEMANDS":
                        parts = line.split()
                        node = int(parts[0])
                        demand = int(parts[1])
                        self.demands[node] = demand
                    elif section == "DEPOT":
                        if line != "-1":
                            self.depot = int(line.strip())

class CVRPSolution:
    def __init__(self, routes: List[List[int]], instance: CVRPInstance):
        self.routes = [r for r in routes if r]
        self.instance = instance
        self._cost = None
        
    def validate(self):
        all_nodes = []
        for route in self.routes:
            if sum(self.instance.demands[n] for n in route) > self.instance.capacity:
                raise ValueError(f"Overloaded route: {route}")
            all_nodes.extend(route)
            
        expected = set(self.instance.demands.keys()) - {self.instance.depot}
        if set(all_nodes) != expected:
            missing = expected - set(all_nodes)
            raise ValueError(f"Missing nodes: {missing}")
    
    def cost(self) -> float:
        if self._cost is None:
            self.validate()
            total = 0.0
            depot = self.instance.depot
            for route in self.routes:
                current = depot
                for node in route:
                    dx = self.instance.coords[node][0] - self.instance.coords[current][0]
                    dy = self.instance.coords[node][1] - self.instance.coords[current][1]
                    total += math.hypot(dx, dy)
                    current = node
                # Return to depot
                dx = self.instance.coords[depot][0] - self.instance.coords[current][0]
                dy = self.instance.coords[depot][1] - self.instance.coords[current][1]
                total += math.hypot(dx, dy)
            self._cost = total
        return self._cost
    
    def copy(self):
        return CVRPSolution([r.copy() for r in self.routes], self.instance)

import json
import math
import random
import numpy as np

# --- CONFIGURATION ---
POPULATION_SIZE = 20
MAX_ITERATIONS = 50
ALPHA = 0.5  # Contraction-Expansion Coefficient for QPSO

def load_amplitudes():
    with open("tca.json", "r") as f:
        return json.load(f)

def interference_aware_fitness(permutation_indices, test_cases):
    """
    Calculates fitness of a test ordering.
    Models 'Wave Function Collapse':
    - When a test is executed, it 'observes' (resolves) risk at a specific phase.
    - Subsequent tests with similar phases contribute less value (Destructive Interference).
    """
    total_fitness = 0.0
    covered_phases = [] # List of (magnitude, phase) tuples already executed
    
    # We weight earlier tests higher (APFD-like time decay)
    # Position weight: 1.0 for first test, decreasing...
    n = len(permutation_indices)
    
    for rank, idx in enumerate(permutation_indices):
        test = test_cases[idx]
        mag = test['magnitude']
        phase = test['phase']
        
        # Calculate Interference Factor
        # If current phase is close to ANY covered phase, reduce effective magnitude
        interference_penalty = 0.0
        if mag > 0:
            for cov_mag, cov_phase in covered_phases:
                # Phase difference
                delta_theta = abs(phase - cov_phase)
                # Cosine similarity: 1 if identical angle, 0 if orthogonal
                similarity = max(0, math.cos(delta_theta))
                
                # Penalty is proportional to how much 'energy' was already covered at this angle
                interference_penalty += similarity * cov_mag

        # Effective Magnitude (cannot be negative)
        effective_mag = max(0, mag - (interference_penalty * 0.5))
        
        # Weighted score based on position (Early detection is better)
        position_weight = (n - rank) / n
        
        total_fitness += effective_mag * position_weight
        
        # "Collapse" - Add this test's state to history
        covered_phases.append((mag, phase))
        
    return total_fitness

class QPSO:
    def __init__(self, test_cases):
        self.test_cases = test_cases
        self.dim = len(test_cases)
        self.pop_size = POPULATION_SIZE
        
        # Initialize Particles (Continuous representation of permutations)
        # X ranges [0, dim]
        self.X = np.random.uniform(0, self.dim, (self.pop_size, self.dim))
        
        # Personal Best (Pbest)
        self.Pbest = self.X.copy()
        self.Pbest_fitness = np.zeros(self.pop_size)
        
        # Global Best (Gbest)
        self.Gbest = np.zeros(self.dim)
        self.Gbest_fitness = -1.0

    def get_permutation(self, position_vector):
        # SPV (Smallest Position Value) rule to convert continuous -> discrete
        # Argsort returns the indices that would sort the array
        return np.argsort(position_vector)

    def optimize(self):
        # Evaluate initial population
        for i in range(self.pop_size):
            perm = self.get_permutation(self.X[i])
            fit = interference_aware_fitness(perm, self.test_cases)
            self.Pbest_fitness[i] = fit
            
            if fit > self.Gbest_fitness:
                self.Gbest_fitness = fit
                self.Gbest = self.X[i].copy()
        
        # Main Loop
        for t in range(MAX_ITERATIONS):
            # Mean Best Position (mbest)
            mbest = np.mean(self.Pbest, axis=0)
            
            for i in range(self.pop_size):
                # QPSO Update Equation
                phi = np.random.rand(self.dim)
                # p_i is local attractor
                p = (phi * self.Pbest[i] + (1 - phi) * self.Gbest)
                
                u = np.random.rand(self.dim)
                
                # Characteristic length L
                L = ALPHA * np.abs(mbest - self.X[i])
                
                # Update position
                # X(t+1) = p +/- L * ln(1/u)
                sign = np.where(np.random.rand(self.dim) > 0.5, 1, -1)
                self.X[i] = p + sign * L * np.log(1 / u)
                
                # Boundary handling (optional, but good for stability)
                self.X[i] = np.clip(self.X[i], 0, self.dim)
                
                # Evaluation
                perm = self.get_permutation(self.X[i])
                fit = interference_aware_fitness(perm, self.test_cases)
                
                if fit > self.Pbest_fitness[i]:
                    self.Pbest_fitness[i] = fit
                    self.Pbest[i] = self.X[i].copy()
                    
                    if fit > self.Gbest_fitness:
                        self.Gbest_fitness = fit
                        self.Gbest = self.X[i].copy()

        return self.get_permutation(self.Gbest)

def generate_report(ordered_indices, test_cases):
    report = "# QI-PSO Test Case Prioritization Results\n\n"
    report += "| Priority | Test Case ID | Magnitude | Phase (rad) | Semantics |\n"
    report += "|---|---|---|---|---|\n"
    
    for rank, idx in enumerate(ordered_indices):
        t = test_cases[idx]
        report += f"| {rank+1} | {t['test_id']} | {t['magnitude']} | {t['phase']} | {t['original_semantics']} |\n"
    
    report += "\n\n**Algorithm Stats:**\n"
    report += f"- Population: {POPULATION_SIZE}\n"
    report += f"- Iterations: {MAX_ITERATIONS}\n"
    
    with open("prioritization_report.md", "w") as f:
        f.write(report)

def main():
    try:
        test_cases = load_amplitudes()
    except FileNotFoundError:
        print("tca.json not found.")
        return
        
    if not test_cases:
        print("No test cases found in tca.json")
        return

    print(f"Starting QI-PSO optimization for {len(test_cases)} test cases...")
    
    optimizer = QPSO(test_cases)
    best_order_indices = optimizer.optimize()
    
    generate_report(best_order_indices, test_cases)
    print("Optimization complete. Report generated: prioritization_report.md")

if __name__ == "__main__":
    main()
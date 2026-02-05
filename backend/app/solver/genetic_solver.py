
import random
from typing import List, Dict, Any
from .constraints.base import HardConstraints, SoftConstraints
from ..domain.entities.all_entities import Teacher, Subject, Room, ClassGroup, TimeSlot

class GeneticTimetableSolver:
    def __init__(self, teachers, subjects, rooms, groups, slots, 
                 pop_size=50, generations=100, mutation_rate=0.1):
        self.teachers = teachers
        self.subjects = subjects
        self.rooms = rooms
        self.groups = groups
        self.slots = [s for s in slots if not s.is_break]
        self.pop_size = pop_size
        self.generations = generations
        self.mutation_rate = mutation_rate

    def _generate_random_individual(self) -> List[Dict]:
        individual = []
        for g in self.groups:
            for s in self.subjects:
                # Basic assignment
                slot = random.choice(self.slots)
                valid_rooms = [r for r in self.rooms if r.type == s.required_room_type]
                room = random.choice(valid_rooms) if valid_rooms else self.rooms[0]
                
                individual.append({
                    "class_group_id": g.id,
                    "subject_id": s.id,
                    "room_id": room.id,
                    "time_slot_id": slot.id,
                    "teacher_id": s.teacher_id
                })
        return individual

    def _fitness(self, individual: List[Dict]) -> float:
        score = 10000.0
        
        # 1. Hard Constraints (Severe Penalties)
        h_conflicts = HardConstraints.check_teacher_overlap(individual)
        h_conflicts += HardConstraints.check_room_overlap(individual)
        h_conflicts += HardConstraints.check_room_capacity(individual, self.groups, self.rooms)
        
        score -= len(h_conflicts) * 1000
        
        # 2. Soft Constraints (Minor Penalties)
        soft_penalty = SoftConstraints.total_soft_score(individual, self.teachers, self.slots)
        score -= soft_penalty
        
        return max(0.0, score)

    def solve(self) -> List[Dict]:
        population = [self._generate_random_individual() for _ in range(self.pop_size)]
        
        for gen in range(self.generations):
            # Sort by fitness
            population.sort(key=lambda x: self._fitness(x), reverse=True)
            
            if self._fitness(population[0]) >= 10000: # Found a valid one with no soft penalty
                 break
                 
            # Evolve
            new_population = population[:2] # Elitism
            
            while len(new_population) < self.pop_size:
                # Selection
                parent1 = self._tournament_selection(population)
                parent2 = self._tournament_selection(population)
                
                # Crossover
                child = self._crossover(parent1, parent2)
                
                # Mutation
                if random.random() < self.mutation_rate:
                    child = self._mutate(child)
                
                new_population.append(child)
            
            population = new_population
            
        return population[0]

    def _tournament_selection(self, population):
        subset = random.sample(population, 3)
        return max(subset, key=lambda x: self._fitness(x))

    def _crossover(self, p1, p2):
        point = random.randint(0, len(p1)-1)
        return p1[:point] + p2[point:]

    def _mutate(self, ind):
        idx = random.randint(0, len(ind)-1)
        # Mutate time or room
        ind[idx]['time_slot_id'] = random.choice(self.slots).id
        return ind

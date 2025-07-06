import sys
import math
import numpy as np
import matplotlib.pyplot as plt

# Reproduction
REPRODUCE_PREY_PROB = 0.05
REPRODUCE_PRED_PROB = 0.03

# Cohesion/Avoidance
SAME_SPECIES_AVOIDANCE_RADIUS = 0.035
PREY_GROUP_COHESION_RADIUS = 0.2

# Predator/Prey/Grass interaction
PRED_PREY_INTERACTION_RADIUS = 0.3
PRED_SPEED_ADVANTAGE = 3.0
PRED_KILL_DISTANCE = 0.03
GRASS_EAT_DISTANCE = 0.05
GAIN_FROM_FOOD_PREY = 80
GAIN_FROM_FOOD_PREDATOR = 100
GRASS_REGROW_CYCLES = 20
PRED_HUNGER_THRESH = 100
PREY_HUNGER_THRESH = 100

# Simulation properties
DELTA_TIME = 0.001
BOUNDS_WIDTH = 2.0
MIN_POSITION = -1.0
MAX_POSITION = 1.0

NEXT_PRED_ID = 1
NEXT_PREY_ID = 1

class Prey:
    def __init__(self):
        global NEXT_PREY_ID
        self.id = NEXT_PREY_ID
        NEXT_PREY_ID += 1
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.steer_x = 0.0
        self.steer_y = 0.0
        self.life = 0

    def avoid_predators(self, predator_list):
        # Reset this prey's steer force
        self.steer_x = 0.0
        self.steer_y = 0.0

        # Add a steering factor away from each predator. Strength increases with closeness.
        for predator in predator_list:
            # Fetch location of predator
            predator_x = self.x;
            predator_y = self.y;

            # Check if the two predators are within interaction radius
            dx = self.x - predator.x
            dy = self.y - predator.y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < PRED_PREY_INTERACTION_RADIUS:
                # Steer the prey away from the predator
                self.steer_x += (PRED_PREY_INTERACTION_RADIUS / distance) * dx
                self.steer_y += (PRED_PREY_INTERACTION_RADIUS / distance) * dy

    def flock(self, prey_list):
        group_centre_x = 0.0
        group_centre_y = 0.0
        group_velocity_x = 0.0
        group_velocity_y = 0.0
        avoid_velocity_x = 0.0
        avoid_velocity_y = 0.0
        group_centre_count = 0

        for other in prey_list:
            dx = self.x - other.x
            dy = self.y - other.y
            separation = math.sqrt(dx * dx + dy * dy)

            if separation < PREY_GROUP_COHESION_RADIUS and self.id != other.id:
                group_centre_x += other.x
                group_centre_y += other.y
                group_centre_count += 1

                # Avoidance behaviour
                if separation < SAME_SPECIES_AVOIDANCE_RADIUS and separation > 0:
                    # Was a check for separation > 0 in original - redundant?
                    avoid_velocity_x += SAME_SPECIES_AVOIDANCE_RADIUS / separation * dx
                    avoid_velocity_y += SAME_SPECIES_AVOIDANCE_RADIUS / separation * dy

        # Compute group centre as the average of the nearby prey positions and a velocity to move towards the group centre
        if group_centre_count > 0:
            group_centre_x /= group_centre_count
            group_centre_y /= group_centre_count
            group_velocity_x = group_centre_x - self.x
            group_velocity_y = group_centre_y - self.y

        self.steer_x += group_velocity_x + avoid_velocity_x
        self.steer_y += group_velocity_y + avoid_velocity_y

    def move(self):
        # Integrate steering forces and cap velocity
        self.vx += self.steer_x
        self.vy += self.steer_y

        speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
        if speed > 1.0:
            self.vx /= speed
            self.vy /= speed

        # Integrate velocity
        self.x += self.vx * DELTA_TIME
        self.y += self.vy * DELTA_TIME

        # Bound the position within the environment - can this be moved
        self.x = max(self.x, MIN_POSITION)
        self.x = min(self.x, MAX_POSITION)
        self.y = max(self.y, MIN_POSITION)
        self.y = min(self.y, MAX_POSITION)

        # Reduce life by one unit of energy
        self.life -= 1

    def eaten_or_starve(self, predator_list):
        predator_index = -1
        closest_pred = PRED_KILL_DISTANCE

        # Iterate predator_location messages to find the closest predator
        for i in range(len(predator_list)):
            predator = predator_list[i]
            if predator.life < PRED_HUNGER_THRESH:
                # Check if the two predators are within interaction radius
                dx = self.x - predator.x
                dy = self.y - predator.y
                distance = math.sqrt(dx * dx + dy * dy)

                if distance < closest_pred:
                    predator_index = i
                    closest_pred = distance

        if predator_index >= 0:
            predator_list[predator_index].life += GAIN_FROM_FOOD_PREDATOR
            return True
            
        # If the life has reduced to 0 then the prey should die or starvation 
        if self.life < 1:
            return True
        return False
        
    def reproduce(self):
        if np.random.uniform() < REPRODUCE_PREY_PROB:
            self.life /= 2
        
            child = Prey()
            child.x = np.random.uniform() * BOUNDS_WIDTH - BOUNDS_WIDTH / 2.0
            child.y = np.random.uniform() * BOUNDS_WIDTH - BOUNDS_WIDTH / 2.0
            child.vx = np.random.uniform() * 2 - 1
            child.vy = np.random.uniform() * 2 - 1
            child.life = self.life
        
    
class Predator:
    def __init__(self):
        global NEXT_PRED_ID
        self.id = NEXT_PRED_ID
        NEXT_PRED_ID += 1
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.steer_x = 0.0
        self.steer_y = 0.0
        self.life = 0
    
    def follow_prey(self, prey_list):
        # Find the closest prey by iterating the prey_location messages
        closest_prey_x = 0.0
        closest_prey_y = 0.0
        closest_prey_distance = PRED_PREY_INTERACTION_RADIUS
        is_a_prey_in_range = 0

        for prey in prey_list:
            # Check if prey is within sight range of predator
            dx = self.x - prey.x
            dy = self.y - prey.y
            separation = math.sqrt(dx * dx + dy * dy)

            if separation < closest_prey_distance:
                closest_prey_x = prey.x
                closest_prey_y = prey.y
                closest_prey_distance = separation
                is_a_prey_in_range = 1

        # If there was a prey in range, steer the predator towards it
        if is_a_prey_in_range:
            self.steer_x = closest_prey_x - self.x
            self.steer_y = closest_prey_y - self.y

        
    def avoid_predators(self, predator_list):
        # Fetch this predator's position
        avoid_velocity_x = 0.0
        avoid_velocity_y = 0.0

        # Add a steering factor away from each other predator. Strength increases with closeness.
        for other in predator_list:
            # Check if the two predators are within interaction radius
            dx = self.x - other.x
            dy = self.y - other.y
            separation = math.sqrt(dx * dx + dy * dy)

            if separation < SAME_SPECIES_AVOIDANCE_RADIUS and separation > 0.0 and self.id != other.id:
                avoid_velocity_x += SAME_SPECIES_AVOIDANCE_RADIUS / separation * dx
                avoid_velocity_y += SAME_SPECIES_AVOIDANCE_RADIUS / separation * dy

        self.steer_x += avoid_velocity_x
        self.steer_y += avoid_velocity_y
        
    def move(self):
        # Integrate steering forces and cap velocity
        self.vx += self.steer_x
        self.vy += self.steer_y

        speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
        if speed > 1.0:
            self.vx /= speed
            self.vy /= speed

        # Integrate velocity
        self.x += self.vx * DELTA_TIME * PRED_SPEED_ADVANTAGE
        self.y += self.vy * DELTA_TIME * PRED_SPEED_ADVANTAGE

        # Bound the position within the environment 
        self.x = max(self.x, MIN_POSITION)
        self.x = min(self.x, MAX_POSITION)
        self.y = max(self.y, MIN_POSITION)
        self.y = min(self.y, MAX_POSITION)

        # Reduce life by one unit of energy
        self.life -= 1
        
    def starve(self):
        # Did the predator starve?
        if self.life < 1:
            return True
        return False
        
    def reproduce(self):
        if np.random.uniform() < REPRODUCE_PRED_PROB:
            self.life /= 2

            child = Predator()
            child.x = np.random.uniform() * BOUNDS_WIDTH - BOUNDS_WIDTH / 2.0
            child.y = np.random.uniform() * BOUNDS_WIDTH - BOUNDS_WIDTH / 2.0
            child.vx = np.random.uniform() * 2 - 1
            child.vy = np.random.uniform() * 2 - 1
            child.life = self.life
            return child
        
class Grass:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.dead_cycles = 0
        self.available = 1
        
    def grow(self):
        new_dead_cycles = self.dead_cycles + 1
        if self.dead_cycles == GRASS_REGROW_CYCLES:
            self.dead_cycles = 0
            self.available = 1

        if self.available == 0:
            self.dead_cycles = new_dead_cycles

        
    def eaten(self, prey_list):
        if self.available:
            prey_index = -1
            closest_prey = GRASS_EAT_DISTANCE

            # Iterate prey_location messages to find the closest prey
            for i in range(len(prey_list)):
                prey = prey_list[i]
                if prey.life < PREY_HUNGER_THRESH:
                    # Check if they are within interaction radius
                    dx = self.x - prey.x
                    dy = self.y - prey.y
                    distance = math.sqrt(dx*dx + dy*dy)

                    if distance < closest_prey:
                        prey_index = i
                        closest_prey = distance

            if prey_index >= 0:
                # Add grass eaten message
                prey_list[prey_index].life += GAIN_FROM_FOOD_PREY
               
                # Update grass agent variables
                self.dead_cycles = 0
                self.available = 0
        
class Model:

    def __init__(self, steps = 250):
        self.steps = steps
        self.num_prey = 200
        self.num_predators = 50
        self.num_grass = 5000

    def _init_population(self):
        # Initialise prey agents
        self.prey = []
        for i in range(self.num_prey):
            p = Prey()
            p.x = np.random.uniform(-1.0, 1.0)
            p.y = np.random.uniform(-1.0, 1.0)
            p.vx = np.random.uniform(-1.0, 1.0)
            p.vy = np.random.uniform(-1.0, 1.0)
            p.life = np.random.randint(10, 50)
            self.prey.append(p)
      
        # Initialise predator agents
        self.predators = []
        for i in range(self.num_predators):
            p = Predator()
            p.x = np.random.uniform(-1.0, 1.0)
            p.y = np.random.uniform(-1.0, 1.0)
            p.vx = np.random.uniform(-1.0, 1.0)
            p.vy = np.random.uniform(-1.0, 1.0)
            p.life = np.random.randint(10, 15)
            self.predators.append(p)
        
        # Initialise grass agents
        self.grass = []
        for i in range(self.num_grass):
            g = Grass()
            g.x = np.random.uniform(-1.0, 1.0)
            g.y = np.random.uniform(-1.0, 1.0)
            self.grass.append(g)
    
    def _step(self):
        ## Shuffle agent list order to avoid bias
        np.random.shuffle(self.predators) # todo, this probably doesn't like Python lists
        np.random.shuffle(self.prey)
        
        for p in self.predators:
            p.follow_prey(self.prey)
        for p in self.prey:
            p.avoid_predators(self.predators)
                
        for p in self.prey:
            p.flock(self.prey)
        for p in self.predators:
            p.avoid_predators(self.predators)
        
        for p in self.prey:
            p.move()
        for p in self.predators:
            p.move()
            
            
        for g in self.grass:
            g.eaten(self.prey)
        
        self.prey = [p for p in self.prey if not p.eaten_or_starve(self.predators)]
        self.predators = [p for p in self.predators if not p.starve()]
                
        children = []
        for p in self.prey:
            c = p.reproduce()
            if c:
                children.append(c)
        self.predators.extend(children)
        children = []
        for p in self.predators:
            c = p.reproduce()
            if c:
                children.append(c)
        self.predators.extend(children)
        for g in self.grass:
            g.grow()
    
    def _init_log(self):
        self.prey_log = [len(self.prey)]
        self.predator_log = [len(self.predators)]
        self.grass_log = [sum(g.available for g in self.grass)/20]
        
    def _log(self):
        self.prey_log.append(len(self.prey))
        self.predator_log.append(len(self.predators))
        self.grass_log.append(sum(g.available for g in self.grass)/20)
    
    def _plot(self):
        plt.figure(figsize=(16,10))
        plt.rcParams.update({'font.size': 18})
        plt.xlabel("Step")
        plt.ylabel("Population")
        plt.plot(range(0, len(self.prey_log)), self.prey_log, 'b', label="Prey")
        plt.plot(range(0, len(self.predator_log)), self.predator_log, 'r', label="Predators")
        plt.plot(range(0, len(self.grass_log)), self.grass_log, 'g', label="Grass/20")
        plt.legend()
        plt.savefig('predprey_out.png')
    
    def run(self, random_seed=12):
        np.random.seed(random_seed)
        # init
        self._init_population()
        self._init_log()
        # execute
        for i in range(self.steps):
            self._step()
            self._log()
        # plot graph of results
        self._plot()
        
# Argument parsing
if len(sys.argv) != 2:
    print("Script expects 1 positive integer argument (number of steps), %u found."%(len(sys.argv) - 1))
    sys.exit(1)
steps = int(sys.argv[1])
if steps < 1:
    print("Script expects 1 positive integer argument (number of steps), %s converts < 1."%(sys.argv[1]))
    sys.exit(1)
        
model = Model(steps=steps)
model.run()
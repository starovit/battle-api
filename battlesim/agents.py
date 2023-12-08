import json
import copy
import random
import numpy as np
from mesa import Agent


class SoldierAgent(Agent):
    """An agent with fixed initial health."""

    def __init__(self, unique_id, params, model):
        
        super().__init__(unique_id, model)

        # general atributes
        self.status = "alive"
        
        self.fraction = params["fraction"] # ally / enemy
        self.type = params["type"] # soldier or mine-thrower
        
        # type specific atributes
        self._set_type_specific_attributes()
        
        # battle attributes
        self.last_aim = None
        self.last_heal = None
        
        # movement attributes
        self.movement = params["movement"] # [random, stay, route]
        self.route = params["route"]  # List of points (x, y) to visit
        self.route_index = 0  # Current target point index in the route
        self.steps_after_attack = 0  # Steps count after last attack
        
        # statistics attributes
        self.damaged = 0
        self.healed = 0
    
    def _set_type_specific_attributes(self):
        
        ATTRIBUTES = {
    "infantry": {
        "max_health": 100,
        "speed": 1,
        "damage": 10,
        "damage_range": 6,
        "damage_chance": 0.4
    },
    "medic": {
        "max_health": 70,
        "speed": 1,
        "damage": 5,
        "damage_range": 3,
        "damage_chance": 0.2,
        "special": {
            "healing": 5,
            "healing_chance": 0.8,
            "healing_range": 1,
            "steps_after_healing": 0
        }
    },
    "mortar": {
        "max_health": 30,
        "speed": 1,
        "damage_range": 99,
        "special": {
            "caliber": "projectile_120mm",
            "steps_after_shot": 25
        }
    },
    "projectile_120mm": {
        "max_health": 10,
        "speed": 10,
        "damage": 80,
        "damage_range": 1,
        "damage_chance": 0.05
    }
}
        type_attrs = copy.deepcopy(ATTRIBUTES[self.type])
        self.max_health = self.health = type_attrs.get("max_health", 100)
        self.speed = type_attrs.get("speed", 1)
        self.damage = type_attrs.get("damage", 0)
        self.damage_range = type_attrs.get("damage_range", 3)
        self.damage_chance = type_attrs.get("damage_chance", 0.5)
        self.special_attributes = type_attrs.get("special", dict())
        
    def kill_agent(self):
        self.health = 0
        self.status = "dead"   
        
    def step(self):
        if self.status == "dead":
            return
        if self.type == "medic":
            if not self.heal_wounded():
                self.attack()
        else:
            self.attack()
        for _ in range(self.speed):
            self.move()
    
    def _mortar_shoot(self, target_agent):
        if self.special_attributes["steps_after_shot"] < 30:
            self.special_attributes["steps_after_shot"] += 1
            return
        else:
            x, y = self.pos
            target_x, target_y = target_agent.pos
            params = dict(
                fraction = self.fraction,
                type = self.special_attributes["caliber"],
                movement = "route",
                route = [(x, y), (target_x, target_y)]
            )
            place_agents(model=self.model,
                         n_soldiers=1,
                         params=params,
                         pos=(x,y))
            self.steps_after_attack = 0
            self.special_attributes["steps_after_shot"] = 0
            return
         
    def attack(self):
        if self.last_aim is not None and self.last_aim.status != "dead":
            smart_attack(self, self.last_aim)
        else:
            range_positions = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=True,
                radius=self.damage_range) # get x,y in range N
    
            for position in range_positions: # get all agents in range
                result = self.model.grid.get_cell_list_contents([position])
                random.shuffle(result)
                for cellmate in result:
                    if cellmate.fraction != self.fraction and cellmate.status != "dead" and not cellmate.type.startswith("projectile_"): # check if enemy
                        if self.type == "mortar":
                            self._mortar_shoot(cellmate)
                        else:
                            smart_attack(self, cellmate)
                        break
                        
    def heal_wounded(self):
        if self.last_heal is not None and self.last_heal.status != "dead":
            smart_heal(self, self.last_heal)
            return True
        else:
            if self.special_attributes["steps_after_healing"] < 10:
                self.special_attributes["steps_after_healing"] += 1
                return False
            
            range_positions = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=True,
                radius=self.special_attributes["healing_range"]) # get x,y in range N

            for position in range_positions: # get all agents in range
                result = self.model.grid.get_cell_list_contents([position])
                random.shuffle(result)
                for cellmate in result:
                    if cellmate.fraction == self.fraction and cellmate.status == "wounded" and self != cellmate and not cellmate.type.startswith("projectile_"): # check if enemy
                        smart_heal(self, cellmate)
                        return True
            return False

    
    ### movements ###
    def move(self):
        
        if self.type == "medic" and self.special_attributes["steps_after_healing"] < 10:
            self.special_attributes["steps_after_healing"] += 1
            self.steps_after_attack += 1
            return
        
        if not self.type.startswith("projectile_") and self.steps_after_attack < 10:
            self.steps_after_attack += 1
            return
        
        if self.movement == "random":
            possible_steps = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False)
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)
            
        elif self.movement == "stay":
            pass
        
        elif self.movement == "route":
            if self.route_index < len(self.route):
                self.move_towards(self.route[self.route_index])
                if self.pos == self.route[self.route_index]:
                    self.route_index += 1
            if self.type.startswith("projectile_") and self.pos == self.route[-1] and self.status != "dead":
                self.attack()
                self.kill_agent()
            
            
        # Check for mines after moving
        if self.pos in self.model.mine_map and self.model.mine_map[self.pos] > 0:
            self.trigger_mine()

    def move_towards(self, target):
        """Move one step towards the target."""
        x, y = self.pos
        target_x, target_y = target

        # Determine the direction to move in x and y
        next_x = x + 1 if target_x > x else x - 1 if target_x < x else x
        next_y = y + 1 if target_y > y else y - 1 if target_y < y else y

        # Move to the new position if it's different from the current position
        if (next_x, next_y) != self.pos:
            new_position = (next_x, next_y)
            self.model.grid.move_agent(self, new_position)
            
    def trigger_mine(self):
        if self.type.startswith("projectile_"):
            return
        mine_damage = 80

        self.health -= mine_damage
        if self.health <= 0:
            self.health = 0
            self.status = "dead"

        # Reduce the number of mines at this location
        self.model.mine_map[self.pos] -= 1
        if self.model.mine_map[self.pos] == 0:
            del self.model.mine_map[self.pos]  # Remove the mine location if no mines are left

def smart_attack(agent_damager, agent_aim):
    if agent_damager.type.startswith("projectile_") and agent_damager.pos != agent_damager.route[-1]:
        return
     
    # general change 0 or 1
    chance = np.random.binomial(n=1, p=agent_damager.damage_chance)
    basic_damage = agent_damager.damage 
    
    # basic damage amount
    height_map = agent_damager.model.height_map
    agent_damager_height = height_map[agent_damager.pos]
    agent_aim_height = height_map[agent_aim.pos]
    h_coefficient = 0.3*(agent_damager_height - agent_aim_height) + 1
    amount_to_damage = chance * basic_damage * h_coefficient

    # atack (change attributes)
    agent_aim.health -= amount_to_damage
    agent_aim.status = "wounded"
    agent_damager.damaged += amount_to_damage
    
    # change status if needed
    if agent_aim.health <= 0:
        agent_aim.kill_agent()
    if agent_damager.type.startswith("projectile_"):
        agent_damager.kill_agent()
        
    agent_damager.steps_after_attack = 0
    agent_damager.last_aim = agent_aim


def smart_heal(agent_medic, agent_wounded):
    # variables
    chance = np.random.binomial(n=1, p=agent_medic.special_attributes["healing_chance"]) # 0 or 1
    heal_amount = agent_medic.special_attributes["healing"]
    
    # calculate healing
    result = chance * heal_amount
    
    # heal
    agent_wounded.health += result
    if agent_wounded.health > agent_wounded.max_health:
        agent_wounded.health = agent_wounded.max_health
        agent_wounded.status = "alive"
    agent_medic.healed += result
    agent_medic.special_attributes["steps_after_healing"] = 0
    agent_medic.last_heal = agent_wounded


# place agents to grid
def place_agents(model, n_soldiers, params, pos=None):
    """
    Place soldiers on the grid.

    Args:
        model: The model instance.
        n_soldiers: Number of soldiers to place.
        params: Parameters for the soldiers.
        pos: Optional position to place the soldiers. If None, places randomly.
    """

    current_id = model.max_id
    
    for unique_id in range(current_id + 1, current_id + 1 + n_soldiers):
        agent = SoldierAgent(unique_id, params, model)
        model.schedule.add(agent)
        
        if pos is None:
            x = model.random.randrange(model.grid.width)
            y = model.random.randrange(model.grid.height)
            model.grid.place_agent(agent, (x, y))
        else:
            model.grid.place_agent(agent, pos)
        
    model.max_id += n_soldiers + 1


def add_agents_to_model(model, case=1, n=50, n_medics=0, n_mortars=0):
    
    if case == "big_battle":
        
        ### ENEMIES ###
        
        # mortars 
        params = {"fraction": "enemy",
                  "type": "mortar",
                  "movement": "stop",
                  "route": []}
        place_agents(model=model, n_soldiers=1, params=params, pos=(40, 90))
        place_agents(model=model, n_soldiers=1, params=params, pos=(45, 90))
        place_agents(model=model, n_soldiers=1, params=params, pos=(50, 90))
        place_agents(model=model, n_soldiers=1, params=params, pos=(55, 90))
        place_agents(model=model, n_soldiers=1, params=params, pos=(60, 90))
        
        # infantries
        params = {"fraction": "enemy",
                  "type": "infantry",
                  "movement": "stop",
                  "route": []}
        
        place_agents(model=model, n_soldiers=20, params=params, pos=(45, 75))
        place_agents(model=model, n_soldiers=20, params=params, pos=(55, 75))
        
        # infantries with random walking
        params = {"fraction": "enemy",
                  "type": "infantry",
                  "movement": "random",
                  "route": []}
        place_agents(model=model, n_soldiers=1, params=params, pos=(50, 80))
        
        ### ALLIES ###
        
        # mortars 
        params = {"fraction": "ally", "type": "mortar", "movement": "stop", "route": []}
        place_agents(model=model, n_soldiers=1, params=params, pos=(40, 10))
        place_agents(model=model, n_soldiers=1, params=params, pos=(45, 10))
        place_agents(model=model, n_soldiers=1, params=params, pos=(55, 10))
        place_agents(model=model, n_soldiers=1, params=params, pos=(60, 10))
        
        # infantries 
        params = {"fraction": "ally",
                  "type": "infantry",
                  "movement": "route",
                  "route": [(40, 90)]}
        
        place_agents(model=model, n_soldiers=30,
                     params=params,
                     pos=(50, 15))
        
        params = {"fraction": "ally",
                  "type": "medic",
                  "movement": "route",
                  "route": [(40, 90)]}
        place_agents(model=model, n_soldiers=2,
                     params=params,
                     pos=(50, 15))
        
        params = {"fraction": "ally",
                  "type": "infantry",
                  "movement": "route",
                  "route": [(60, 90)]}
        place_agents(model=model, n_soldiers=30,
                     params=params,
                     pos=(50, 15))
        
        params = {"fraction": "ally",
                  "type": "medic",
                  "movement": "route",
                  "route": [(60, 90)]}
        place_agents(model=model, n_soldiers=2,
                     params=params,
                     pos=(50, 15))
        
    if case == "small_battle":
        ### ENEMIES ###
        
        # infantries
        params = {"fraction": "enemy",
                  "type": "infantry",
                  "movement": "stop",
                  "route": []}
        place_agents(model=model, n_soldiers=5, params=params, pos=(40, 90))
        place_agents(model=model, n_soldiers=5, params=params, pos=(45, 90))
        place_agents(model=model, n_soldiers=5, params=params, pos=(50, 90))
        place_agents(model=model, n_soldiers=5, params=params, pos=(55, 90))
        place_agents(model=model, n_soldiers=5, params=params, pos=(60, 90))
        place_agents(model=model, n_soldiers=5, params=params, pos=(40, 70))
        place_agents(model=model, n_soldiers=5, params=params, pos=(60, 70))
        
        
        ### ALLIES ###
        
        # infantries 
        params = {"fraction": "ally", "type": "infantry", "movement": "route", "route": [(40, 90), (60,90)]}
        place_agents(model=model, n_soldiers=n//2,
                     params=params,
                     pos=(50, 20))
        if n_medics != 0:
            params = {"fraction": "ally", "type": "medic", "movement": "route", "route": [(40, 90), (60,90)]}
            place_agents(model=model, n_soldiers=n_medics,
                            params=params,
                            pos=(50, 20))
        
        params = {"fraction": "ally", "type": "infantry", "movement": "route", "route": [(60, 90), (40,90)]}
        place_agents(model=model, n_soldiers=n//2,
                     params=params,
                     pos=(50, 20))
        
        if n_mortars != 0:
            params = {"fraction": "ally", "type": "mortar", "movement": "stop", "route": [(40, 90), (60,90)]}
            place_agents(model=model, n_soldiers=n_mortars,
                            params=params,
                            pos=(50, 20))
        
    # for visualization
    if case == 1:
        params = {"fraction": "enemy", "type": "infantry", "movement": "stop", "route": None}
        place_agents(model=model, n_soldiers=1, params=params, pos=(60, 80))
        place_agents(model=model, n_soldiers=1, params=params, pos=(40, 80))
        place_agents(model=model, n_soldiers=1, params=params, pos=(20, 80))

        params = {"fraction": "ally", "type": "infantry", "movement": "route", "route": [(20, 80), (80, 80)]}
        place_agents(model=model, n_soldiers=30, params=params, pos=(20, 0))

        params = {"fraction": "ally", "type": "mortar", "movement": "stop", "route": []}
        place_agents(model=model, n_soldiers=1, params=params, pos=(20, 0))
        place_agents(model=model, n_soldiers=1, params=params, pos=(60, 0))
    
    # for tests
    if case == 2:
        params = {"fraction": "enemy", "type": "infantry", "movement": "stop", "route": None}
        place_agents(model=model, n_soldiers=5, params=params, pos=(60, 80))

        params = {"fraction": "ally", "type": "infantry", "movement": "stop", "route": None}
        place_agents(model=model, n_soldiers=5, params=params, pos=(65, 80))
from mesa import Model, space, time
from mesa.datacollection import DataCollector

class BattleModel(Model):

    def __init__(self, width, height, height_map, mine_map):
        self.grid = space.MultiGrid(width, height, False)
        self.schedule = time.RandomActivation(self)
        self.max_id = 0
        
        self.datacollector = DataCollector(
            
            model_reporters={"alive allies": compute_alive_allies,
                            "alive enemies": compute_alive_enemies,
                            "allies total health": compute_health_allies,
                            "enemies total health": compute_health_enemies},
            
            
            agent_reporters={"Fraction": "fraction",
                             "Status": "status",
                             "Health": "health",
                             "Damaged": "damaged",
                             "Healed": "healed"}

        )
        
        self.height_map = height_map
        self.mine_map = mine_map 
        
        
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

# model reportes

def compute_alive_allies(model):
    alive = 0
    for agent in model.schedule.agents:
        if agent.fraction == "ally" and agent.status != "dead" and not agent.type.startswith("projectile_"):
            alive +=1
    return alive

def compute_alive_enemies(model):
    alive = 0
    for agent in model.schedule.agents:
        if agent.fraction == "enemy" and agent.status != "dead" and not agent.type.startswith("projectile_"):
            alive +=1
    return alive

def compute_health_allies(model):
    health = 0
    for agent in model.schedule.agents:
        if agent.fraction == "ally" and agent.status != "dead" and not agent.type.startswith("projectile_"):
            health += agent.health
    return health

def compute_health_enemies(model):
    health = 0
    for agent in model.schedule.agents:
        if agent.fraction == "enemy" and agent.status != "dead" and not agent.type.startswith("projectile_"):
            health += agent.health
    return health
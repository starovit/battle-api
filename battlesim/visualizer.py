import matplotlib.pyplot as plt
import scipy.ndimage
import cv2

class Visualizer():
    
    def __init__(self, model, image_path):
    
        self.model = model
        self.height = model.grid.height
        self.width = model.grid.width
        self.image = self.read_image(image_path)
        self.scaler = 10
    
    def read_image(self, image_path):
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, dsize=(10*self.width, 10*self.height),
                                    interpolation=cv2.INTER_CUBIC)
        return image

    @staticmethod
    def _get_color(agent):
        if agent.fraction == "ally":
            if agent.type.startswith("projectile_"):
                return "yellow"
            return "blue"
        elif agent.fraction == "enemy":
            if agent.type.startswith("projectile_"):
                return "orange"
            return "red"
        return "white"
    
    @staticmethod
    def _plot_agents(ax, arguments):
        ax.scatter(
            arguments["xs"],
            arguments["ys"],
            s=arguments["ss"],
            color=arguments["colors"],
            marker=arguments.get("marker")
        )
    
    def _add_agent_arguments(self, agent, arguments):
        x_transformed = int(agent.pos[0] * self.scaler)
        y_transformed = int((self.height - 1 - agent.pos[1]) * self.scaler)
    
        arguments["xs"].append(x_transformed)
        arguments["ys"].append(y_transformed)
        arguments["ss"].append(agent.health)
        arguments["colors"].append(self._get_color(agent))
        
          
    
    def plot_teritory(self, show_heights = True, show_mines = True):
        
        fig, ax = plt.subplots()
        
        ax.imshow(self.image) # trick to show white
        
        if show_heights == True:
            zoomed_heiths =  scipy.ndimage.zoom(self.model.height_map.round(1),
                                 (self.scaler, self.scaler),
                                 order=1)
            ax.imshow(zoomed_heiths, cmap="gray", alpha=0.4)
            
        if show_mines == True and len(self.model.mine_map)!=0:

            mine_xs, mine_ys = zip(*self.model.mine_map.keys())
            mine_xs = [int(x * self.scaler) for x in mine_xs]
            mine_ys = [int((self.height - 1 - y) * self.scaler) for y in mine_ys]
            mine_sizes = [5*value for value in self.model.mine_map.values()]  # Adjust size as needed

            ax.scatter(mine_xs,
                       mine_ys,
                       color='purple',
                       s=mine_sizes,
                       marker='.',
                       alpha=0.8)
        
        # show soldiers
        infantry_scatter_arguments = {"xs":[], "ys":[], "ss":[], "colors":[]}
        medic_scatter_arguments = {"xs":[], "ys":[], "ss":[], "colors":[], "marker": "+"}
        mortar_scatter_arguments = {"xs":[], "ys":[], "ss":[], "colors":[], "marker": "s"}
        projectile_scatter_arguments = {"xs":[], "ys":[], "ss":[], "colors":[], "marker": "x"}
        for agent in self.model.schedule.agents:
            if agent.type == "infantry":
                self._add_agent_arguments(agent, infantry_scatter_arguments)
            elif agent.type == "medic":
                self._add_agent_arguments(agent, medic_scatter_arguments)
            elif agent.type == "mortar":
                self._add_agent_arguments(agent, mortar_scatter_arguments)
            elif agent.type.startswith("projectile_"):
                self._add_agent_arguments(agent, projectile_scatter_arguments)
            
        
        self._plot_agents(ax, infantry_scatter_arguments)
        self._plot_agents(ax, medic_scatter_arguments)
        self._plot_agents(ax, mortar_scatter_arguments)
        self._plot_agents(ax, projectile_scatter_arguments)     
        ax.set_xticks([])
        ax.set_yticks([])
        plt.close()
            
        return fig
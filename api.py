from flask import Flask, request, jsonify
import matplotlib.pyplot as plt

from battlesim.agents import add_agents_to_model, add_agents_to_model
from battlesim.model import BattleModel
from battlesim.map_creator import MapCreator
from battlesim.utils import final_stats
from battlesim.visualizer import Visualizer # ADDED

app = Flask(__name__)

@app.route('/run_simulation', methods=['GET'])
def run_battle_simulation():
    # Get parameters from URL query string
    n_soldiers = request.args.get('n_soldiers', default=50, type=int)
    n_medics = request.args.get('n_medics', default=0, type=int)
    n_mines = request.args.get('n_mines', default=1, type=int) 

    # create map
    map_creator = MapCreator(size=100)
    map_creator.read_heights(path_to_file="database/heights.txt")
    height_map = map_creator.height_map
    mine_map = map_creator.create_mine_map((0,30), (100, 50), n_mines)

    # create model
    model = BattleModel(width=100,
                    height=100,
                    height_map=height_map,
                    mine_map=mine_map)
    
    visualizer = Visualizer(model, image_path="database/image.png") # ADDED
    
    # add agents
    add_agents_to_model(model=model,
                        case="small_battle",
                        n=n_soldiers,
                        n_medics=n_medics)

    max_steps = 150
    for i in range(max_steps):
        model.step()
        if i%3 == 0:
            fig = visualizer.plot_teritory()
            fig.savefig("database/teritory.png",
                        bbox_inches='tight',
                        pad_inches=0)
            plt.close(fig)

    stats = final_stats(model)  # Get final stats
    return jsonify(stats)




if __name__ == '__main__':
    app.run(debug=True)

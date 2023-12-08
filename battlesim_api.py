from flask import Flask, request, jsonify

from battlesim.agents import add_agents_to_model, add_agents_to_model
from battlesim.model import BattleModel
from battlesim.map_creator import MapCreator
from battlesim.utils import run_simulation, final_stats

app = Flask(__name__)

@app.route('/run_simulation', methods=['GET'])
def run_battle_simulation():
    # Get parameters from URL query string
    n_soldiers = request.args.get('n_soldiers', default=50, type=int)
    n_medics = request.args.get('n_medics', default=0, type=int)
    n_mines = request.args.get('n_mines', default=1, type=int) 

    # create map
    map_creator = MapCreator(size=100)
    height_map = map_creator.create_height_map()
    mine_map = map_creator.create_mine_map((0,30), (100, 50), n_mines)

    # create model
    model = BattleModel(width=100,
                    height=100,
                    height_map=height_map,
                    mine_map=mine_map)
    
    # add agents
    add_agents_to_model(model=model,
                        case="small_battle",
                        n=n_soldiers,
                        n_medics=n_medics)

    run_simulation(model, None, show = False)  # Run the simulation
    stats = final_stats(model)  # Get final stats
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True)

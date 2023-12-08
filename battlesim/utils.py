import matplotlib.pyplot as plt
import seaborn as sns
import time
from IPython.display import display, clear_output


def show_online(visualizer):
    fig = visualizer.plot_teritory()
    clear_output(wait=True)
    display(fig)
    plt.close(fig)

def any_team_exist(model):
    dataframe = model.datacollector.get_model_vars_dataframe()
    if dataframe.empty:
        return True
    elif 0 in dataframe.iloc[-1, :2].values:
        return False
    else:
        return True

def run_simulation(model, visualizer, max_steps=500, show=False, sleep_time=0.1):
    i = 0
    if show:
        while i < max_steps and any_team_exist(model):
            model.step()
            show_online(visualizer)
            time.sleep(sleep_time)
            i += 1
    else:
        while i < max_steps and any_team_exist(model):
            model.step()
            i += 1
    print(f"Numb of iterations: {i}")



# Final plots
def final_plots(model):

    # Get model vars dataframe
    data = model.datacollector.get_model_vars_dataframe()

    # Create a figure with subplots
    fig, axs = plt.subplots(2, 2, figsize=(10, 6))  # 2 rows, 2 columns

    # First subplot - Model Vars Plot 1
    axs[0, 0].plot(data.iloc[:, -2:], label=data.columns[-2:])
    axs[0, 0].legend()
    axs[0, 0].grid(alpha=0.5)
    axs[0, 0].set_ylabel("Health")
    axs[0, 0].set_xlabel("Step")
    axs[0, 0].set_xlim(0)

    # Second subplot - Model Vars Plot 2
    axs[0, 1].plot(data.iloc[:, :2], label=data.columns[:2])
    axs[0, 1].legend()
    axs[0, 1].grid(alpha=0.5)
    axs[0, 1].set_ylabel("Number")
    axs[0, 1].set_xlabel("Step")
    axs[0, 1].set_xlim(0)

    # Get agent vars dataframe
    data = model.datacollector.get_agent_vars_dataframe()

    # Last step results
    last_step = data.index.get_level_values("Step").max()
    last_step_data = data.xs(last_step, level="Step")
    last_step_data = last_step_data[["Fraction", "Health", "Damaged"]]

    # Third subplot - Last Step Allies Health
    sns.histplot(data=last_step_data[last_step_data["Fraction"]=="ally"],
                 x="Health", ax=axs[1, 0])
    axs[1, 0].set_title("Last Step Allies Health")

    # Fourth subplot - Last Step Enemies Health
    sns.histplot(data=last_step_data[last_step_data["Fraction"]=="enemy"],
                 x="Health", color="red", ax=axs[1, 1])
    axs[1, 1].set_title("Last Step Enemies Health")

    # Adjust layout
    plt.tight_layout()
    plt.show()


# Final plots
def final_stats(model):

    # Get model vars dataframe
    try:
        data = model.datacollector.get_model_vars_dataframe().iloc[-1,:]
    except:
        return 0

    result = {"Number of allies alive": float(data[0]),
              "Number of enemies alive": float(data[1]),
              "Allies health": int(data[2]),
              "Enemies health": int(data[3])}
    
    return result
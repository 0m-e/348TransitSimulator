import TransitSimulator as sim
import distribution_fitting as dist
import pandas as pd

# --- Program stops, vehicles, and delays here --- #
# sim.Stop(ID, waiting_passengers, distance_from_prev_stop, passenger_arrival_mean, passenger_deboard_p, terminal=False, print_updates=False)
# sim.Vehicle(ID, capacity, route, current_stop, oos=False, print_updates=False)
# sim.Delay(ID, prob, duration_p, duration_n)

stops = [sim.Stop(0, 0, 5, 0.5, 0.2, False, print_updates=True), sim.Stop(1, 0, 5, 0, 1, True, print_updates=True)]
vehs = [sim.Vehicle(0, 10, stops, 0, print_updates=True), sim.Vehicle(1, 10, stops, 0, print_updates=True)]
#create list of Delay object
error_dict = dist.get_error_prob("data/processed/bus_proportions.csv")
df = pd.read_csv("data/processed/bus_delay_model_results.csv")

size_list = df["size"].tolist()
prob_list = df["mu"].tolist()
delay_list = []
for (size, prob), (key, value) in zip(zip(size_list, prob_list), error_dict.items()):
    delay_list.append(sim.Delay(key, value, size, prob))
delays = delay_list

sim.run_simulation(20, vehs, stops, delays, "summary.txt")


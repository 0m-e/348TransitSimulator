import numpy as np
import matplotlib as plt
rng = np.random.default_rng()
import pandas as pd
from scipy.stats import poisson, nbinom, geom

class Vehicle:
    def __init__(self, ID, capacity, route, current_stop, oos=False, print_updates=False):
        self.ID = ID  # Vehicle name
        self.capacity = capacity  # Max passengers
        self.route = route  # Must be list of stops
        self.current_stop = current_stop  # Current stop
        self.oos = oos  # Out of service, used in vehicle loop to make this vehicle do nothing, in constructor so it is possible to start out of service
        self.print_updates = print_updates  # Print updates about this object to timestep summary

        self.passengers = 0
        self.distance_to_next_stop = 0  # Vehicles will all initialize at a stop
        self.remaining_delay = 0  # Initialize delay time variable

class Stop:
    def __init__(self, ID, waiting_passengers, distance_from_prev_stop, passenger_arrival_mean, passenger_deboard_p, terminal=False, print_updates=False):
        self.ID = ID  # Stop name
        self.distance_from_prev_stop = distance_from_prev_stop  # Distance from previous stop in timesteps, should have avg of ~5
        self.terminal = terminal  # Bool for if its the last stop, default False
        self.waiting_passengers = waiting_passengers
        self.passenger_arrival_mean = passenger_arrival_mean  # Mean number of passengers arriving per timestep
        self.passenger_deboard_p = passenger_deboard_p  # Probability each passenger deboards at this stop
        self.print_updates = print_updates  # Print updates about this object to timestep summary

class Delay:
    def __init__(self, ID, prob, duration_p, duration_n, fatal=False):
        self.ID = ID  # Type of delay
        self.prob = prob  # Probability of occurrence on each timestep
        self.duration_p = duration_p  # p parameter in negative binomial sample for delay duration
        self.duration_n = duration_n  # n parameter in negative binomial sample for delay duration
        self.fatal = fatal  # Bool for whether delay causes vehcle to be permanently out of service

    def possible(self, v):  # Evaluate whether delay can occur for this vehicle configuration, to be used in subclasses
        return True  # Generic delay is always possible

class Route:
    def __init__(self, ID, num_stops, expected_length, expected_intervals):
        self.ID = ID #route_id i.e "510 SPADINA", "505 DUNDAS"
        self.num_stops = num_stops #number of stops on the line (integer)
        self.expected_length = expected_length #expected length of the line (in time)
        self.expected_intervals = expected_intervals #expected amt of time to travel to each stop (list of integers
    #should sum to expected length
def run_simulation(timesteps, vehicles, stops, delays, output):
    # Every time step, stop passenger arrival will be calculated and there will be a chance of delays
    # delays is list of delays that are possible in this simulation

    f = open(output, "w")

    for t in range(timesteps):
        print(f"--- Timestep {t} Summary ---", file=f)

        # Firstly passengers arrive at stops
        for s in stops:
            arriving = rng.poisson(s.passenger_arrival_mean)
            s.waiting_passengers += arriving

            if s.print_updates:
                print(f"Stop {s.ID}: {arriving} passengers arrived. Total: {s.waiting_passengers}", file=f)

        # Secondly vehicles are updated, if at stop they load/unload, if not they move forward
        # If at terminal all passengers unload, vehicle is deleted and stats are collected
        for v in vehicles:
            if v.oos:
                if v.print_updates:
                    print(f"Vehicle {v.ID}: Out of service.", file=f)
                continue  # Do nothing

            elif v.remaining_delay > 0:  # Vehicle is delayed
                if v.print_updates:
                    print(f"Vehicle {v.ID}: Delayed for {v.remaining_delay} more timesteps.", file=f)

                v.remaining_delay -= 1

            elif v.distance_to_next_stop > 0:  # Vehicle is between stops, not delayed
                if v.print_updates:
                    print(f"Vehicle {v.ID}: {v.distance_to_next_stop} timesteps away from Stop {v.current_stop} carrying {v.passengers}/{v.capacity} passengers.", file=f)

                v.distance_to_next_stop -= 1

            else:  # Vehicle is at a stop and not currently delayed
                stop = v.route[v.current_stop]

                # Deboard, board, set next stop
                # Deboard
                deboarded = rng.binomial(v.passengers, stop.passenger_deboard_p)  # Deboarding is binomially distributed
                v.passengers -= deboarded
                # Board
                space = max(0, v.capacity - v.passengers)  # Availible space is max of 0, capacity - passengers
                waiting = max(0, stop.waiting_passengers)

                boarded = min(waiting, space)  # Board the minimum of space in vehicle or passengers waiting at stop
                v.passengers += boarded
                stop.waiting_passengers -= boarded

                if v.print_updates:
                    print(f"Vehicle {v.ID} @ Stop {v.current_stop}: Boarded {boarded}, Deboarded {deboarded}, Capacity {v.passengers}/{v.capacity}", file=f)

                # Set next stop
                if stop.terminal:  # Current stop is terminal
                    # Take veh out of service
                    v.oos = True;
                else:
                    v.current_stop += 1
                    v.distance_to_next_stop = v.route[v.current_stop].distance_from_prev_stop


            # Calculate vehicle specific delays
            for d in delays:
                if d.possible(v):
                    # Delay is possible for vehicle configuration, now determine whether it actually happens
                    if rng.binomial(1, d.prob):
                        # Delay occurs
                        time = rng.negative_binomial(d.duration_n, d.duration_p) + d.duration_n # p = 1/(mu + 1)
                        v.remaining_delay += time

                        if v.print_updates:
                            print(f"Vehicle {v.ID}: Delay type [{d.ID}] occurred with duration {time}. Remaining delay is now {v.remaining_delay}.", file=f)


        print("\n", file=f)  # Maybe idk if it looks good
    f.close()


bus_proportions = pd.read_csv("bus_proportions.csv")
streetcar_porportions = pd.read_csv("streetcar_proportions.csv")

# Convert to dictionary: {column_name: value}
bus_dict = bus_proportions.iloc[0].to_dict()
streetcar_dict = streetcar_porportions.iloc[0].to_dict()

df = pd.read_csv("bus_delay_model_results.csv")

# Dictionary to store PMFs
pmf_dict = {}

for _, row in df.iterrows():
    code = row["delay_code"]
    model = row["best_model"]

    if model == "pois":
        lam = row["lambda"]

        def pmf(k, lam=lam):
            return poisson.pmf(k, mu=lam)

    elif model == "nb":
        size = row["size"]   # corresponds to 'n'
        mu = row["mu"]

        # Convert (size, mu) → (n, p) for scipy
        p = size / (size + mu)

        def pmf(k, size=size, p=p):
            return nbinom.pmf(k, n=size, p=p)

    elif model == "geom":
        p = row["prob"]

        def pmf(k, p=p):
            return geom.pmf(k, p=p)

    else:
        continue

    pmf_dict[code] = pmf

# --- Program stops, vehicles, and delays here --- #
# Stop(ID, waiting_passengers, distance_from_prev_stop, passenger_arrival_mean, passenger_deboard_p, terminal=False, print_updates=False)
# Vehicle(ID, capacity, route, current_stop, oos=False, print_updates=False)
# Delay(ID, prob, duration_mean)

stops = [Stop(0, 0, 5, 0.5, 0.2, False, print_updates=True), Stop(1, 0, 5, 0, 1, True, print_updates=True)]
vehs = [Vehicle(0, 10, stops, 0, print_updates=True), Vehicle(1, 10, stops, 0, print_updates=True)]
delays = [Delay("Test Delay", 0.1, 1/(3+1), 1)]  # mu = (1-p)/p <-> p = 1/(mu+1)

run_simulation(20, vehs, stops, delays, "summary.txt")

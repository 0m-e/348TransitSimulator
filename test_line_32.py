import TransitSimulator as sim
import distribution_fitting as dist
import pandas as pd
import numpy as np
rng = np.random.default_rng()

def alt_run_simulation(timesteps, vehicles, stops, delays, output, delay_occured):
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
                        delay_occured = True

                        if v.print_updates:
                            print(f"Vehicle {v.ID}: Delay type [{d.ID}] occurred with duration {time}. Remaining delay is now {v.remaining_delay}.", file=f)


        print("\n", file=f)  # Newline at end of every timestep summary
    f.close()

error_dict = dist.get_error_prob("data/processed/bus_proportions.csv")
df = pd.read_csv("data/processed/bus_delay_model_results.csv")

size_list = df["size"].tolist()
prob_list = df["mu"].tolist()
delay_list = []
for (size, prob), (key, value) in zip(zip(size_list, prob_list), error_dict.items()):
    delay_list.append(sim.Delay(key, value, size, prob))
delays = delay_list
# sim.Stop(ID, waiting_passengers, distance_from_prev_stop, passenger_arrival_mean, passenger_deboard_p, terminal=False, print_updates=False)
# sim.Vehicle(ID, capacity, route, current_stop, oos=False, print_updates=False)
# sim.Delay(ID, prob, duration_p, duration_n)
stops = [sim.Stop("Renforth", 0, 5, 0.5, 0.2, False, False),
         sim.Stop("East Mall", 0, 5, 0.5, 0.2, False, False),
         sim.Stop("Martin Grove", 0, 5, 0.5, 0.2, False, False),
         sim.Stop("Kipling Ave", 0, 5, 0.5, 0.2, False, False),
         sim.Stop("Islington Ave", 0, 5, 0.5, 0.2, False, False),
         sim.Stop("Royal York Rd", 0, 5, 0.5, 0.2, False, False),
         sim.Stop("Scarlett Rd", 0, 5, 0.5, 0.2, False, False),
         sim.Stop("Jane St", 0, 5, 0.5, 0.2, False, False),
         sim.Stop("Weston Road", 0, 5, 0.5, 0.2, False, False),
         sim.Stop("Mount Dennis Station", 0, 5, 0, 1, True, False)

]
vehs = [sim.Vehicle(0, 50, stops, 0, print_updates=False)]

#sim loop
delay_counter = 0
while delay_counter <392:
    alt_run_simulation(100)


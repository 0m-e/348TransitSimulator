import TransitSimulator as sim

# --- Program stops, vehicles, and delays here --- #
# sim.Stop(ID, waiting_passengers, distance_from_prev_stop, passenger_arrival_mean, passenger_deboard_p, terminal=False, print_updates=False)
# sim.Vehicle(ID, capacity, route, current_stop, oos=False, print_updates=False)
# sim.Delay(ID, prob, duration_p, duration_n)

stops = [sim.Stop(0, 0, 5, 0.5, 0.2, False, print_updates=True), sim.Stop(1, 0, 5, 0, 1, True, print_updates=True)]
vehs = [sim.Vehicle(0, 10, stops, 0, print_updates=True), sim.Vehicle(1, 10, stops, 0, print_updates=True)]
delays = [sim.Delay("Test Delay", 0.1, 1/(3+1), 1)]  # mu = (1-p)/p <-> p = 1/(mu+1)

sim.run_simulation(20, vehs, stops, delays, "summary.txt")

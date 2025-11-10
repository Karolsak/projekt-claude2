"""
Command-Line Interface for Economic Load Dispatch
Works without GUI for testing and quick calculations
"""

import sys


class EconomicLoadDispatch:
    """Economic Load Dispatch Calculator"""

    def __init__(self, plants_data):
        self.plants = plants_data
        self.n_plants = len(plants_data)

    def calculate_cost(self, plant_idx, power):
        """Calculate total cost for a plant at given power output"""
        plant = self.plants[plant_idx]
        cost = plant['a'] * power + (plant['b'] / 2) * power**2
        return cost

    def incremental_cost(self, plant_idx, power):
        """Calculate incremental cost (dC/dP) for a plant"""
        plant = self.plants[plant_idx]
        return plant['a'] + plant['b'] * power

    def solve_economic_dispatch(self, total_load):
        """Solve economic dispatch using lambda iteration method"""
        lambda_min = max([plant['a'] for plant in self.plants])
        lambda_max = max([plant['a'] + plant['b'] * plant['pmax'] for plant in self.plants])

        tolerance = 0.01
        max_iterations = 100

        for iteration in range(max_iterations):
            lambda_val = (lambda_min + lambda_max) / 2

            powers = []
            total_power = 0

            for plant in self.plants:
                p = (lambda_val - plant['a']) / plant['b']
                p = max(plant['pmin'], min(plant['pmax'], p))
                powers.append(p)
                total_power += p

            error = total_power - total_load

            if abs(error) < tolerance:
                break
            elif error > 0:
                lambda_max = lambda_val
            else:
                lambda_min = lambda_val

        individual_costs = [self.calculate_cost(i, powers[i]) for i in range(self.n_plants)]
        total_cost = sum(individual_costs)
        inc_costs = [self.incremental_cost(i, powers[i]) for i in range(self.n_plants)]

        return {
            'powers': powers,
            'lambda': lambda_val,
            'total_cost': total_cost,
            'individual_costs': individual_costs,
            'incremental_costs': inc_costs,
            'iterations': iteration + 1
        }


def print_results(plants_data, result, total_load):
    """Print formatted results"""
    print()
    print("=" * 80)
    print("ECONOMIC LOAD DISPATCH - OPTIMAL SOLUTION")
    print("=" * 80)
    print()

    print(f"Total System Load: {total_load:.2f} MW")
    print(f"Lambda (λ): {result['lambda']:.3f} ₹/MW")
    print(f"Iterations: {result['iterations']}")
    print()

    print("-" * 80)
    print(f"{'Plant':<10} {'Power (MW)':<15} {'Inc. Cost':<15} {'Total Cost':<15} {'Limits (MW)':<20}")
    print("-" * 80)

    for i, plant in enumerate(plants_data):
        print(f"{plant['name']:<10} "
              f"{result['powers'][i]:>10.2f}     "
              f"{result['incremental_costs'][i]:>10.3f}     "
              f"₹{result['individual_costs'][i]:>10.2f}     "
              f"[{plant['pmin']}-{plant['pmax']}]")

    print("-" * 80)
    print(f"{'TOTAL':<10} {sum(result['powers']):>10.2f} MW{'':<14} ₹{result['total_cost']:>10.2f}")
    print("=" * 80)
    print()

    # Verification
    print("VERIFICATION:")
    print("-" * 80)

    # Check power balance
    power_balance = abs(sum(result['powers']) - total_load) < 0.1
    print(f"Power Balance: {sum(result['powers']):.2f} MW = {total_load:.2f} MW " +
          ("✓" if power_balance else "✗"))

    # Check incremental costs are equal
    ic_equal = all(abs(result['incremental_costs'][0] - ic) < 0.1
                   for ic in result['incremental_costs'])
    print(f"Equal Incremental Costs: {ic_equal} " + ("✓" if ic_equal else "✗"))

    # Check constraints
    constraints_ok = all(
        plant['pmin'] <= power <= plant['pmax']
        for plant, power in zip(plants_data, result['powers'])
    )
    print(f"All Constraints Satisfied: {constraints_ok} " + ("✓" if constraints_ok else "✗"))
    print("=" * 80)
    print()


def run_default_problem():
    """Run the default problem from the textbook"""
    plants_data = [
        {'name': 'Plant 1', 'a': 40, 'b': 0.25, 'pmin': 30, 'pmax': 150},
        {'name': 'Plant 2', 'a': 50, 'b': 0.30, 'pmin': 40, 'pmax': 125},
        {'name': 'Plant 3', 'a': 20, 'b': 0.20, 'pmin': 50, 'pmax': 225}
    ]

    total_load = 350.0

    print()
    print("PROBLEM STATEMENT:")
    print("-" * 80)
    for plant in plants_data:
        print(f"{plant['name']}: dC/dP = {plant['a']} + {plant['b']}·P, "
              f"{plant['pmin']} ≤ P ≤ {plant['pmax']} MW")
    print(f"Total Load: {total_load} MW")

    dispatcher = EconomicLoadDispatch(plants_data)
    result = dispatcher.solve_economic_dispatch(total_load)

    print_results(plants_data, result, total_load)


def run_custom_problem(load=None):
    """Run with custom load value"""
    plants_data = [
        {'name': 'Plant 1', 'a': 40, 'b': 0.25, 'pmin': 30, 'pmax': 150},
        {'name': 'Plant 2', 'a': 50, 'b': 0.30, 'pmin': 40, 'pmax': 125},
        {'name': 'Plant 3', 'a': 20, 'b': 0.20, 'pmin': 50, 'pmax': 225}
    ]

    if load is None:
        load = 350.0

    dispatcher = EconomicLoadDispatch(plants_data)
    result = dispatcher.solve_economic_dispatch(load)

    print_results(plants_data, result, load)


def interactive_mode():
    """Interactive mode for custom load values"""
    print()
    print("=" * 80)
    print("ECONOMIC LOAD DISPATCH - INTERACTIVE MODE")
    print("=" * 80)
    print()

    while True:
        try:
            load_input = input("Enter total load in MW (or 'q' to quit): ").strip()

            if load_input.lower() in ['q', 'quit', 'exit']:
                print("Exiting...")
                break

            load = float(load_input)

            if load < 120 or load > 500:
                print("⚠ Warning: Load should be between 120 and 500 MW for valid results")

            run_custom_problem(load)

        except ValueError:
            print("Invalid input! Please enter a number or 'q' to quit.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break


def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '-i' or sys.argv[1] == '--interactive':
            interactive_mode()
        else:
            try:
                load = float(sys.argv[1])
                run_custom_problem(load)
            except ValueError:
                print(f"Usage: {sys.argv[0]} [load_in_MW | -i]")
                print(f"Example: {sys.argv[0]} 400")
                print(f"         {sys.argv[0]} -i  (interactive mode)")
    else:
        run_default_problem()


if __name__ == "__main__":
    main()

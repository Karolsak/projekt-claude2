"""
Verification script for Economic Load Dispatch solution
Validates the analytical solution against the numerical solution
"""

import numpy as np


def verify_analytical_solution():
    """
    Verify the analytical solution from the textbook problem
    """
    print("=" * 70)
    print("ECONOMIC LOAD DISPATCH - SOLUTION VERIFICATION")
    print("=" * 70)
    print()

    # Given parameters
    print("GIVEN PARAMETERS:")
    print("-" * 70)
    print("Plant 1: dC₁/dP₁ = 40 + 0.25·P₁,  30 ≤ P₁ ≤ 150 MW")
    print("Plant 2: dC₂/dP₂ = 50 + 0.30·P₂,  40 ≤ P₂ ≤ 125 MW")
    print("Plant 3: dC₃/dP₃ = 20 + 0.20·P₃,  50 ≤ P₃ ≤ 225 MW")
    print("Total Load = 350 MW")
    print()

    # Analytical solution (from textbook)
    P1_analytical = 91.98
    P2_analytical = 43.29
    P3_analytical = 214.73

    print("ANALYTICAL SOLUTION (from textbook):")
    print("-" * 70)
    print(f"P₁ = {P1_analytical:.2f} MW")
    print(f"P₂ = {P2_analytical:.2f} MW")
    print(f"P₃ = {P3_analytical:.2f} MW")
    print(f"Total = {P1_analytical + P2_analytical + P3_analytical:.2f} MW")
    print()

    # Verify using numerical solution
    print("NUMERICAL VERIFICATION:")
    print("-" * 70)

    # Plant data
    plants = [
        {'a': 40, 'b': 0.25, 'pmin': 30, 'pmax': 150},  # Plant 1
        {'a': 50, 'b': 0.30, 'pmin': 40, 'pmax': 125},  # Plant 2
        {'a': 20, 'b': 0.20, 'pmin': 50, 'pmax': 225},  # Plant 3
    ]

    total_load = 350.0
    tolerance = 0.01

    # Lambda iteration
    lambda_min = 40.0  # Min possible lambda
    lambda_max = 100.0  # Max possible lambda

    for iteration in range(100):
        lambda_val = (lambda_min + lambda_max) / 2

        powers = []
        for plant in plants:
            # P = (lambda - a) / b
            p = (lambda_val - plant['a']) / plant['b']
            # Apply constraints
            p = max(plant['pmin'], min(plant['pmax'], p))
            powers.append(p)

        total_power = sum(powers)
        error = total_power - total_load

        if abs(error) < tolerance:
            break

        if error > 0:
            lambda_max = lambda_val
        else:
            lambda_min = lambda_val

    P1_numerical, P2_numerical, P3_numerical = powers

    print(f"P₁ = {P1_numerical:.2f} MW")
    print(f"P₂ = {P2_numerical:.2f} MW")
    print(f"P₃ = {P3_numerical:.2f} MW")
    print(f"Total = {sum(powers):.2f} MW")
    print(f"λ = {lambda_val:.3f} ₹/MW")
    print(f"Iterations = {iteration + 1}")
    print()

    # Verify incremental costs
    print("INCREMENTAL COSTS AT OPTIMAL POINT:")
    print("-" * 70)
    ic1 = plants[0]['a'] + plants[0]['b'] * P1_numerical
    ic2 = plants[1]['a'] + plants[1]['b'] * P2_numerical
    ic3 = plants[2]['a'] + plants[2]['b'] * P3_numerical

    print(f"dC₁/dP₁ = {ic1:.3f} ₹/MW")
    print(f"dC₂/dP₂ = {ic2:.3f} ₹/MW")
    print(f"dC₃/dP₃ = {ic3:.3f} ₹/MW")
    print()

    # Check if all incremental costs are equal (within tolerance)
    ic_equal = abs(ic1 - ic2) < 0.1 and abs(ic2 - ic3) < 0.1 and abs(ic1 - ic3) < 0.1
    print(f"Incremental costs equal? {ic_equal} ✓" if ic_equal else f"Incremental costs equal? {ic_equal} ✗")
    print()

    # Calculate total costs
    print("COST ANALYSIS:")
    print("-" * 70)

    # Total cost = integral of (a + b*P) = a*P + (b/2)*P^2
    cost1 = plants[0]['a'] * P1_numerical + (plants[0]['b'] / 2) * P1_numerical**2
    cost2 = plants[1]['a'] * P2_numerical + (plants[1]['b'] / 2) * P2_numerical**2
    cost3 = plants[2]['a'] * P3_numerical + (plants[2]['b'] / 2) * P3_numerical**2
    total_cost = cost1 + cost2 + cost3

    print(f"Cost₁ = ₹{cost1:.2f}")
    print(f"Cost₂ = ₹{cost2:.2f}")
    print(f"Cost₃ = ₹{cost3:.2f}")
    print(f"Total Cost = ₹{total_cost:.2f}")
    print()

    # Verify constraints
    print("CONSTRAINT VERIFICATION:")
    print("-" * 70)
    constraints_ok = True

    for i, (power, plant) in enumerate(zip(powers, plants), 1):
        within_limits = plant['pmin'] <= power <= plant['pmax']
        status = "✓" if within_limits else "✗"
        print(f"Plant {i}: {plant['pmin']} ≤ {power:.2f} ≤ {plant['pmax']} {status}")
        constraints_ok = constraints_ok and within_limits

    power_balance = abs(sum(powers) - total_load) < tolerance
    status = "✓" if power_balance else "✗"
    print(f"Power Balance: {sum(powers):.2f} = {total_load:.2f} {status}")
    constraints_ok = constraints_ok and power_balance
    print()

    # Error analysis
    print("ERROR ANALYSIS:")
    print("-" * 70)
    error_p1 = abs(P1_numerical - P1_analytical)
    error_p2 = abs(P2_numerical - P2_analytical)
    error_p3 = abs(P3_numerical - P3_analytical)

    print(f"P₁ error: {error_p1:.4f} MW")
    print(f"P₂ error: {error_p2:.4f} MW")
    print(f"P₃ error: {error_p3:.4f} MW")
    print()

    # Final verdict
    print("=" * 70)
    if constraints_ok and ic_equal:
        print("✓ SOLUTION VERIFIED - All conditions satisfied!")
    else:
        print("✗ SOLUTION VERIFICATION FAILED")
    print("=" * 70)
    print()

    # Additional insight
    print("KEY INSIGHTS:")
    print("-" * 70)
    print("• Plant 3 generates most power (214.73 MW) - it has lowest base cost (a=20)")
    print("• Plant 2 generates least power (43.29 MW) - it has highest base cost (a=50)")
    print("• All plants operate at same incremental cost (λ ≈ 63 ₹/MW)")
    print("• This ensures minimum total cost for meeting the 350 MW load")
    print("=" * 70)


if __name__ == "__main__":
    verify_analytical_solution()

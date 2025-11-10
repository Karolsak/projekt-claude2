# Economic Load Dispatch Simulator

## Overview

This interactive Python application solves the **Economic Load Dispatch (ELD)** problem for power systems using tkinter GUI and matplotlib visualization. The application allows you to study different operating conditions through interactive sliders and real-time visualization.

## Problem Statement

The system has **3 power plants** that need to supply a total system load of **350 MW**. Each plant has:

### Plant Characteristics

**Plant 1:**
- Incremental Cost: `dC₁/dP₁ = 40 + 0.25·P₁` (₹/MW)
- Constraints: `30 ≤ P₁ ≤ 150` MW

**Plant 2:**
- Incremental Cost: `dC₂/dP₂ = 50 + 0.30·P₂` (₹/MW)
- Constraints: `40 ≤ P₂ ≤ 125` MW

**Plant 3:**
- Incremental Cost: `dC₃/dP₃ = 20 + 0.20·P₃` (₹/MW)
- Constraints: `50 ≤ P₃ ≤ 225` MW

## Solution Method

The application uses the **Equal Incremental Cost Principle** (λ-iteration method):

```
dC₁/dP₁ = dC₂/dP₂ = dC₃/dP₃ = λ
```

### Optimal Solution (for 350 MW load)

- **P₁ = 91.98 MW**
- **P₂ = 43.29 MW**
- **P₃ = 214.73 MW**
- **λ = 63.0 ₹/MW**

## Features

### Interactive Controls

1. **Total Load Slider** (120-500 MW)
   - Adjust the system load demand in real-time
   - See how optimal dispatch changes with load

2. **Plant Parameter Sliders** (for each plant)
   - **Coefficient a**: Base incremental cost (₹/MW)
   - **Coefficient b**: Incremental cost slope (₹/MW²)
   - **Min Power**: Minimum generation limit (MW)
   - **Max Power**: Maximum generation limit (MW)

3. **Reset Button**
   - Restore default problem parameters

### Visualizations

1. **Power Distribution Bar Chart**
   - Shows optimal power output from each plant
   - Color-coded for easy identification

2. **Cost Distribution Pie Chart**
   - Displays percentage of total cost from each plant
   - Helps identify most expensive generators

3. **Incremental Cost Curves**
   - Plots dC/dP vs P for each plant
   - Shows the equal λ line (optimal operating point)
   - Marks current operating points with circles

4. **Total Cost vs Load Curve**
   - Shows how system cost varies with load
   - Marks current operating point

### Results Panel

Displays detailed results including:
- Power output from each plant
- Incremental costs at optimal points
- Individual and total costs
- Lambda (λ) value
- Number of iterations to converge

## Installation

### Requirements

```bash
pip install numpy matplotlib
```

### Standard Library Dependencies
- tkinter (usually included with Python)

## Usage

### Run the Application

```bash
python economic_load_dispatch_simulator.py
```

### How to Use

1. **Start the Application**: The program opens with default parameters (350 MW load)

2. **Adjust Total Load**: Move the "Total Load" slider to study different load conditions

3. **Modify Plant Parameters**:
   - Adjust cost coefficients to simulate different fuel costs
   - Change generation limits to simulate unit outages or derating

4. **Observe Results**:
   - Watch the visualizations update in real-time
   - Read optimal dispatch values in the results panel
   - Notice how λ changes with different conditions

5. **Study Scenarios**:
   - **High Load**: Increase load to 450 MW → observe constraint violations
   - **Low Load**: Decrease to 200 MW → see how dispatch changes
   - **Expensive Plant**: Increase Plant 2's coefficient 'a' → less generation from Plant 2
   - **Unit Outage**: Set a plant's max power to its min → forced redistribution

## Theory

### Economic Dispatch Principle

For optimal (minimum cost) operation:

**All online generators must operate at equal incremental cost (λ)**

This is the necessary condition for optimality, subject to:
- Power balance: ΣPᵢ = Load
- Generator limits: Pmin,i ≤ Pi ≤ Pmax,i

### Cost Function

For each plant, the total cost is:
```
C = a·P + (b/2)·P²
```

The incremental cost is:
```
dC/dP = a + b·P
```

### Lambda Iteration Algorithm

1. Start with λ_min and λ_max bounds
2. For current λ, calculate each plant's output: P = (λ - a) / b
3. Apply constraints (Pmin, Pmax)
4. Check power balance: ΣP vs Load
5. Adjust λ bounds based on error
6. Repeat until convergence

## Educational Value

This simulator helps understand:

✓ **Economic Dispatch Principles**
- How plants with different costs are coordinated
- Why cheaper plants generate more power

✓ **Constraint Effects**
- Impact of generation limits on optimal dispatch
- How constraints force sub-optimal operation

✓ **System Economics**
- Relationship between load and total cost
- Marginal cost of supplying additional load (λ)

✓ **Sensitivity Analysis**
- How fuel cost changes affect dispatch
- Effect of plant availability on system cost

## Example Study Cases

### Case 1: Base Case (Default)
- Load: 350 MW
- Result: P₁=91.98, P₂=43.29, P₃=214.73 MW
- Observation: Plant 3 (cheapest) generates most

### Case 2: High Load
- Load: 450 MW
- Observation: Plants approach maximum limits
- λ increases (higher marginal cost)

### Case 3: Plant 3 Outage
- Set Plant 3: Pmax = 50 MW (minimum)
- Observation: Plants 1 & 2 pick up load
- Total cost increases significantly

### Case 4: Fuel Price Increase
- Increase Plant 1: a = 60 (from 40)
- Observation: Plant 1 generation decreases
- Load shifts to other plants

## Technical Details

### Algorithm Convergence
- Method: Bisection (Lambda iteration)
- Tolerance: 0.01 MW
- Max Iterations: 100
- Typical convergence: 5-15 iterations

### Coordinate Optimization
The problem is solved using the Lagrangian method:
```
L = Σ Cᵢ(Pᵢ) + λ(Load - Σ Pᵢ)
```

Optimality conditions:
```
∂L/∂Pᵢ = dCᵢ/dPᵢ - λ = 0  →  dCᵢ/dPᵢ = λ
∂L/∂λ = Load - Σ Pᵢ = 0
```

## Troubleshooting

### Issue: Window too small
**Solution**: The window is set to 1400x900. Adjust in code line `self.root.geometry("1400x900")`

### Issue: Infeasible solution
**Solution**: Check that sum of Pmin ≤ Load ≤ sum of Pmax

### Issue: tkinter not found
**Solution**: On Linux: `sudo apt-get install python3-tk`

## Extensions

Possible enhancements:
- Add transmission losses (B-coefficients)
- Include ramp rate constraints
- Multi-period optimization
- Add renewable generation
- Economic dispatch with valve-point effects

## References

- Power System Operation and Control (textbook)
- Economic Load Dispatch principles
- Lagrange multiplier optimization

## Author

Created for power systems education and analysis.

## License

Free to use for educational purposes.

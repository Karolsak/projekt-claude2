# Advanced Power Grid Control & Protection Simulator

## Overview

This comprehensive power grid simulator includes advanced control systems, multi-machine operation, protection systems, and reliability analysis. It provides a complete environment for studying power system dynamics, control strategies, and protection coordination.

## Features

### 1. Control System Integration

#### PID Controller
- **Proportional-Integral-Derivative control** for voltage and frequency regulation
- **Tunable parameters**: Kp, Ki, Kd with real-time sliders
- **Anti-windup protection** to prevent integrator saturation
- **Setpoint adjustment** from 59.5 to 60.5 Hz
- **Real-time response** visualization in phase plane plots

#### Fuzzy Logic Controller
- **Fuzzification** of frequency error and rate of change
- **Fuzzy membership functions**: Large Negative, Small Negative, Zero, Small Positive, Large Positive
- **Rule-based inference** system with 15 fuzzy rules
- **Defuzzification** using weighted average method
- **Adjustable fuzziness level** for control sensitivity

#### Control Modes
- **Manual**: Direct user control
- **Auto**: Automatic governor response
- **PID**: PID controller active
- **Fuzzy**: Fuzzy logic controller active

### 2. Multi-Machine and Grid Integration

#### Parallel Generator Operation
- **Three generators** with different ratings (500 MW, 400 MW, 300 MW)
- **Independent control** of each generator (power, voltage, status)
- **Online/offline switching** with dynamic recalculation
- **Real-time monitoring** of power output, loading, and temperature

#### Load Sharing Strategies
- **Equal Sharing**: Distributes load equally among online generators
- **Proportional Sharing**: Distributes based on generator ratings
- **Economic Dispatch**: Optimized distribution for economic operation

#### Grid Synchronization Features
- **Voltage control** for each generator (0.8 - 1.2 pu)
- **Power setpoint control** up to rated capacity
- **Status monitoring** with visual indicators
- **Temperature tracking** for thermal management

### 3. Dynamic and Transient Simulation

#### Advanced ODE Solvers
- **RK45 (Runge-Kutta 4-5)**: Adaptive step-size, high accuracy
- **BDF (Backward Differentiation Formula)**: For stiff systems
- **Euler**: Simple explicit integration (for comparison)
- **Selectable solver** from GUI dropdown

#### System Dynamics Model
- **Frequency dynamics**: Based on swing equation df/dt = (P_gen - P_load) / (2H)
- **Voltage dynamics**: Simplified excitation system model
- **Power dynamics**: Load-frequency response
- **Inertia calculation**: Combined inertia of all online generators

#### Event Simulation
- **Load Changes**: Random ±200 MW disturbances
- **Short Circuits**: Voltage drop to 50%
- **Excitation Faults**: Field voltage reduction to 80%
- **Generator Trips**: Random generator disconnection
- **Event logging**: Timestamped event records

### 4. Protection and Reliability Analysis

#### Protection Systems

##### Overcurrent Protection
- **Adjustable setting**: 100-150% of rated current
- **Per-generator limits**: Based on individual ratings
- **Trip logging** with timestamp and values

##### Voltage Protection
- **Overvoltage**: Adjustable 1.0-1.3 pu
- **Undervoltage**: Adjustable 0.7-0.95 pu
- **Real-time monitoring**
- **Automatic tripping** when limits exceeded

##### Frequency Protection
- **Underfrequency**: Adjustable 59.0-59.9 Hz
- **Load shedding coordination**
- **UFLS (Under-Frequency Load Shedding)** capability

##### Thermal Protection
- **Temperature monitoring** for each generator
- **Thermal time constant**: 600 seconds
- **Maximum temperature**: 120°C
- **Automatic trip** on thermal overload

#### Reliability Analysis

##### MTBF (Mean Time Between Failures)
- **Calculated** as 1/λ where λ is failure rate
- **Stress-dependent**: Accounts for temperature and loading
- **Per-generator values**
- **Visual bar chart** comparison

##### Failure Rate Calculation
```
λ = λ_base × e^((T-75)/50) × (1 + (P/P_rated)²)
```
- **Temperature factor**: Exponential with temperature
- **Load factor**: Quadratic with loading
- **Base rate**: 0.001 failures/hour

##### Reliability Function
```
R(t) = e^(-λt)
```
- **Time-dependent** reliability calculation
- **Plotted over one week** (168 hours)
- **Individual curves** for each generator

##### Derating Analysis
- **Temperature derating**: Reduces capacity above 100°C
- **Voltage derating**: Reduces capacity with low voltage
- **Combined factor**: Minimum of all derating factors
- **Color-coded display**: Green (>0.9), Yellow (>0.7), Red (<0.7)

## GUI Components

### Control System Tab
- Control mode selection (Manual/Auto/PID/Fuzzy)
- PID parameter tuning sliders
- Fuzzy logic settings
- ODE solver selection
- Simulation controls (Start/Stop/Reset)
- Event injection
- Real-time status display
- Multi-plot visualization:
  - System frequency response
  - Voltage profile
  - Power output
  - Frequency deviation
  - Phase plane diagram

### Multi-Machine Tab
- Individual generator controls
- Status indicators (Online/Offline)
- Power setpoint sliders
- Voltage setpoint sliders
- Load sharing buttons
- Real-time plots:
  - Power output comparison
  - Loading percentage
  - Temperature monitoring
  - Online status

### Protection Tab
- Protection setting sliders:
  - Overcurrent (% of rated)
  - Overvoltage (pu)
  - Undervoltage (pu)
  - Underfrequency (Hz)
- Trip log with timestamps
- Clear log button
- Apply settings button

### Reliability Tab
- Per-generator metrics:
  - MTBF (hours)
  - 24-hour reliability
  - Failure rate
  - Derating factor
  - Temperature
- Update metrics button
- Comprehensive plots:
  - MTBF bar chart
  - Reliability vs. time curves
  - Failure rate comparison
  - Derating factor visualization

## Technical Specifications

### System Model

#### Generator Model
- **Rated powers**: 500 MW, 400 MW, 300 MW
- **Inertia constants**: 6.0, 5.0, 4.0 seconds
- **Voltage range**: 0.8 - 1.2 pu
- **Frequency nominal**: 60.0 Hz

#### Control Parameters
- **PID defaults**: Kp=2.0, Ki=0.5, Kd=0.1
- **Control output limits**: ±10.0
- **Setpoint**: 60.0 Hz
- **Sample time**: 0.01 seconds

#### Protection Limits
- **Overcurrent**: 120% rated (default)
- **Overvoltage**: 1.15 pu (default)
- **Undervoltage**: 0.85 pu (default)
- **Underfrequency**: 59.5 Hz (default)
- **Thermal limit**: 120°C

### Numerical Methods

#### RK45 Solver
- **Order**: 4th/5th order Runge-Kutta
- **Error control**: Adaptive step size
- **Accuracy**: High (suitable for most applications)
- **Speed**: Medium

#### BDF Solver
- **Order**: Variable order (1-5)
- **Type**: Implicit multistep method
- **Best for**: Stiff systems
- **Stability**: A-stable

#### Euler Solver
- **Order**: 1st order
- **Type**: Explicit forward Euler
- **Best for**: Simple systems, comparison
- **Speed**: Fast

## Usage Examples

### Example 1: PID Controller Tuning

1. Select **Control System** tab
2. Choose **PID** mode
3. Adjust Kp, Ki, Kd sliders
4. Set desired setpoint (e.g., 60.0 Hz)
5. Click **Start Simulation**
6. Observe frequency response and phase plane
7. **Inject events** to test disturbance rejection

### Example 2: Multi-Machine Load Sharing

1. Select **Multi-Machine** tab
2. Set all generators **Online**
3. Set total load (combined power)
4. Click **Proportional Sharing**
5. Observe power distribution in bar chart
6. Check loading percentages
7. Monitor temperatures

### Example 3: Protection Coordination

1. Select **Protection** tab
2. Set overcurrent to **110%**
3. Set underfrequency to **59.7 Hz**
4. Click **Apply Settings**
5. Go to **Control System** tab
6. **Inject** load change event
7. Monitor trip log for violations

### Example 4: Reliability Assessment

1. Select **Reliability** tab
2. Click **Update Metrics**
3. Review MTBF for each generator
4. Check 24-hour reliability
5. Observe time-dependent curves
6. Check derating factors
7. Adjust operating conditions to improve reliability

## Installation and Requirements

### Required Libraries
```bash
pip install numpy scipy matplotlib tkinter
```

### Running the Simulator
```bash
python power_grid_control_protection_simulator.py
```

## Mathematical Background

### Swing Equation
```
2H * df/dt = P_mech - P_elec
```
Where:
- H = Inertia constant (seconds)
- f = Frequency (Hz)
- P_mech = Mechanical power input (MW)
- P_elec = Electrical power output (MW)

### PID Control Law
```
u(t) = Kp*e(t) + Ki*∫e(t)dt + Kd*de(t)/dt
```
Where:
- e(t) = Setpoint - Measured value
- Kp = Proportional gain
- Ki = Integral gain
- Kd = Derivative gain

### Fuzzy Logic Membership Functions
```
μ(x) = max(0, min(1, (x - a)/(b - a)))
```
Triangular and trapezoidal functions for error and rate.

### Reliability Calculation
```
R(t) = exp(-λ * t)
MTBF = 1 / λ
λ = λ_base * f_temp * f_load
```

## Performance Characteristics

### Computational Efficiency
- **RK45**: ~1000 evaluations for 10-second simulation
- **BDF**: ~500 evaluations for stiff systems
- **Euler**: ~1000 fixed steps
- **Real-time factor**: >100x (simulation faster than real-time)

### Accuracy
- **Frequency**: ±0.001 Hz
- **Voltage**: ±0.01 pu
- **Power**: ±0.1 MW
- **Temperature**: ±0.1°C

## Limitations and Assumptions

1. **Simplified models**: Generators use reduced-order models
2. **Network neglected**: Transmission network impedances not modeled
3. **Linearized voltage**: Voltage dynamics simplified
4. **Steady-state load**: Load assumed constant (no dynamic load model)
5. **Single bus**: All generators connected to single bus
6. **No transformer dynamics**: Transformer models not included

## Future Enhancements

1. **Grid synchronization**: Phase angle synchronization for parallel operation
2. **Anti-islanding**: Detection and prevention of islanding conditions
3. **Detailed network**: Transmission line models with impedances
4. **Dynamic loads**: Motor loads with frequency dependence
5. **AVR models**: Detailed automatic voltage regulator models
6. **Governor models**: Detailed turbine-governor models
7. **Power flow**: AC power flow with reactive power
8. **Transient stability**: Large-disturbance angle stability
9. **Small-signal stability**: Eigenvalue analysis
10. **Economic optimization**: Real-time economic dispatch with cost curves

## References

1. Kundur, P. "Power System Stability and Control", McGraw-Hill, 1994
2. Anderson, P.M., Fouad, A.A. "Power System Control and Stability", IEEE Press, 2003
3. Saadat, H. "Power System Analysis", McGraw-Hill, 1999
4. IEEE Std C37.102 "Guide for AC Generator Protection"
5. NERC Reliability Standards

## License

Educational use only. Not for commercial deployment without validation.

## Author

Created for advanced power systems education and research.

## Support

For questions or issues, please refer to the project documentation or contact the development team.

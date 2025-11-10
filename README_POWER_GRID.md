# Power Grid Frequency Simulator

## Historical Context: November 12, 1992 Event

On November 12, 1992, at 10:09 AM, a large generator on the East Coast tripped out, causing a significant power grid disturbance:

- **System Size**: 18,823 MW interconnected power pool
- **Lost Generation**: 1,050 MW
- **Frequency Drop**: 60 Hz → 59.97 Hz (in seconds)
- **Restoration Time**: 7.5 minutes to return to 60 Hz
- **Recovery Action**: Frequency raised above 60 Hz to recover lost cycles and correct electric clocks

## Problem Calculations

### a. Average Frequency During Restoration
The average frequency is calculated by integrating the frequency curve over the 7.5-minute restoration period:

```
f_avg = (1/T) × ∫[0 to T] f(t) dt
```

For the actual event: **f_avg ≈ 59.985 Hz**

### b. Cycles Generated During Restoration
The number of cycles is the integral of frequency over time (converted to seconds):

```
Cycles = ∫[0 to T] f(t) dt × 60 seconds/minute
```

For the actual event: **~26,993.25 cycles**

### c. Cycles at Normal Frequency
If the frequency had remained at 60 Hz:

```
Cycles_ideal = 60 Hz × 7.5 min × 60 s/min = 27,000 cycles
```

### d. Clock Error

Electric clocks count cycles to measure time. They're designed so:
- 1 minute = 3,600 cycles at 60 Hz
- 1 second = 60 cycles at 60 Hz

**Clock error calculation:**
```
Time shown by clock = Cycles_actual / 60
Actual time elapsed = 7.5 min × 60 s/min = 450 seconds
Clock error = 450 - (26,993.25 / 60) ≈ 0.1125 seconds = 112.5 milliseconds
```

**Minute hand turns:**
```
Turns = Cycles_actual / 3,600 ≈ 7.498125 turns
```

The minute hand made approximately **7.498 turns** instead of 7.5 turns, resulting in a clock that was **~112.5 milliseconds slow**.

## Application Features

### Interactive Sliders
- **Total System Power (MW)**: Adjust the total interconnected system capacity
- **Lost Generation (MW)**: Change the amount of generation lost
- **Initial Frequency (Hz)**: Set the pre-event frequency
- **Minimum Frequency (Hz)**: Control the frequency nadir
- **Restoration Time (min)**: Adjust how long it takes to restore frequency
- **Recovery Time (min)**: Time to bring frequency back to nominal
- **Overshoot Frequency (Hz)**: Frequency during clock correction phase
- **Overshoot Duration (min)**: How long frequency is elevated

### Visualizations

1. **Frequency Response**: Shows the complete frequency trajectory
   - Initial drop phase (exponential)
   - Restoration phase (exponential recovery)
   - Overshoot phase (for clock correction)

2. **Cumulative Cycles**: Compares actual cycles generated vs. ideal cycles at 60 Hz

3. **Cycle Deficit**: Shows the accumulation of lost cycles over time

4. **Frequency Deviation**: Displays deviation from nominal 60 Hz

5. **Clock Error**: Shows how electric clock error accumulates over time

### Real-Time Calculations

The application continuously calculates and displays:
- Average frequency during restoration
- Total cycles generated
- Expected cycles at 60 Hz
- Cycles lost
- Minute hand turns
- Clock error (in seconds and milliseconds)

## Installation & Usage

### Requirements
```bash
pip install numpy matplotlib
```

### Running the Application
```bash
python power_grid_frequency_simulator.py
```

### Using the Simulator

1. **Default Scenario**: Launch the app to see the historical November 12, 1992 event
2. **Adjust Parameters**: Use sliders to explore different scenarios:
   - Larger power loss → greater frequency drop
   - Longer restoration time → more cycles lost
   - Different frequency nadirs → varying system responses
3. **Update**: Click "Update Simulation" to recalculate with new parameters
4. **Reset**: Click "Reset to Default" to return to the 1992 event parameters

## Scenarios to Explore

### Scenario 1: Larger Disturbance
- Increase lost power to 2,000 MW
- Observe deeper frequency drop and longer recovery

### Scenario 2: Faster Response
- Reduce restoration time to 3 minutes
- See how faster governor response reduces cycle loss

### Scenario 3: Weaker System
- Reduce total system power to 12,000 MW
- Same 1,050 MW loss has greater impact

### Scenario 4: Modern Grid
- Reduce restoration time to 2 minutes
- Increase overshoot to 60.05 Hz
- Modern systems respond faster

## Technical Details

### Frequency Response Model

The simulation uses exponential models for realistic frequency dynamics:

**Drop Phase (0-6 seconds):**
```
f(t) = f_min + (f_0 - f_min) × (1 - e^(-t/τ_drop))
```

**Restoration Phase:**
```
f(t) = f_min + (f_0 - f_min) × (1 - e^(-t/τ_restore))
```

**Overshoot Phase:**
```
f(t) = f_0 + (f_overshoot - f_0) × sin(πt/(2T_overshoot))
```

### Why Frequency Drops

When generation is lost:
1. **Power Imbalance**: Generation < Load
2. **Kinetic Energy**: System draws on rotating inertia
3. **Frequency Drop**: As rotors slow, frequency decreases
4. **Governor Response**: Other generators increase output
5. **Restoration**: Frequency gradually returns to normal

### Why Overshoot Correction

The overshoot phase (raising frequency above 60 Hz) serves to:
- Recover lost cycles
- Correct electric clocks
- Compensate for the period of under-frequency operation

## Educational Value

This simulator demonstrates:
- **Grid Stability**: How interconnected systems respond to disturbances
- **Inertia**: The role of rotating mass in frequency stability
- **Governor Action**: Automatic generation control mechanisms
- **Time Standards**: Relationship between frequency and time-keeping
- **System Resilience**: How grids recover from significant events

## References

This simulation is based on the actual November 12, 1992 power grid event documented in electrical engineering textbooks as a classic example of frequency response and grid stability.

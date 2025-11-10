#!/usr/bin/env python3
"""
Demonstration Script - Power Grid Frequency Calculations
Shows all calculations and results without GUI
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from datetime import datetime


def simulate_frequency_response(params):
    """Simulate the frequency response"""
    # Time arrays
    t_drop = np.linspace(0, 0.1, 50)
    t_restore = np.linspace(0.1, params['restoration_time'], 1000)
    t_overshoot = np.linspace(params['restoration_time'],
                              params['restoration_time'] + params['overshoot_time'],
                              500)

    # Phase 1: Exponential drop
    tau_drop = 0.02
    freq_drop = (params['initial_freq'] - params['min_freq']) * \
                (1 - np.exp(-t_drop / tau_drop)) + params['min_freq']

    # Phase 2: Exponential restoration
    tau_restore = params['restoration_time'] / 5
    time_since_drop = t_restore - 0.1
    freq_restore = params['min_freq'] + \
                  (params['initial_freq'] - params['min_freq']) * \
                  (1 - np.exp(-time_since_drop / tau_restore))

    # Phase 3: Overshoot
    t_overshoot_rel = t_overshoot - params['restoration_time']
    freq_overshoot = params['initial_freq'] + \
                    (params['overshoot_freq'] - params['initial_freq']) * \
                    np.sin(np.pi * t_overshoot_rel / (2 * params['overshoot_time']))

    # Combine
    time = np.concatenate([t_drop, t_restore, t_overshoot])
    frequency = np.concatenate([freq_drop, freq_restore, freq_overshoot])

    return time, frequency


def calculate_results(time, frequency, params):
    """Calculate all required results"""
    results = {}

    # Focus on restoration period
    restoration_mask = time <= params['restoration_time']
    time_restore = time[restoration_mask]
    freq_restore = frequency[restoration_mask]

    # a. Average frequency
    results['avg_freq'] = np.trapz(freq_restore, time_restore) / params['restoration_time']

    # b. Cycles generated
    results['cycles_actual'] = np.trapz(freq_restore, time_restore) * 60

    # c. Cycles at 60 Hz
    results['cycles_normal'] = params['initial_freq'] * params['restoration_time'] * 60

    # Cycles lost
    results['cycles_lost'] = results['cycles_normal'] - results['cycles_actual']

    # d. Clock calculations
    cycles_per_turn = 60 * 60
    results['clock_turns'] = results['cycles_actual'] / cycles_per_turn

    clock_time_seconds = results['cycles_actual'] / 60
    actual_time_seconds = params['restoration_time'] * 60
    results['clock_error_s'] = actual_time_seconds - clock_time_seconds
    results['clock_error_ms'] = results['clock_error_s'] * 1000

    results['power_loss_pct'] = (params['lost_power'] / params['total_power']) * 100
    results['freq_drop'] = params['initial_freq'] - params['min_freq']

    return results


def print_results(scenario_name, params, results):
    """Print formatted results"""
    print("\n" + "="*80)
    print(f"SCENARIO: {scenario_name}")
    print("="*80)

    print("\nSYSTEM PARAMETERS:")
    print("-"*80)
    print(f"Total System Power:          {params['total_power']:>10.2f} MW")
    print(f"Lost Generation:             {params['lost_power']:>10.2f} MW")
    print(f"Power Loss Percentage:       {results['power_loss_pct']:>10.2f} %")
    print(f"Initial Frequency:           {params['initial_freq']:>10.4f} Hz")
    print(f"Minimum Frequency:           {params['min_freq']:>10.4f} Hz")
    print(f"Frequency Drop:              {results['freq_drop']:>10.4f} Hz")
    print(f"Restoration Time:            {params['restoration_time']:>10.2f} minutes")

    print("\nCALCULATED RESULTS:")
    print("-"*80)
    print(f"a. Average Frequency:        {results['avg_freq']:>10.6f} Hz")
    print(f"b. Cycles Generated:         {results['cycles_actual']:>10.2f} cycles")
    print(f"c. Cycles @ 60 Hz:           {results['cycles_normal']:>10.2f} cycles")
    print(f"   Cycles Lost:              {results['cycles_lost']:>10.2f} cycles")
    print(f"d. Clock Minute Hand Turns:  {results['clock_turns']:>10.6f} turns")
    print(f"   Expected Turns:           {params['restoration_time']:>10.6f} turns")
    print(f"   Turn Deficit:             {params['restoration_time'] - results['clock_turns']:>10.6f} turns")
    print(f"   Clock Error:              {results['clock_error_s']:>10.6f} seconds")
    print(f"   Clock Error:              {results['clock_error_ms']:>10.2f} milliseconds")

    print("\nINTERPRETATION:")
    print("-"*80)
    print(f"• The frequency dropped by {results['freq_drop']:.4f} Hz due to loss of")
    print(f"  {params['lost_power']:.0f} MW ({results['power_loss_pct']:.2f}% of system capacity)")
    print(f"• During the {params['restoration_time']:.1f}-minute restoration period,")
    print(f"  {results['cycles_lost']:.2f} AC cycles were lost")
    print(f"• Electric clocks ran slow by {results['clock_error_ms']:.2f} milliseconds")
    print(f"• The minute hand completed {results['clock_turns']:.6f} turns instead of")
    print(f"  the expected {params['restoration_time']:.6f} turns")

    # Calculate overshoot needed
    if results['cycles_lost'] > 0:
        overshoot_needed = results['cycles_lost'] / (params['overshoot_time'] * 60)
        freq_needed = params['initial_freq'] + overshoot_needed
        print(f"\nOVERSHOOT CORRECTION:")
        print(f"• To recover {results['cycles_lost']:.2f} lost cycles in {params['overshoot_time']:.1f} minutes:")
        print(f"  Required frequency: {freq_needed:.4f} Hz")
        print(f"  Planned overshoot: {params['overshoot_freq']:.4f} Hz")

        cycles_recovered = (params['overshoot_freq'] - params['initial_freq']) * params['overshoot_time'] * 60
        print(f"  Cycles that will be recovered: {cycles_recovered:.2f} cycles")
        remaining_error = (results['cycles_lost'] - cycles_recovered) / 60
        print(f"  Remaining clock error after correction: {remaining_error*1000:.2f} ms")


def save_plots(scenarios_data, filename='frequency_analysis.png'):
    """Create and save comprehensive plots"""
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.25)

    colors = plt.cm.tab10(np.linspace(0, 1, len(scenarios_data)))

    # Plot 1: Frequency Comparison
    ax1 = fig.add_subplot(gs[0, :])
    for i, (name, data) in enumerate(scenarios_data.items()):
        ax1.plot(data['time'], data['frequency'], linewidth=2.5,
                label=name, color=colors[i])
    ax1.axhline(y=60.0, color='k', linestyle='--', alpha=0.3, label='Nominal 60 Hz')
    ax1.set_xlabel('Time (minutes)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Frequency (Hz)', fontsize=12, fontweight='bold')
    ax1.set_title('Power Grid Frequency Response - Multiple Scenarios', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle=':')
    ax1.legend(loc='best', fontsize=9)

    # Plot 2: Cycles Lost Comparison
    ax2 = fig.add_subplot(gs[1, 0])
    names = list(scenarios_data.keys())
    cycles_lost = [scenarios_data[name]['results']['cycles_lost'] for name in names]
    bars = ax2.bar(range(len(names)), cycles_lost, color=colors)
    ax2.set_xticks(range(len(names)))
    ax2.set_xticklabels(names, rotation=45, ha='right', fontsize=9)
    ax2.set_ylabel('Cycles Lost', fontsize=11, fontweight='bold')
    ax2.set_title('Cycles Lost Comparison', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}', ha='center', va='bottom', fontsize=8)

    # Plot 3: Clock Error Comparison
    ax3 = fig.add_subplot(gs[1, 1])
    clock_errors = [scenarios_data[name]['results']['clock_error_ms'] for name in names]
    bars = ax3.bar(range(len(names)), clock_errors, color=colors)
    ax3.set_xticks(range(len(names)))
    ax3.set_xticklabels(names, rotation=45, ha='right', fontsize=9)
    ax3.set_ylabel('Clock Error (ms)', fontsize=11, fontweight='bold')
    ax3.set_title('Clock Error Comparison', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')

    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom', fontsize=8)

    # Plot 4: Average Frequency Comparison
    ax4 = fig.add_subplot(gs[2, 0])
    avg_freqs = [scenarios_data[name]['results']['avg_freq'] for name in names]
    bars = ax4.bar(range(len(names)), avg_freqs, color=colors)
    ax4.axhline(y=60.0, color='r', linestyle='--', alpha=0.5, label='Nominal 60 Hz')
    ax4.set_xticks(range(len(names)))
    ax4.set_xticklabels(names, rotation=45, ha='right', fontsize=9)
    ax4.set_ylabel('Average Frequency (Hz)', fontsize=11, fontweight='bold')
    ax4.set_title('Average Frequency During Restoration', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    ax4.legend()

    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}', ha='center', va='bottom', fontsize=7)

    # Plot 5: Frequency Drop Comparison
    ax5 = fig.add_subplot(gs[2, 1])
    freq_drops = [scenarios_data[name]['results']['freq_drop'] for name in names]
    bars = ax5.bar(range(len(names)), freq_drops, color=colors)
    ax5.set_xticks(range(len(names)))
    ax5.set_xticklabels(names, rotation=45, ha='right', fontsize=9)
    ax5.set_ylabel('Frequency Drop (Hz)', fontsize=11, fontweight='bold')
    ax5.set_title('Frequency Nadir Comparison', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='y')

    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}', ha='center', va='bottom', fontsize=7)

    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"\n📊 Plots saved to: {filename}")


def main():
    """Main demonstration"""
    print("\n" + "="*80)
    print("POWER GRID FREQUENCY SIMULATOR - CALCULATION DEMONSTRATION")
    print("November 12, 1992 East Coast Power Grid Event Analysis")
    print("="*80)

    # Define scenarios
    scenarios = {
        "1992 East Coast Event": {
            'total_power': 18823,
            'lost_power': 1050,
            'initial_freq': 60.0,
            'min_freq': 59.97,
            'restoration_time': 7.5,
            'recovery_time': 6.0,
            'overshoot_freq': 60.03,
            'overshoot_time': 3.0
        },
        "Large Disturbance": {
            'total_power': 18823,
            'lost_power': 2500,
            'initial_freq': 60.0,
            'min_freq': 59.90,
            'restoration_time': 12.0,
            'recovery_time': 8.0,
            'overshoot_freq': 60.05,
            'overshoot_time': 5.0
        },
        "Small Disturbance": {
            'total_power': 18823,
            'lost_power': 300,
            'initial_freq': 60.0,
            'min_freq': 59.99,
            'restoration_time': 3.0,
            'recovery_time': 2.0,
            'overshoot_freq': 60.01,
            'overshoot_time': 1.5
        },
        "Modern Fast Response": {
            'total_power': 25000,
            'lost_power': 1050,
            'initial_freq': 60.0,
            'min_freq': 59.985,
            'restoration_time': 2.0,
            'recovery_time': 1.5,
            'overshoot_freq': 60.015,
            'overshoot_time': 1.0
        }
    }

    # Process each scenario
    scenarios_data = {}

    for name, params in scenarios.items():
        # Simulate
        time, frequency = simulate_frequency_response(params)
        results = calculate_results(time, frequency, params)

        # Store
        scenarios_data[name] = {
            'params': params,
            'time': time,
            'frequency': frequency,
            'results': results
        }

        # Print
        print_results(name, params, results)

    # Create plots
    print("\n" + "="*80)
    print("Generating comparison plots...")
    print("="*80)
    save_plots(scenarios_data)

    print("\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80)
    print("\nTo run the interactive simulators:")
    print("  python power_grid_frequency_simulator.py          (basic)")
    print("  python power_grid_simulator_advanced.py           (advanced)")
    print("\nFor detailed explanations, see:")
    print("  SOLUTIONS.md       - Mathematical solutions")
    print("  QUICKSTART.md      - Usage guide")
    print("  README_POWER_GRID.md - Comprehensive documentation")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

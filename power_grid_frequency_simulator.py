"""
Power Grid Frequency Simulator
Based on the November 12, 1992 East Coast Power Grid Event
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec


class PowerGridSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Power Grid Frequency Simulator - Nov 12, 1992 Event")
        self.root.geometry("1400x900")

        # Default parameters (from the original event)
        self.params = {
            'total_power': 18823,      # MW
            'lost_power': 1050,        # MW
            'initial_freq': 60.0,      # Hz
            'min_freq': 59.97,         # Hz
            'restoration_time': 7.5,   # minutes
            'recovery_time': 6.0,      # minutes (time to bring freq above 60)
            'overshoot_freq': 60.03,   # Hz (frequency during clock correction)
            'overshoot_time': 3.0      # minutes (duration of overshoot)
        }

        self.setup_ui()
        self.update_simulation()

    def setup_ui(self):
        # Create main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel for controls
        control_frame = ttk.LabelFrame(main_frame, text="Simulation Parameters", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Right panel for plots
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create sliders
        self.sliders = {}
        slider_configs = [
            ('total_power', 'Total System Power (MW)', 10000, 30000, 18823),
            ('lost_power', 'Lost Generation (MW)', 100, 3000, 1050),
            ('initial_freq', 'Initial Frequency (Hz)', 59.5, 60.5, 60.0),
            ('min_freq', 'Minimum Frequency (Hz)', 59.5, 60.0, 59.97),
            ('restoration_time', 'Restoration Time (min)', 1.0, 15.0, 7.5),
            ('recovery_time', 'Recovery Time (min)', 1.0, 10.0, 6.0),
            ('overshoot_freq', 'Overshoot Frequency (Hz)', 60.0, 60.1, 60.03),
            ('overshoot_time', 'Overshoot Duration (min)', 0.5, 10.0, 3.0)
        ]

        for i, (key, label, min_val, max_val, default) in enumerate(slider_configs):
            frame = ttk.Frame(control_frame)
            frame.pack(fill=tk.X, pady=5)

            ttk.Label(frame, text=label, width=25, anchor='w').pack()

            value_label = ttk.Label(frame, text=f"{default:.2f}", width=10)
            value_label.pack()

            slider = ttk.Scale(frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL,
                             command=lambda v, k=key, vl=value_label: self.on_slider_change(k, v, vl))
            slider.set(default)
            slider.pack(fill=tk.X)

            self.sliders[key] = (slider, value_label)

        # Update button
        ttk.Button(control_frame, text="Update Simulation",
                  command=self.update_simulation).pack(pady=10, fill=tk.X)

        # Reset button
        ttk.Button(control_frame, text="Reset to Default",
                  command=self.reset_parameters).pack(pady=5, fill=tk.X)

        # Results display
        results_frame = ttk.LabelFrame(control_frame, text="Calculated Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.result_labels = {}
        result_keys = [
            ('avg_freq', 'Average Frequency (Hz):'),
            ('cycles_actual', 'Cycles Generated:'),
            ('cycles_normal', 'Cycles @ 60Hz:'),
            ('cycles_lost', 'Cycles Lost:'),
            ('clock_turns', 'Clock Minute Hand Turns:'),
            ('clock_error_s', 'Clock Error (seconds):'),
            ('clock_error_ms', 'Clock Error (milliseconds):')
        ]

        for key, label in result_keys:
            frame = ttk.Frame(results_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=label, width=25, anchor='w').pack(side=tk.LEFT)
            value_label = ttk.Label(frame, text="0.00", width=15, anchor='e',
                                   font=('Arial', 9, 'bold'))
            value_label.pack(side=tk.RIGHT)
            self.result_labels[key] = value_label

        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def on_slider_change(self, key, value, label):
        val = float(value)
        self.params[key] = val
        label.config(text=f"{val:.2f}")

    def reset_parameters(self):
        defaults = {
            'total_power': 18823,
            'lost_power': 1050,
            'initial_freq': 60.0,
            'min_freq': 59.97,
            'restoration_time': 7.5,
            'recovery_time': 6.0,
            'overshoot_freq': 60.03,
            'overshoot_time': 3.0
        }

        for key, value in defaults.items():
            slider, label = self.sliders[key]
            slider.set(value)
            label.config(text=f"{value:.2f}")
            self.params[key] = value

        self.update_simulation()

    def simulate_frequency_response(self):
        """
        Simulate the frequency response with three phases:
        1. Initial drop (exponential)
        2. Restoration period (exponential recovery)
        3. Overshoot period (to correct clock)
        """
        # Time arrays
        t_drop = np.linspace(0, 0.1, 50)  # First 6 seconds - rapid drop
        t_restore = np.linspace(0.1, self.params['restoration_time'], 1000)
        t_overshoot = np.linspace(self.params['restoration_time'],
                                  self.params['restoration_time'] + self.params['overshoot_time'],
                                  500)

        # Phase 1: Exponential drop
        tau_drop = 0.02  # Time constant for drop (minutes)
        freq_drop = (self.params['initial_freq'] - self.params['min_freq']) * \
                    (1 - np.exp(-t_drop / tau_drop)) + self.params['min_freq']

        # Phase 2: Exponential restoration
        tau_restore = self.params['restoration_time'] / 5  # Time constant
        time_since_drop = t_restore - 0.1
        freq_restore = self.params['min_freq'] + \
                      (self.params['initial_freq'] - self.params['min_freq']) * \
                      (1 - np.exp(-time_since_drop / tau_restore))

        # Phase 3: Overshoot for clock correction
        t_overshoot_rel = t_overshoot - self.params['restoration_time']
        freq_overshoot = self.params['initial_freq'] + \
                        (self.params['overshoot_freq'] - self.params['initial_freq']) * \
                        np.sin(np.pi * t_overshoot_rel / (2 * self.params['overshoot_time']))

        # Combine all phases
        time = np.concatenate([t_drop, t_restore, t_overshoot])
        frequency = np.concatenate([freq_drop, freq_restore, freq_overshoot])

        return time, frequency

    def calculate_results(self, time, frequency):
        """Calculate all required results"""
        results = {}

        # Focus on the restoration period (first 7.5 minutes)
        restoration_mask = time <= self.params['restoration_time']
        time_restore = time[restoration_mask]
        freq_restore = frequency[restoration_mask]

        # a. Average frequency during restoration period
        results['avg_freq'] = np.trapz(freq_restore, time_restore) / self.params['restoration_time']

        # b. Number of cycles during restoration period
        # Cycles = integral of frequency over time
        # Convert minutes to seconds: multiply by 60
        results['cycles_actual'] = np.trapz(freq_restore, time_restore) * 60

        # c. Number of cycles at 60 Hz
        results['cycles_normal'] = self.params['initial_freq'] * self.params['restoration_time'] * 60

        # Cycles lost
        results['cycles_lost'] = results['cycles_normal'] - results['cycles_actual']

        # d. Clock calculations
        # Electric clocks count cycles. One turn of minute hand = 60 seconds = 3600 cycles at 60 Hz
        cycles_per_turn = 60 * 60  # 3600 cycles per minute of actual time
        results['clock_turns'] = results['cycles_actual'] / cycles_per_turn

        # Time error
        # Actual time shown by clock = cycles / (60 cycles/second)
        clock_time_seconds = results['cycles_actual'] / 60
        actual_time_seconds = self.params['restoration_time'] * 60
        results['clock_error_s'] = actual_time_seconds - clock_time_seconds
        results['clock_error_ms'] = results['clock_error_s'] * 1000

        return results

    def update_simulation(self):
        """Update the simulation and plots"""
        # Simulate frequency response
        time, frequency = self.simulate_frequency_response()

        # Calculate results
        results = self.calculate_results(time, frequency)

        # Update result labels
        self.result_labels['avg_freq'].config(text=f"{results['avg_freq']:.6f}")
        self.result_labels['cycles_actual'].config(text=f"{results['cycles_actual']:.2f}")
        self.result_labels['cycles_normal'].config(text=f"{results['cycles_normal']:.2f}")
        self.result_labels['cycles_lost'].config(text=f"{results['cycles_lost']:.2f}")
        self.result_labels['clock_turns'].config(text=f"{results['clock_turns']:.6f}")
        self.result_labels['clock_error_s'].config(text=f"{results['clock_error_s']:.6f}")
        self.result_labels['clock_error_ms'].config(text=f"{results['clock_error_ms']:.2f}")

        # Update plots
        self.plot_results(time, frequency, results)

    def plot_results(self, time, frequency, results):
        """Create comprehensive visualization"""
        self.fig.clear()

        # Create grid layout
        gs = gridspec.GridSpec(3, 2, figure=self.fig, hspace=0.3, wspace=0.3)

        # Plot 1: Frequency vs Time
        ax1 = self.fig.add_subplot(gs[0, :])
        ax1.plot(time, frequency, 'b-', linewidth=2, label='Frequency')
        ax1.axhline(y=60.0, color='g', linestyle='--', alpha=0.5, label='Nominal 60 Hz')
        ax1.axhline(y=self.params['min_freq'], color='r', linestyle='--',
                   alpha=0.5, label=f'Minimum {self.params["min_freq"]} Hz')
        ax1.axvline(x=self.params['restoration_time'], color='orange',
                   linestyle='--', alpha=0.5, label='Restoration Complete')
        ax1.set_xlabel('Time (minutes)', fontsize=10)
        ax1.set_ylabel('Frequency (Hz)', fontsize=10)
        ax1.set_title('Power Grid Frequency Response', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='best', fontsize=8)

        # Plot 2: Cumulative Cycles
        cumulative_cycles = np.cumsum(frequency[:-1] * np.diff(time) * 60)
        cumulative_cycles = np.insert(cumulative_cycles, 0, 0)

        ideal_cycles = 60 * time * 60

        ax2 = self.fig.add_subplot(gs[1, 0])
        ax2.plot(time, cumulative_cycles, 'b-', linewidth=2, label='Actual Cycles')
        ax2.plot(time, ideal_cycles, 'g--', linewidth=2, alpha=0.7, label='Ideal @ 60 Hz')
        ax2.set_xlabel('Time (minutes)', fontsize=10)
        ax2.set_ylabel('Cumulative Cycles', fontsize=10)
        ax2.set_title('Cumulative Cycles Generated', fontsize=11, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='best', fontsize=8)

        # Plot 3: Cycle Deficit
        cycle_deficit = ideal_cycles - cumulative_cycles

        ax3 = self.fig.add_subplot(gs[1, 1])
        ax3.plot(time, cycle_deficit, 'r-', linewidth=2)
        ax3.fill_between(time, 0, cycle_deficit, alpha=0.3, color='red')
        ax3.set_xlabel('Time (minutes)', fontsize=10)
        ax3.set_ylabel('Cycles Lost', fontsize=10)
        ax3.set_title('Cycle Deficit Over Time', fontsize=11, fontweight='bold')
        ax3.grid(True, alpha=0.3)

        # Plot 4: Frequency Deviation
        freq_deviation = frequency - 60.0

        ax4 = self.fig.add_subplot(gs[2, 0])
        colors = ['red' if f < 0 else 'green' for f in freq_deviation]
        ax4.fill_between(time, 0, freq_deviation, alpha=0.5, color='blue')
        ax4.plot(time, freq_deviation, 'b-', linewidth=2)
        ax4.axhline(y=0, color='k', linestyle='-', alpha=0.5)
        ax4.set_xlabel('Time (minutes)', fontsize=10)
        ax4.set_ylabel('Deviation (Hz)', fontsize=10)
        ax4.set_title('Frequency Deviation from 60 Hz', fontsize=11, fontweight='bold')
        ax4.grid(True, alpha=0.3)

        # Plot 5: Clock Error
        clock_time = cumulative_cycles / 60  # seconds shown on clock
        actual_time = time * 60  # actual seconds elapsed
        clock_error = actual_time - clock_time

        ax5 = self.fig.add_subplot(gs[2, 1])
        ax5.plot(time, clock_error, 'purple', linewidth=2)
        ax5.fill_between(time, 0, clock_error, alpha=0.3, color='purple')
        ax5.set_xlabel('Time (minutes)', fontsize=10)
        ax5.set_ylabel('Clock Error (seconds)', fontsize=10)
        ax5.set_title('Electric Clock Error Over Time', fontsize=11, fontweight='bold')
        ax5.grid(True, alpha=0.3)

        self.canvas.draw()


def main():
    root = tk.Tk()
    app = PowerGridSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()

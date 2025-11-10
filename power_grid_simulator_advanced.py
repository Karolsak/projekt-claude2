"""
Advanced Power Grid Frequency Simulator
With Scenario Presets, Export, and Comparison Features
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
from datetime import datetime
import json


class AdvancedPowerGridSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Power Grid Frequency Simulator")
        self.root.geometry("1600x950")

        # Scenario presets
        self.scenarios = {
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
            "Weak Grid": {
                'total_power': 10000,
                'lost_power': 1050,
                'initial_freq': 60.0,
                'min_freq': 59.92,
                'restoration_time': 10.0,
                'recovery_time': 7.0,
                'overshoot_freq': 60.04,
                'overshoot_time': 4.0
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
            },
            "Critical Under-frequency": {
                'total_power': 15000,
                'lost_power': 2000,
                'initial_freq': 60.0,
                'min_freq': 59.85,
                'restoration_time': 15.0,
                'recovery_time': 10.0,
                'overshoot_freq': 60.06,
                'overshoot_time': 6.0
            }
        }

        # Default parameters
        self.params = self.scenarios["1992 East Coast Event"].copy()

        # Storage for comparison
        self.comparison_data = []

        self.setup_ui()
        self.update_simulation()

    def setup_ui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: Main Simulator
        sim_tab = ttk.Frame(notebook)
        notebook.add(sim_tab, text="Simulator")
        self.setup_simulator_tab(sim_tab)

        # Tab 2: Comparison
        comp_tab = ttk.Frame(notebook)
        notebook.add(comp_tab, text="Scenario Comparison")
        self.setup_comparison_tab(comp_tab)

        # Tab 3: Analysis
        analysis_tab = ttk.Frame(notebook)
        notebook.add(analysis_tab, text="Detailed Analysis")
        self.setup_analysis_tab(analysis_tab)

    def setup_simulator_tab(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Scenario selection
        scenario_frame = ttk.LabelFrame(left_panel, text="Preset Scenarios", padding=10)
        scenario_frame.pack(fill=tk.X, pady=(0, 10))

        self.scenario_var = tk.StringVar(value="1992 East Coast Event")
        scenario_combo = ttk.Combobox(scenario_frame, textvariable=self.scenario_var,
                                     values=list(self.scenarios.keys()),
                                     state='readonly', width=25)
        scenario_combo.pack(fill=tk.X, pady=5)
        scenario_combo.bind('<<ComboboxSelected>>', self.load_scenario)

        ttk.Button(scenario_frame, text="Load Scenario",
                  command=lambda: self.load_scenario(None)).pack(fill=tk.X, pady=2)
        ttk.Button(scenario_frame, text="Add to Comparison",
                  command=self.add_to_comparison).pack(fill=tk.X, pady=2)

        # Control panel
        control_frame = ttk.LabelFrame(left_panel, text="Parameters", padding=10)
        control_frame.pack(fill=tk.BOTH, expand=True)

        # Create sliders
        self.sliders = {}
        slider_configs = [
            ('total_power', 'System Power (MW)', 5000, 30000, 18823),
            ('lost_power', 'Lost Gen (MW)', 100, 5000, 1050),
            ('initial_freq', 'Initial (Hz)', 59.5, 60.5, 60.0),
            ('min_freq', 'Minimum (Hz)', 59.5, 60.0, 59.97),
            ('restoration_time', 'Restore (min)', 1.0, 20.0, 7.5),
            ('recovery_time', 'Recovery (min)', 0.5, 10.0, 6.0),
            ('overshoot_freq', 'Overshoot (Hz)', 60.0, 60.15, 60.03),
            ('overshoot_time', 'Overshoot (min)', 0.5, 10.0, 3.0)
        ]

        for key, label, min_val, max_val, default in slider_configs:
            frame = ttk.Frame(control_frame)
            frame.pack(fill=tk.X, pady=3)

            ttk.Label(frame, text=label, width=18, anchor='w', font=('Arial', 8)).pack()

            value_label = ttk.Label(frame, text=f"{default:.2f}", width=10, font=('Arial', 8, 'bold'))
            value_label.pack()

            slider = ttk.Scale(frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL,
                             command=lambda v, k=key, vl=value_label: self.on_slider_change(k, v, vl))
            slider.set(default)
            slider.pack(fill=tk.X)

            self.sliders[key] = (slider, value_label)

        # Buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="Update",
                  command=self.update_simulation).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Reset",
                  command=self.reset_parameters).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Export Data",
                  command=self.export_data).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Export Plot",
                  command=self.export_plot).pack(fill=tk.X, pady=2)

        # Results display
        results_frame = ttk.LabelFrame(left_panel, text="Results", padding=10)
        results_frame.pack(fill=tk.X, pady=10)

        self.result_labels = {}
        result_keys = [
            ('avg_freq', 'Avg Freq (Hz):'),
            ('cycles_actual', 'Cycles:'),
            ('cycles_lost', 'Lost:'),
            ('clock_error_ms', 'Error (ms):'),
            ('power_loss_pct', 'Loss %:'),
            ('freq_drop', 'Drop (Hz):')
        ]

        for key, label in result_keys:
            frame = ttk.Frame(results_frame)
            frame.pack(fill=tk.X, pady=1)
            ttk.Label(frame, text=label, width=15, anchor='w', font=('Arial', 8)).pack(side=tk.LEFT)
            value_label = ttk.Label(frame, text="0.00", width=12, anchor='e',
                                   font=('Arial', 8, 'bold'), foreground='blue')
            value_label.pack(side=tk.RIGHT)
            self.result_labels[key] = value_label

        # Right panel - plots
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(11, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_comparison_tab(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Comparison Controls", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(control_frame, text="Stored Scenarios:",
                 font=('Arial', 10, 'bold')).pack(pady=5)

        # Listbox for scenarios
        list_frame = ttk.Frame(control_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.comparison_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                            height=15, width=30)
        self.comparison_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.comparison_listbox.yview)

        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Clear All",
                  command=self.clear_comparison).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Remove Selected",
                  command=self.remove_selected).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Compare All",
                  command=self.plot_comparison).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Quick Compare All Presets",
                  command=self.quick_compare_all).pack(fill=tk.X, pady=2)

        # Plot area
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.comp_fig = Figure(figsize=(11, 8), dpi=100)
        self.comp_canvas = FigureCanvasTkAgg(self.comp_fig, master=plot_frame)
        self.comp_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_analysis_tab(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Analysis text
        text_frame = ttk.LabelFrame(main_frame, text="Detailed Analysis Report", padding=10)
        text_frame.pack(fill=tk.BOTH, expand=True)

        # Scrolled text widget
        scroll_y = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        scroll_x = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.analysis_text = tk.Text(text_frame, wrap=tk.NONE,
                                     yscrollcommand=scroll_y.set,
                                     xscrollcommand=scroll_x.set,
                                     font=('Courier', 9))
        self.analysis_text.pack(fill=tk.BOTH, expand=True)

        scroll_y.config(command=self.analysis_text.yview)
        scroll_x.config(command=self.analysis_text.xview)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Generate Analysis Report",
                  command=self.generate_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Export Report",
                  command=self.export_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear",
                  command=lambda: self.analysis_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)

    def on_slider_change(self, key, value, label):
        val = float(value)
        self.params[key] = val
        label.config(text=f"{val:.2f}")

    def load_scenario(self, event):
        scenario_name = self.scenario_var.get()
        if scenario_name in self.scenarios:
            self.params = self.scenarios[scenario_name].copy()

            for key, value in self.params.items():
                if key in self.sliders:
                    slider, label = self.sliders[key]
                    slider.set(value)
                    label.config(text=f"{value:.2f}")

            self.update_simulation()

    def reset_parameters(self):
        self.load_scenario(None)

    def simulate_frequency_response(self):
        """Simulate frequency response"""
        t_drop = np.linspace(0, 0.1, 50)
        t_restore = np.linspace(0.1, self.params['restoration_time'], 1000)
        t_overshoot = np.linspace(self.params['restoration_time'],
                                  self.params['restoration_time'] + self.params['overshoot_time'],
                                  500)

        tau_drop = 0.02
        freq_drop = (self.params['initial_freq'] - self.params['min_freq']) * \
                    (1 - np.exp(-t_drop / tau_drop)) + self.params['min_freq']

        tau_restore = self.params['restoration_time'] / 5
        time_since_drop = t_restore - 0.1
        freq_restore = self.params['min_freq'] + \
                      (self.params['initial_freq'] - self.params['min_freq']) * \
                      (1 - np.exp(-time_since_drop / tau_restore))

        t_overshoot_rel = t_overshoot - self.params['restoration_time']
        freq_overshoot = self.params['initial_freq'] + \
                        (self.params['overshoot_freq'] - self.params['initial_freq']) * \
                        np.sin(np.pi * t_overshoot_rel / (2 * self.params['overshoot_time']))

        time = np.concatenate([t_drop, t_restore, t_overshoot])
        frequency = np.concatenate([freq_drop, freq_restore, freq_overshoot])

        return time, frequency

    def calculate_results(self, time, frequency):
        """Calculate all results"""
        results = {}

        restoration_mask = time <= self.params['restoration_time']
        time_restore = time[restoration_mask]
        freq_restore = frequency[restoration_mask]

        results['avg_freq'] = np.trapz(freq_restore, time_restore) / self.params['restoration_time']
        results['cycles_actual'] = np.trapz(freq_restore, time_restore) * 60
        results['cycles_normal'] = self.params['initial_freq'] * self.params['restoration_time'] * 60
        results['cycles_lost'] = results['cycles_normal'] - results['cycles_actual']

        cycles_per_turn = 60 * 60
        results['clock_turns'] = results['cycles_actual'] / cycles_per_turn

        clock_time_seconds = results['cycles_actual'] / 60
        actual_time_seconds = self.params['restoration_time'] * 60
        results['clock_error_s'] = actual_time_seconds - clock_time_seconds
        results['clock_error_ms'] = results['clock_error_s'] * 1000

        results['power_loss_pct'] = (self.params['lost_power'] / self.params['total_power']) * 100
        results['freq_drop'] = self.params['initial_freq'] - self.params['min_freq']

        return results

    def update_simulation(self):
        """Update simulation"""
        time, frequency = self.simulate_frequency_response()
        results = self.calculate_results(time, frequency)

        # Store for later use
        self.current_time = time
        self.current_frequency = frequency
        self.current_results = results

        # Update labels
        self.result_labels['avg_freq'].config(text=f"{results['avg_freq']:.6f}")
        self.result_labels['cycles_actual'].config(text=f"{results['cycles_actual']:.2f}")
        self.result_labels['cycles_lost'].config(text=f"{results['cycles_lost']:.2f}")
        self.result_labels['clock_error_ms'].config(text=f"{results['clock_error_ms']:.2f}")
        self.result_labels['power_loss_pct'].config(text=f"{results['power_loss_pct']:.2f}")
        self.result_labels['freq_drop'].config(text=f"{results['freq_drop']:.4f}")

        self.plot_results(time, frequency, results)

    def plot_results(self, time, frequency, results):
        """Plot results"""
        self.fig.clear()
        gs = gridspec.GridSpec(3, 2, figure=self.fig, hspace=0.35, wspace=0.3)

        # Plot 1: Frequency vs Time
        ax1 = self.fig.add_subplot(gs[0, :])
        ax1.plot(time, frequency, 'b-', linewidth=2.5, label='Frequency')
        ax1.axhline(y=60.0, color='g', linestyle='--', alpha=0.5, linewidth=1.5, label='Nominal 60 Hz')
        ax1.axhline(y=self.params['min_freq'], color='r', linestyle='--',
                   alpha=0.5, linewidth=1.5, label=f'Minimum {self.params["min_freq"]:.3f} Hz')
        ax1.axvline(x=self.params['restoration_time'], color='orange',
                   linestyle='--', alpha=0.5, linewidth=1.5, label='Restoration Complete')
        ax1.set_xlabel('Time (minutes)', fontsize=10, fontweight='bold')
        ax1.set_ylabel('Frequency (Hz)', fontsize=10, fontweight='bold')
        ax1.set_title('Power Grid Frequency Response', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle=':')
        ax1.legend(loc='best', fontsize=8, framealpha=0.9)
        ax1.set_ylim([min(frequency) - 0.01, max(frequency) + 0.01])

        # Plot 2: Cumulative Cycles
        cumulative_cycles = np.cumsum(frequency[:-1] * np.diff(time) * 60)
        cumulative_cycles = np.insert(cumulative_cycles, 0, 0)
        ideal_cycles = 60 * time * 60

        ax2 = self.fig.add_subplot(gs[1, 0])
        ax2.plot(time, cumulative_cycles, 'b-', linewidth=2, label='Actual')
        ax2.plot(time, ideal_cycles, 'g--', linewidth=2, alpha=0.7, label='Ideal @ 60 Hz')
        ax2.fill_between(time, cumulative_cycles, ideal_cycles, alpha=0.2, color='red')
        ax2.set_xlabel('Time (minutes)', fontsize=9, fontweight='bold')
        ax2.set_ylabel('Cumulative Cycles', fontsize=9, fontweight='bold')
        ax2.set_title('Cumulative Cycles Generated', fontsize=10, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle=':')
        ax2.legend(loc='best', fontsize=8)

        # Plot 3: Cycle Deficit
        cycle_deficit = ideal_cycles - cumulative_cycles

        ax3 = self.fig.add_subplot(gs[1, 1])
        ax3.plot(time, cycle_deficit, 'r-', linewidth=2.5)
        ax3.fill_between(time, 0, cycle_deficit, alpha=0.3, color='red')
        ax3.set_xlabel('Time (minutes)', fontsize=9, fontweight='bold')
        ax3.set_ylabel('Cycles Lost', fontsize=9, fontweight='bold')
        ax3.set_title(f'Total Loss: {results["cycles_lost"]:.2f} cycles', fontsize=10, fontweight='bold')
        ax3.grid(True, alpha=0.3, linestyle=':')

        # Plot 4: Frequency Deviation
        freq_deviation = frequency - 60.0

        ax4 = self.fig.add_subplot(gs[2, 0])
        ax4.fill_between(time, 0, freq_deviation, alpha=0.4, color='blue')
        ax4.plot(time, freq_deviation, 'b-', linewidth=2)
        ax4.axhline(y=0, color='k', linestyle='-', alpha=0.5, linewidth=1)
        ax4.set_xlabel('Time (minutes)', fontsize=9, fontweight='bold')
        ax4.set_ylabel('Deviation (Hz)', fontsize=9, fontweight='bold')
        ax4.set_title('Frequency Deviation from 60 Hz', fontsize=10, fontweight='bold')
        ax4.grid(True, alpha=0.3, linestyle=':')

        # Plot 5: Clock Error
        clock_time = cumulative_cycles / 60
        actual_time = time * 60
        clock_error = actual_time - clock_time

        ax5 = self.fig.add_subplot(gs[2, 1])
        ax5.plot(time, clock_error, 'purple', linewidth=2.5)
        ax5.fill_between(time, 0, clock_error, alpha=0.3, color='purple')
        ax5.set_xlabel('Time (minutes)', fontsize=9, fontweight='bold')
        ax5.set_ylabel('Clock Error (seconds)', fontsize=9, fontweight='bold')
        ax5.set_title(f'Final Error: {results["clock_error_ms"]:.2f} ms', fontsize=10, fontweight='bold')
        ax5.grid(True, alpha=0.3, linestyle=':')

        self.canvas.draw()

    def add_to_comparison(self):
        """Add current scenario to comparison list"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        scenario_name = f"{self.scenario_var.get()} - {timestamp}"

        data = {
            'name': scenario_name,
            'params': self.params.copy(),
            'time': self.current_time.copy(),
            'frequency': self.current_frequency.copy(),
            'results': self.current_results.copy()
        }

        self.comparison_data.append(data)
        self.comparison_listbox.insert(tk.END, scenario_name)
        messagebox.showinfo("Added", f"Added '{scenario_name}' to comparison")

    def clear_comparison(self):
        """Clear all comparison data"""
        self.comparison_data = []
        self.comparison_listbox.delete(0, tk.END)
        self.comp_fig.clear()
        self.comp_canvas.draw()

    def remove_selected(self):
        """Remove selected item from comparison"""
        selection = self.comparison_listbox.curselection()
        if selection:
            idx = selection[0]
            self.comparison_listbox.delete(idx)
            self.comparison_data.pop(idx)

    def quick_compare_all(self):
        """Quickly add all preset scenarios to comparison"""
        self.clear_comparison()

        for scenario_name in self.scenarios.keys():
            self.scenario_var.set(scenario_name)
            self.load_scenario(None)
            self.add_to_comparison()

        self.plot_comparison()

    def plot_comparison(self):
        """Plot comparison of all stored scenarios"""
        if not self.comparison_data:
            messagebox.showwarning("No Data", "Add scenarios to comparison first")
            return

        self.comp_fig.clear()
        gs = gridspec.GridSpec(2, 2, figure=self.comp_fig, hspace=0.3, wspace=0.3)

        colors = plt.cm.tab10(np.linspace(0, 1, len(self.comparison_data)))

        # Plot 1: Frequency comparison
        ax1 = self.comp_fig.add_subplot(gs[0, :])
        for i, data in enumerate(self.comparison_data):
            ax1.plot(data['time'], data['frequency'], linewidth=2,
                    label=data['name'], color=colors[i])
        ax1.axhline(y=60.0, color='k', linestyle='--', alpha=0.3)
        ax1.set_xlabel('Time (minutes)', fontweight='bold')
        ax1.set_ylabel('Frequency (Hz)', fontweight='bold')
        ax1.set_title('Frequency Comparison', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='best', fontsize=7)

        # Plot 2: Cycles lost comparison
        ax2 = self.comp_fig.add_subplot(gs[1, 0])
        names = [d['name'].split(' - ')[0] for d in self.comparison_data]
        cycles_lost = [d['results']['cycles_lost'] for d in self.comparison_data]
        bars = ax2.bar(range(len(names)), cycles_lost, color=colors)
        ax2.set_xticks(range(len(names)))
        ax2.set_xticklabels(names, rotation=45, ha='right', fontsize=7)
        ax2.set_ylabel('Cycles Lost', fontweight='bold')
        ax2.set_title('Cycles Lost Comparison', fontsize=11, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')

        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=7)

        # Plot 3: Clock error comparison
        ax3 = self.comp_fig.add_subplot(gs[1, 1])
        clock_errors = [d['results']['clock_error_ms'] for d in self.comparison_data]
        bars = ax3.bar(range(len(names)), clock_errors, color=colors)
        ax3.set_xticks(range(len(names)))
        ax3.set_xticklabels(names, rotation=45, ha='right', fontsize=7)
        ax3.set_ylabel('Clock Error (ms)', fontweight='bold')
        ax3.set_title('Clock Error Comparison', fontsize=11, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')

        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=7)

        self.comp_fig.tight_layout()
        self.comp_canvas.draw()

    def generate_analysis(self):
        """Generate detailed analysis report"""
        self.analysis_text.delete(1.0, tk.END)

        report = f"""
{'='*80}
POWER GRID FREQUENCY ANALYSIS REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
{'='*80}

SCENARIO: {self.scenario_var.get()}

SYSTEM PARAMETERS:
{'-'*80}
Total System Power:          {self.params['total_power']:>10.2f} MW
Lost Generation:             {self.params['lost_power']:>10.2f} MW
Power Loss Percentage:       {self.current_results['power_loss_pct']:>10.2f} %

Initial Frequency:           {self.params['initial_freq']:>10.4f} Hz
Minimum Frequency:           {self.params['min_freq']:>10.4f} Hz
Frequency Drop:              {self.current_results['freq_drop']:>10.4f} Hz

Restoration Time:            {self.params['restoration_time']:>10.2f} minutes
Recovery Time:               {self.params['recovery_time']:>10.2f} minutes
Overshoot Frequency:         {self.params['overshoot_freq']:>10.4f} Hz
Overshoot Duration:          {self.params['overshoot_time']:>10.2f} minutes

CALCULATED RESULTS:
{'-'*80}
Average Frequency:           {self.current_results['avg_freq']:>10.6f} Hz
Cycles Generated (actual):   {self.current_results['cycles_actual']:>10.2f} cycles
Cycles Expected (60 Hz):     {self.current_results['cycles_normal']:>10.2f} cycles
Cycles Lost:                 {self.current_results['cycles_lost']:>10.2f} cycles

Clock Minute Hand Turns:     {self.current_results['clock_turns']:>10.6f} turns
Clock Error:                 {self.current_results['clock_error_s']:>10.6f} seconds
Clock Error:                 {self.current_results['clock_error_ms']:>10.2f} milliseconds

ANALYSIS:
{'-'*80}

1. SEVERITY ASSESSMENT:
   The power loss of {self.params['lost_power']:.0f} MW represents {self.current_results['power_loss_pct']:.2f}%
   of the total system capacity. This is considered a {'CRITICAL' if self.current_results['power_loss_pct'] > 10 else 'SIGNIFICANT' if self.current_results['power_loss_pct'] > 5 else 'MODERATE'} disturbance.

   Frequency dropped by {self.current_results['freq_drop']:.4f} Hz, reaching a nadir of
   {self.params['min_freq']:.4f} Hz. {'WARNING: Frequency approached load shedding threshold!' if self.params['min_freq'] < 59.5 else 'Frequency remained within acceptable operational limits.'}

2. SYSTEM RESPONSE:
   The system took {self.params['restoration_time']:.2f} minutes to restore frequency to nominal.
   {'This indicates good system inertia and governor response.' if self.params['restoration_time'] < 5 else 'This indicates moderate system response capability.' if self.params['restoration_time'] < 10 else 'This indicates slow system response - consider additional reserves.'}

3. TIMEKEEPING IMPACT:
   Electric clocks lost {self.current_results['cycles_lost']:.2f} cycles during the event.
   This resulted in clocks being slow by {self.current_results['clock_error_ms']:.2f} milliseconds.

   The minute hand made {self.current_results['clock_turns']:.6f} turns instead of the expected
   {self.params['restoration_time']:.6f} turns.

4. RECOVERY ACTIONS:
   {'Overshoot correction phase planned for ' + str(self.params['overshoot_time']) + ' minutes at ' + str(self.params['overshoot_freq']) + ' Hz' if self.params['overshoot_time'] > 0 else 'No overshoot correction implemented.'}
   {'This will help recover lost cycles and correct electric clocks.' if self.params['overshoot_time'] > 0 else ''}

5. RECOMMENDATIONS:
"""

        # Add recommendations based on analysis
        if self.current_results['power_loss_pct'] > 10:
            report += "\n   - Critical: System lacks sufficient reserve capacity"
            report += "\n   - Recommend adding spinning reserves or fast-start generation"

        if self.params['min_freq'] < 59.85:
            report += "\n   - Frequency nadir too low - risk of under-frequency load shedding"
            report += "\n   - Consider faster governor response or additional inertia"

        if self.params['restoration_time'] > 10:
            report += "\n   - Slow restoration time indicates weak governor response"
            report += "\n   - Recommend review of AGC settings and reserve deployment"

        if self.current_results['cycles_lost'] > 50:
            report += "\n   - Significant cycle loss requires overshoot correction"
            report += f"\n   - Plan {self.current_results['cycles_lost']/60:.2f} seconds of correction"

        report += f"\n\n{'='*80}\n"
        report += "END OF REPORT\n"
        report += f"{'='*80}\n"

        self.analysis_text.insert(1.0, report)

    def export_data(self):
        """Export simulation data to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if filename:
            with open(filename, 'w') as f:
                f.write("Time (min),Frequency (Hz),Cumulative Cycles,Clock Error (s)\n")

                cumulative_cycles = np.cumsum(self.current_frequency[:-1] *
                                             np.diff(self.current_time) * 60)
                cumulative_cycles = np.insert(cumulative_cycles, 0, 0)

                clock_error = self.current_time * 60 - cumulative_cycles / 60

                for i in range(len(self.current_time)):
                    f.write(f"{self.current_time[i]:.6f},{self.current_frequency[i]:.8f},"
                          f"{cumulative_cycles[i]:.4f},{clock_error[i]:.6f}\n")

            messagebox.showinfo("Success", f"Data exported to {filename}")

    def export_plot(self):
        """Export plot as image"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"),
                      ("SVG files", "*.svg"), ("All files", "*.*")]
        )

        if filename:
            self.fig.savefig(filename, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Success", f"Plot exported to {filename}")

    def export_analysis(self):
        """Export analysis report"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filename:
            with open(filename, 'w') as f:
                f.write(self.analysis_text.get(1.0, tk.END))
            messagebox.showinfo("Success", f"Analysis exported to {filename}")


def main():
    root = tk.Tk()
    app = AdvancedPowerGridSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()

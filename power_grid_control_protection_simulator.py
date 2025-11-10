"""
Advanced Power Grid Control and Protection Simulator
Features:
- PID and Fuzzy Logic Controllers
- Multi-machine parallel operation
- Advanced ODE solvers (RK45, BDF)
- Protection systems (overcurrent, overvoltage, underfrequency)
- Reliability analysis (MTBF, failure probability)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
from datetime import datetime
import json


class PIDController:
    """PID Controller for voltage/frequency regulation"""
    def __init__(self, kp=1.0, ki=0.1, kd=0.05, setpoint=60.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.integral = 0.0
        self.prev_error = 0.0
        self.output_min = -10.0
        self.output_max = 10.0

    def update(self, measured_value, dt):
        """Calculate PID output"""
        error = self.setpoint - measured_value

        # Proportional term
        p_term = self.kp * error

        # Integral term with anti-windup
        self.integral += error * dt
        self.integral = np.clip(self.integral, -100, 100)
        i_term = self.ki * self.integral

        # Derivative term
        d_term = self.kd * (error - self.prev_error) / dt if dt > 0 else 0

        # Calculate output
        output = p_term + i_term + d_term
        output = np.clip(output, self.output_min, self.output_max)

        self.prev_error = error
        return output

    def reset(self):
        """Reset controller state"""
        self.integral = 0.0
        self.prev_error = 0.0


class FuzzyLogicController:
    """Fuzzy Logic Controller for power system control"""
    def __init__(self, setpoint=60.0):
        self.setpoint = setpoint

    def fuzzify_error(self, error):
        """Convert error to fuzzy sets"""
        # Membership functions for error
        large_negative = max(0, min(1, (-error - 0.02) / 0.01))
        small_negative = max(0, min(1, (-error) / 0.02)) if error < 0 else 0
        zero = max(0, 1 - abs(error) / 0.01)
        small_positive = max(0, min(1, error / 0.02)) if error > 0 else 0
        large_positive = max(0, min(1, (error - 0.02) / 0.01))

        return {
            'LN': large_negative,
            'SN': small_negative,
            'ZE': zero,
            'SP': small_positive,
            'LP': large_positive
        }

    def fuzzify_rate(self, rate):
        """Convert rate of change to fuzzy sets"""
        negative = max(0, min(1, (-rate) / 0.01)) if rate < 0 else 0
        zero = max(0, 1 - abs(rate) / 0.005)
        positive = max(0, min(1, rate / 0.01)) if rate > 0 else 0

        return {'N': negative, 'Z': zero, 'P': positive}

    def defuzzify(self, error_fuzzy, rate_fuzzy):
        """Apply fuzzy rules and defuzzify"""
        # Fuzzy rules (simplified)
        rules = {
            ('LN', 'N'): 10.0,   # Large negative error, decreasing -> large positive control
            ('LN', 'Z'): 8.0,
            ('LN', 'P'): 5.0,
            ('SN', 'N'): 5.0,
            ('SN', 'Z'): 3.0,
            ('SN', 'P'): 1.0,
            ('ZE', 'N'): 1.0,
            ('ZE', 'Z'): 0.0,
            ('ZE', 'P'): -1.0,
            ('SP', 'N'): -1.0,
            ('SP', 'Z'): -3.0,
            ('SP', 'P'): -5.0,
            ('LP', 'N'): -5.0,
            ('LP', 'Z'): -8.0,
            ('LP', 'P'): -10.0
        }

        # Calculate weighted average
        total_weight = 0.0
        weighted_sum = 0.0

        for error_key, error_val in error_fuzzy.items():
            for rate_key, rate_val in rate_fuzzy.items():
                weight = error_val * rate_val
                if weight > 0:
                    output = rules.get((error_key, rate_key), 0.0)
                    weighted_sum += weight * output
                    total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def update(self, measured_value, rate_of_change):
        """Calculate fuzzy control output"""
        error = self.setpoint - measured_value

        error_fuzzy = self.fuzzify_error(error)
        rate_fuzzy = self.fuzzify_rate(rate_of_change)

        output = self.defuzzify(error_fuzzy, rate_fuzzy)
        return np.clip(output, -10.0, 10.0)


class Generator:
    """Generator model with dynamics"""
    def __init__(self, name, rated_power, inertia=5.0):
        self.name = name
        self.rated_power = rated_power  # MW
        self.inertia = inertia  # seconds
        self.frequency = 60.0
        self.voltage = 1.0  # pu
        self.power_output = 0.0
        self.field_voltage = 1.0
        self.is_online = True

        # Protection settings
        self.max_current = rated_power * 1.2  # 120% of rated
        self.min_voltage = 0.85  # pu
        self.max_voltage = 1.15  # pu
        self.min_frequency = 59.5  # Hz

        # Thermal model
        self.temperature = 25.0  # °C
        self.max_temperature = 120.0  # °C
        self.thermal_time_constant = 600.0  # seconds

        # Reliability
        self.operating_hours = 0.0
        self.stress_accumulator = 0.0


class ProtectionSystem:
    """Protection and fault detection system"""
    def __init__(self):
        self.trip_log = []
        self.active_alarms = []

    def check_overcurrent(self, generator, current):
        """Check for overcurrent condition"""
        if current > generator.max_current:
            self.trip_log.append({
                'time': datetime.now(),
                'generator': generator.name,
                'type': 'Overcurrent',
                'value': current,
                'limit': generator.max_current
            })
            return True
        return False

    def check_overvoltage(self, generator):
        """Check for overvoltage condition"""
        if generator.voltage > generator.max_voltage:
            self.trip_log.append({
                'time': datetime.now(),
                'generator': generator.name,
                'type': 'Overvoltage',
                'value': generator.voltage,
                'limit': generator.max_voltage
            })
            return True
        return False

    def check_undervoltage(self, generator):
        """Check for undervoltage condition"""
        if generator.voltage < generator.min_voltage:
            self.trip_log.append({
                'time': datetime.now(),
                'generator': generator.name,
                'type': 'Undervoltage',
                'value': generator.voltage,
                'limit': generator.min_voltage
            })
            return True
        return False

    def check_underfrequency(self, generator):
        """Check for underfrequency condition"""
        if generator.frequency < generator.min_frequency:
            self.trip_log.append({
                'time': datetime.now(),
                'generator': generator.name,
                'type': 'Underfrequency',
                'value': generator.frequency,
                'limit': generator.min_frequency
            })
            return True
        return False

    def check_thermal_trip(self, generator):
        """Check for thermal overload"""
        if generator.temperature > generator.max_temperature:
            self.trip_log.append({
                'time': datetime.now(),
                'generator': generator.name,
                'type': 'Thermal Trip',
                'value': generator.temperature,
                'limit': generator.max_temperature
            })
            return True
        return False

    def check_all(self, generator):
        """Check all protection conditions"""
        current = generator.power_output / generator.voltage if generator.voltage > 0 else 0

        if self.check_overcurrent(generator, current):
            return 'Overcurrent'
        if self.check_overvoltage(generator):
            return 'Overvoltage'
        if self.check_undervoltage(generator):
            return 'Undervoltage'
        if self.check_underfrequency(generator):
            return 'Underfrequency'
        if self.check_thermal_trip(generator):
            return 'Thermal Trip'

        return None


class ReliabilityAnalyzer:
    """Reliability and failure analysis"""
    def __init__(self):
        self.base_failure_rate = 0.001  # failures per hour

    def calculate_mtbf(self, generator):
        """Calculate Mean Time Between Failures"""
        # MTBF = 1 / failure_rate
        failure_rate = self.get_failure_rate(generator)
        return 1.0 / failure_rate if failure_rate > 0 else float('inf')

    def get_failure_rate(self, generator):
        """Calculate current failure rate based on stress"""
        # Base failure rate modified by stress factors
        temp_factor = np.exp((generator.temperature - 75) / 50)
        load_factor = (generator.power_output / generator.rated_power) ** 2

        return self.base_failure_rate * temp_factor * (1 + load_factor)

    def calculate_reliability(self, generator, time_hours):
        """Calculate reliability for given time period"""
        failure_rate = self.get_failure_rate(generator)
        # R(t) = e^(-λt)
        return np.exp(-failure_rate * time_hours)

    def calculate_derating(self, generator):
        """Calculate derating factor based on conditions"""
        temp_derating = max(0, 1 - (generator.temperature - 100) / 50) if generator.temperature > 100 else 1.0
        voltage_derating = max(0.5, generator.voltage)

        return min(temp_derating, voltage_derating)


class AdvancedGridSimulator:
    """Advanced grid simulator with control and protection"""
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Power Grid Control & Protection Simulator")
        self.root.geometry("1800x1000")

        # Initialize components
        self.generators = [
            Generator("Gen 1", 500, inertia=6.0),
            Generator("Gen 2", 400, inertia=5.0),
            Generator("Gen 3", 300, inertia=4.0)
        ]

        self.pid_controller = PIDController(kp=2.0, ki=0.5, kd=0.1, setpoint=60.0)
        self.fuzzy_controller = FuzzyLogicController(setpoint=60.0)
        self.protection = ProtectionSystem()
        self.reliability = ReliabilityAnalyzer()

        # Simulation parameters
        self.control_mode = 'Manual'  # Manual, Auto, PID, Fuzzy
        self.simulation_time = 0.0
        self.dt = 0.01  # Time step
        self.solver_type = 'RK45'  # RK45, BDF, Euler

        # Grid parameters
        self.total_load = 1000.0  # MW
        self.system_frequency = 60.0
        self.grid_voltage = 1.0  # pu

        # Event simulation
        self.events = []
        self.event_types = ['Load Change', 'Short Circuit', 'Excitation Fault', 'Generator Trip']

        # Data storage
        self.history = {
            'time': [],
            'frequency': [],
            'voltage': [],
            'power': [],
            'control_signal': [],
            'protection_events': []
        }

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface"""
        # Create notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tabs
        control_tab = ttk.Frame(notebook)
        notebook.add(control_tab, text="Control System")
        self.setup_control_tab(control_tab)

        multi_machine_tab = ttk.Frame(notebook)
        notebook.add(multi_machine_tab, text="Multi-Machine")
        self.setup_multi_machine_tab(multi_machine_tab)

        protection_tab = ttk.Frame(notebook)
        notebook.add(protection_tab, text="Protection")
        self.setup_protection_tab(protection_tab)

        reliability_tab = ttk.Frame(notebook)
        notebook.add(reliability_tab, text="Reliability")
        self.setup_reliability_tab(reliability_tab)

    def setup_control_tab(self, parent):
        """Setup control system tab"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - controls
        left_panel = ttk.Frame(main_frame, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        # Control mode selection
        mode_frame = ttk.LabelFrame(left_panel, text="Control Mode", padding=10)
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        self.control_mode_var = tk.StringVar(value='Manual')
        modes = ['Manual', 'Auto', 'PID', 'Fuzzy']
        for mode in modes:
            ttk.Radiobutton(mode_frame, text=mode, variable=self.control_mode_var,
                          value=mode, command=self.on_mode_change).pack(anchor=tk.W)

        # PID Parameters
        pid_frame = ttk.LabelFrame(left_panel, text="PID Controller", padding=10)
        pid_frame.pack(fill=tk.X, pady=(0, 10))

        self.pid_params = {}
        pid_configs = [
            ('kp', 'Kp (Proportional)', 0.0, 10.0, 2.0),
            ('ki', 'Ki (Integral)', 0.0, 5.0, 0.5),
            ('kd', 'Kd (Derivative)', 0.0, 2.0, 0.1),
            ('setpoint', 'Setpoint (Hz)', 59.5, 60.5, 60.0)
        ]

        for key, label, min_val, max_val, default in pid_configs:
            frame = ttk.Frame(pid_frame)
            frame.pack(fill=tk.X, pady=3)

            ttk.Label(frame, text=label, width=20, anchor='w').pack()

            value_label = ttk.Label(frame, text=f"{default:.3f}", width=10)
            value_label.pack()

            slider = ttk.Scale(frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL,
                             command=lambda v, k=key, vl=value_label: self.update_pid_param(k, v, vl))
            slider.set(default)
            slider.pack(fill=tk.X)

            self.pid_params[key] = (slider, value_label)

        # Fuzzy Logic Parameters
        fuzzy_frame = ttk.LabelFrame(left_panel, text="Fuzzy Logic", padding=10)
        fuzzy_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(fuzzy_frame, text="Fuzziness Level:").pack()
        self.fuzzy_level = ttk.Scale(fuzzy_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL)
        self.fuzzy_level.set(0.5)
        self.fuzzy_level.pack(fill=tk.X)

        # Solver selection
        solver_frame = ttk.LabelFrame(left_panel, text="ODE Solver", padding=10)
        solver_frame.pack(fill=tk.X, pady=(0, 10))

        self.solver_var = tk.StringVar(value='RK45')
        solvers = ['Euler', 'RK45', 'BDF']
        for solver in solvers:
            ttk.Radiobutton(solver_frame, text=solver, variable=self.solver_var,
                          value=solver).pack(anchor=tk.W)

        # Simulation controls
        sim_frame = ttk.LabelFrame(left_panel, text="Simulation", padding=10)
        sim_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(sim_frame, text="Start Simulation",
                  command=self.start_simulation).pack(fill=tk.X, pady=2)
        ttk.Button(sim_frame, text="Stop Simulation",
                  command=self.stop_simulation).pack(fill=tk.X, pady=2)
        ttk.Button(sim_frame, text="Reset",
                  command=self.reset_simulation).pack(fill=tk.X, pady=2)

        # Event injection
        event_frame = ttk.LabelFrame(left_panel, text="Event Simulation", padding=10)
        event_frame.pack(fill=tk.X, pady=(0, 10))

        self.event_type_var = tk.StringVar(value='Load Change')
        ttk.Combobox(event_frame, textvariable=self.event_type_var,
                    values=self.event_types, state='readonly').pack(fill=tk.X, pady=2)

        ttk.Button(event_frame, text="Inject Event",
                  command=self.inject_event).pack(fill=tk.X, pady=2)

        # Status display
        status_frame = ttk.LabelFrame(left_panel, text="Status", padding=10)
        status_frame.pack(fill=tk.BOTH, expand=True)

        self.status_labels = {}
        status_items = [
            ('freq', 'Frequency (Hz):'),
            ('voltage', 'Voltage (pu):'),
            ('power', 'Total Power (MW):'),
            ('control', 'Control Signal:')
        ]

        for key, label in status_items:
            frame = ttk.Frame(status_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=label, width=18, anchor='w').pack(side=tk.LEFT)
            value_label = ttk.Label(frame, text="0.000", width=12, anchor='e',
                                   font=('Arial', 9, 'bold'), foreground='blue')
            value_label.pack(side=tk.RIGHT)
            self.status_labels[key] = value_label

        # Right panel - plots
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.control_fig = Figure(figsize=(12, 8), dpi=100)
        self.control_canvas = FigureCanvasTkAgg(self.control_fig, master=plot_frame)
        self.control_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_multi_machine_tab(self, parent):
        """Setup multi-machine tab"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Generator controls
        gen_frame = ttk.LabelFrame(main_frame, text="Generator Controls", padding=10)
        gen_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.gen_controls = {}
        for gen in self.generators:
            frame = ttk.LabelFrame(gen_frame, text=gen.name, padding=5)
            frame.pack(fill=tk.X, pady=5)

            # Status
            status_var = tk.BooleanVar(value=gen.is_online)
            ttk.Checkbutton(frame, text="Online", variable=status_var,
                          command=lambda g=gen, v=status_var: self.toggle_generator(g, v)).pack()

            # Power setpoint
            ttk.Label(frame, text="Power (MW):").pack()
            power_var = tk.DoubleVar(value=gen.rated_power * 0.8)
            power_slider = ttk.Scale(frame, from_=0, to=gen.rated_power,
                                   variable=power_var, orient=tk.HORIZONTAL)
            power_slider.pack(fill=tk.X)

            # Voltage setpoint
            ttk.Label(frame, text="Voltage (pu):").pack()
            voltage_var = tk.DoubleVar(value=1.0)
            voltage_slider = ttk.Scale(frame, from_=0.8, to=1.2,
                                     variable=voltage_var, orient=tk.HORIZONTAL)
            voltage_slider.pack(fill=tk.X)

            self.gen_controls[gen.name] = {
                'status': status_var,
                'power': power_var,
                'voltage': voltage_var
            }

        # Load sharing
        sharing_frame = ttk.LabelFrame(gen_frame, text="Load Sharing", padding=10)
        sharing_frame.pack(fill=tk.X, pady=10)

        ttk.Button(sharing_frame, text="Equal Sharing",
                  command=self.equal_load_sharing).pack(fill=tk.X, pady=2)
        ttk.Button(sharing_frame, text="Proportional Sharing",
                  command=self.proportional_load_sharing).pack(fill=tk.X, pady=2)
        ttk.Button(sharing_frame, text="Economic Dispatch",
                  command=self.economic_dispatch).pack(fill=tk.X, pady=2)

        # Plots
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.multi_fig = Figure(figsize=(12, 8), dpi=100)
        self.multi_canvas = FigureCanvasTkAgg(self.multi_fig, master=plot_frame)
        self.multi_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initial plot
        self.plot_multi_machine()

    def setup_protection_tab(self, parent):
        """Setup protection tab"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Protection settings
        settings_frame = ttk.LabelFrame(main_frame, text="Protection Settings", padding=10)
        settings_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Overcurrent
        ttk.Label(settings_frame, text="Overcurrent (% of rated):").pack()
        self.oc_setting = ttk.Scale(settings_frame, from_=100, to=150, orient=tk.HORIZONTAL)
        self.oc_setting.set(120)
        self.oc_setting.pack(fill=tk.X, pady=5)

        # Overvoltage
        ttk.Label(settings_frame, text="Overvoltage (pu):").pack()
        self.ov_setting = ttk.Scale(settings_frame, from_=1.0, to=1.3, orient=tk.HORIZONTAL)
        self.ov_setting.set(1.15)
        self.ov_setting.pack(fill=tk.X, pady=5)

        # Undervoltage
        ttk.Label(settings_frame, text="Undervoltage (pu):").pack()
        self.uv_setting = ttk.Scale(settings_frame, from_=0.7, to=0.95, orient=tk.HORIZONTAL)
        self.uv_setting.set(0.85)
        self.uv_setting.pack(fill=tk.X, pady=5)

        # Underfrequency
        ttk.Label(settings_frame, text="Underfrequency (Hz):").pack()
        self.uf_setting = ttk.Scale(settings_frame, from_=59.0, to=59.9, orient=tk.HORIZONTAL)
        self.uf_setting.set(59.5)
        self.uf_setting.pack(fill=tk.X, pady=5)

        ttk.Button(settings_frame, text="Apply Settings",
                  command=self.apply_protection_settings).pack(fill=tk.X, pady=10)

        # Trip log
        log_frame = ttk.LabelFrame(main_frame, text="Protection Trip Log", padding=10)
        log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create text widget with scrollbar
        scroll = ttk.Scrollbar(log_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.trip_log_text = tk.Text(log_frame, yscrollcommand=scroll.set,
                                     font=('Courier', 9), height=20)
        self.trip_log_text.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.trip_log_text.yview)

        ttk.Button(log_frame, text="Clear Log",
                  command=lambda: self.trip_log_text.delete(1.0, tk.END)).pack(fill=tk.X, pady=5)

    def setup_reliability_tab(self, parent):
        """Setup reliability tab"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - metrics
        metrics_frame = ttk.LabelFrame(main_frame, text="Reliability Metrics", padding=10)
        metrics_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.reliability_labels = {}

        for gen in self.generators:
            frame = ttk.LabelFrame(metrics_frame, text=gen.name, padding=5)
            frame.pack(fill=tk.X, pady=5)

            metrics = [
                ('mtbf', 'MTBF (hours):'),
                ('reliability', 'Reliability (24h):'),
                ('failure_rate', 'Failure Rate:'),
                ('derating', 'Derating Factor:'),
                ('temperature', 'Temperature (°C):')
            ]

            gen_labels = {}
            for key, label in metrics:
                subframe = ttk.Frame(frame)
                subframe.pack(fill=tk.X, pady=1)
                ttk.Label(subframe, text=label, width=18, anchor='w').pack(side=tk.LEFT)
                value_label = ttk.Label(subframe, text="0.00", width=12, anchor='e',
                                       font=('Arial', 8, 'bold'))
                value_label.pack(side=tk.RIGHT)
                gen_labels[key] = value_label

            self.reliability_labels[gen.name] = gen_labels

        ttk.Button(metrics_frame, text="Update Metrics",
                  command=self.update_reliability_metrics).pack(fill=tk.X, pady=10)

        # Right panel - plots
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.reliability_fig = Figure(figsize=(12, 8), dpi=100)
        self.reliability_canvas = FigureCanvasTkAgg(self.reliability_fig, master=plot_frame)
        self.reliability_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initial plot
        self.plot_reliability()

    # Control methods
    def update_pid_param(self, key, value, label):
        """Update PID parameter"""
        val = float(value)
        label.config(text=f"{val:.3f}")

        if key == 'kp':
            self.pid_controller.kp = val
        elif key == 'ki':
            self.pid_controller.ki = val
        elif key == 'kd':
            self.pid_controller.kd = val
        elif key == 'setpoint':
            self.pid_controller.setpoint = val
            self.fuzzy_controller.setpoint = val

    def on_mode_change(self):
        """Handle control mode change"""
        self.control_mode = self.control_mode_var.get()
        self.pid_controller.reset()
        messagebox.showinfo("Mode Change", f"Control mode changed to: {self.control_mode}")

    def start_simulation(self):
        """Start the simulation"""
        messagebox.showinfo("Simulation", "Simulation started")
        self.run_simulation()

    def stop_simulation(self):
        """Stop the simulation"""
        messagebox.showinfo("Simulation", "Simulation stopped")

    def reset_simulation(self):
        """Reset the simulation"""
        self.simulation_time = 0.0
        self.system_frequency = 60.0
        self.grid_voltage = 1.0
        self.history = {
            'time': [],
            'frequency': [],
            'voltage': [],
            'power': [],
            'control_signal': [],
            'protection_events': []
        }
        self.pid_controller.reset()

        for gen in self.generators:
            gen.frequency = 60.0
            gen.voltage = 1.0
            gen.temperature = 25.0
            gen.is_online = True

        self.plot_control_results()
        messagebox.showinfo("Reset", "Simulation reset")

    def inject_event(self):
        """Inject simulation event"""
        event_type = self.event_type_var.get()

        if event_type == 'Load Change':
            change = np.random.uniform(-200, 200)
            self.total_load += change
            msg = f"Load changed by {change:.1f} MW"
        elif event_type == 'Short Circuit':
            self.grid_voltage *= 0.5
            msg = "Short circuit: voltage dropped to 50%"
        elif event_type == 'Excitation Fault':
            if self.generators:
                gen = np.random.choice(self.generators)
                gen.field_voltage *= 0.8
                msg = f"{gen.name}: Excitation fault (80% field voltage)"
        elif event_type == 'Generator Trip':
            online_gens = [g for g in self.generators if g.is_online]
            if online_gens:
                gen = np.random.choice(online_gens)
                gen.is_online = False
                msg = f"{gen.name}: Generator tripped offline"

        self.trip_log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {msg}\n")
        self.trip_log_text.see(tk.END)

    def run_simulation(self):
        """Run the simulation with selected solver"""
        # Simulation parameters
        t_span = (0, 10)  # 10 seconds
        t_eval = np.linspace(0, 10, 1000)

        # Initial conditions [frequency, voltage, power]
        y0 = [60.0, 1.0, self.total_load]

        # Select solver
        if self.solver_var.get() == 'RK45':
            sol = solve_ivp(self.system_dynamics, t_span, y0, method='RK45',
                          t_eval=t_eval, dense_output=True)
        elif self.solver_var.get() == 'BDF':
            sol = solve_ivp(self.system_dynamics, t_span, y0, method='BDF',
                          t_eval=t_eval, dense_output=True)
        else:  # Euler
            sol = self.euler_solve(t_span, y0, t_eval)

        # Store results
        self.history['time'] = sol.t.tolist()
        self.history['frequency'] = sol.y[0].tolist()
        self.history['voltage'] = sol.y[1].tolist()
        self.history['power'] = sol.y[2].tolist()

        # Plot results
        self.plot_control_results()

    def system_dynamics(self, t, y):
        """System dynamics for ODE solver"""
        freq, voltage, power = y

        # Calculate system inertia
        total_inertia = sum(g.inertia for g in self.generators if g.is_online)

        # Power imbalance
        total_gen_power = sum(g.power_output for g in self.generators if g.is_online)
        power_imbalance = total_gen_power - self.total_load

        # Frequency dynamics: df/dt = (P_gen - P_load) / (2 * H)
        df_dt = power_imbalance / (2 * total_inertia) if total_inertia > 0 else 0

        # Apply control
        if self.control_mode == 'PID':
            control_signal = self.pid_controller.update(freq, self.dt)
            df_dt += control_signal * 0.1
        elif self.control_mode == 'Fuzzy':
            rate_of_change = df_dt
            control_signal = self.fuzzy_controller.update(freq, rate_of_change)
            df_dt += control_signal * 0.1

        # Voltage dynamics (simplified)
        voltage_error = 1.0 - voltage
        dv_dt = voltage_error * 2.0

        # Power dynamics
        dp_dt = -power_imbalance * 0.5

        return [df_dt, dv_dt, dp_dt]

    def euler_solve(self, t_span, y0, t_eval):
        """Simple Euler integration"""
        t = t_eval
        y = np.zeros((len(y0), len(t)))
        y[:, 0] = y0

        for i in range(1, len(t)):
            dt = t[i] - t[i-1]
            dy = self.system_dynamics(t[i-1], y[:, i-1])
            y[:, i] = y[:, i-1] + np.array(dy) * dt

        class Solution:
            pass

        sol = Solution()
        sol.t = t
        sol.y = y
        return sol

    def plot_control_results(self):
        """Plot control system results"""
        self.control_fig.clear()

        if not self.history['time']:
            return

        gs = gridspec.GridSpec(3, 2, figure=self.control_fig, hspace=0.35, wspace=0.3)

        time = np.array(self.history['time'])
        freq = np.array(self.history['frequency'])
        voltage = np.array(self.history['voltage'])
        power = np.array(self.history['power'])

        # Plot 1: Frequency
        ax1 = self.control_fig.add_subplot(gs[0, :])
        ax1.plot(time, freq, 'b-', linewidth=2, label='Frequency')
        ax1.axhline(y=60.0, color='g', linestyle='--', alpha=0.5, label='Setpoint')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Frequency (Hz)')
        ax1.set_title(f'System Frequency - {self.control_mode} Control')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # Plot 2: Voltage
        ax2 = self.control_fig.add_subplot(gs[1, 0])
        ax2.plot(time, voltage, 'r-', linewidth=2)
        ax2.axhline(y=1.0, color='g', linestyle='--', alpha=0.5)
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Voltage (pu)')
        ax2.set_title('System Voltage')
        ax2.grid(True, alpha=0.3)

        # Plot 3: Power
        ax3 = self.control_fig.add_subplot(gs[1, 1])
        ax3.plot(time, power, 'purple', linewidth=2)
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Power (MW)')
        ax3.set_title('System Power')
        ax3.grid(True, alpha=0.3)

        # Plot 4: Frequency deviation
        ax4 = self.control_fig.add_subplot(gs[2, 0])
        freq_dev = freq - 60.0
        ax4.plot(time, freq_dev, 'b-', linewidth=2)
        ax4.fill_between(time, 0, freq_dev, alpha=0.3, color='blue')
        ax4.axhline(y=0, color='k', linestyle='-', alpha=0.5)
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Deviation (Hz)')
        ax4.set_title('Frequency Deviation')
        ax4.grid(True, alpha=0.3)

        # Plot 5: Phase plane
        ax5 = self.control_fig.add_subplot(gs[2, 1])
        if len(freq) > 1:
            freq_rate = np.gradient(freq, time)
            ax5.plot(freq_dev, freq_rate, 'b-', linewidth=1.5)
            ax5.scatter(freq_dev[0], freq_rate[0], color='green', s=100, zorder=5, label='Start')
            ax5.scatter(freq_dev[-1], freq_rate[-1], color='red', s=100, zorder=5, label='End')
        ax5.set_xlabel('Frequency Deviation (Hz)')
        ax5.set_ylabel('Rate of Change (Hz/s)')
        ax5.set_title('Phase Plane')
        ax5.grid(True, alpha=0.3)
        ax5.legend()

        self.control_canvas.draw()

        # Update status
        if len(freq) > 0:
            self.status_labels['freq'].config(text=f"{freq[-1]:.3f}")
            self.status_labels['voltage'].config(text=f"{voltage[-1]:.3f}")
            self.status_labels['power'].config(text=f"{power[-1]:.1f}")

    # Multi-machine methods
    def toggle_generator(self, gen, status_var):
        """Toggle generator online/offline"""
        gen.is_online = status_var.get()
        self.plot_multi_machine()

    def equal_load_sharing(self):
        """Distribute load equally among online generators"""
        online_gens = [g for g in self.generators if g.is_online]
        if not online_gens:
            return

        equal_share = self.total_load / len(online_gens)

        for gen in online_gens:
            share = min(equal_share, gen.rated_power)
            gen.power_output = share
            self.gen_controls[gen.name]['power'].set(share)

        self.plot_multi_machine()
        messagebox.showinfo("Load Sharing", "Equal load sharing applied")

    def proportional_load_sharing(self):
        """Distribute load proportionally based on ratings"""
        online_gens = [g for g in self.generators if g.is_online]
        if not online_gens:
            return

        total_capacity = sum(g.rated_power for g in online_gens)

        for gen in online_gens:
            share = (gen.rated_power / total_capacity) * self.total_load
            gen.power_output = min(share, gen.rated_power)
            self.gen_controls[gen.name]['power'].set(gen.power_output)

        self.plot_multi_machine()
        messagebox.showinfo("Load Sharing", "Proportional load sharing applied")

    def economic_dispatch(self):
        """Simple economic dispatch (equal incremental cost)"""
        # Simplified: assume cost = a + b*P + c*P^2
        # For simplicity, use proportional sharing with small adjustments
        self.proportional_load_sharing()
        messagebox.showinfo("Economic Dispatch", "Economic dispatch applied")

    def plot_multi_machine(self):
        """Plot multi-machine operation"""
        self.multi_fig.clear()
        gs = gridspec.GridSpec(2, 2, figure=self.multi_fig, hspace=0.3, wspace=0.3)

        # Plot 1: Power output
        ax1 = self.multi_fig.add_subplot(gs[0, 0])
        gen_names = [g.name for g in self.generators]
        powers = [g.power_output for g in self.generators]
        rated_powers = [g.rated_power for g in self.generators]

        x = np.arange(len(gen_names))
        width = 0.35

        ax1.bar(x - width/2, powers, width, label='Output', color='blue', alpha=0.7)
        ax1.bar(x + width/2, rated_powers, width, label='Rated', color='gray', alpha=0.5)

        ax1.set_xlabel('Generator')
        ax1.set_ylabel('Power (MW)')
        ax1.set_title('Generator Power Output')
        ax1.set_xticks(x)
        ax1.set_xticklabels(gen_names)
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')

        # Plot 2: Loading percentage
        ax2 = self.multi_fig.add_subplot(gs[0, 1])
        loading = [g.power_output / g.rated_power * 100 if g.rated_power > 0 else 0
                  for g in self.generators]

        bars = ax2.bar(gen_names, loading, color=['green' if l < 80 else 'yellow' if l < 100 else 'red'
                                                   for l in loading])
        ax2.axhline(y=100, color='r', linestyle='--', label='Rated')
        ax2.set_xlabel('Generator')
        ax2.set_ylabel('Loading (%)')
        ax2.set_title('Generator Loading')
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')

        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom')

        # Plot 3: Temperature
        ax3 = self.multi_fig.add_subplot(gs[1, 0])
        temps = [g.temperature for g in self.generators]
        max_temps = [g.max_temperature for g in self.generators]

        ax3.bar(x - width/2, temps, width, label='Current', color='orange', alpha=0.7)
        ax3.bar(x + width/2, max_temps, width, label='Max', color='red', alpha=0.5)

        ax3.set_xlabel('Generator')
        ax3.set_ylabel('Temperature (°C)')
        ax3.set_title('Generator Temperature')
        ax3.set_xticks(x)
        ax3.set_xticklabels(gen_names)
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')

        # Plot 4: Status
        ax4 = self.multi_fig.add_subplot(gs[1, 1])
        status = [1 if g.is_online else 0 for g in self.generators]

        colors_status = ['green' if s else 'red' for s in status]
        ax4.bar(gen_names, status, color=colors_status, alpha=0.7)
        ax4.set_xlabel('Generator')
        ax4.set_ylabel('Status')
        ax4.set_title('Generator Online Status')
        ax4.set_ylim([0, 1.2])
        ax4.set_yticks([0, 1])
        ax4.set_yticklabels(['Offline', 'Online'])

        self.multi_canvas.draw()

    # Protection methods
    def apply_protection_settings(self):
        """Apply protection settings to all generators"""
        oc = self.oc_setting.get() / 100.0
        ov = self.ov_setting.get()
        uv = self.uv_setting.get()
        uf = self.uf_setting.get()

        for gen in self.generators:
            gen.max_current = gen.rated_power * oc
            gen.max_voltage = ov
            gen.min_voltage = uv
            gen.min_frequency = uf

        messagebox.showinfo("Protection", "Protection settings applied to all generators")

    # Reliability methods
    def update_reliability_metrics(self):
        """Update reliability metrics for all generators"""
        for gen in self.generators:
            # Calculate metrics
            mtbf = self.reliability.calculate_mtbf(gen)
            reliability_24h = self.reliability.calculate_reliability(gen, 24)
            failure_rate = self.reliability.get_failure_rate(gen)
            derating = self.reliability.calculate_derating(gen)

            # Update labels
            labels = self.reliability_labels[gen.name]
            labels['mtbf'].config(text=f"{mtbf:.0f}" if mtbf != float('inf') else "∞")
            labels['reliability'].config(text=f"{reliability_24h:.4f}")
            labels['failure_rate'].config(text=f"{failure_rate:.6f}")
            labels['derating'].config(text=f"{derating:.3f}")
            labels['temperature'].config(text=f"{gen.temperature:.1f}")

        self.plot_reliability()

    def plot_reliability(self):
        """Plot reliability analysis"""
        self.reliability_fig.clear()
        gs = gridspec.GridSpec(2, 2, figure=self.reliability_fig, hspace=0.3, wspace=0.3)

        # Plot 1: MTBF
        ax1 = self.reliability_fig.add_subplot(gs[0, 0])
        gen_names = [g.name for g in self.generators]
        mtbfs = [self.reliability.calculate_mtbf(g) for g in self.generators]
        mtbfs = [m if m != float('inf') else 10000 for m in mtbfs]

        ax1.bar(gen_names, mtbfs, color='blue', alpha=0.7)
        ax1.set_xlabel('Generator')
        ax1.set_ylabel('MTBF (hours)')
        ax1.set_title('Mean Time Between Failures')
        ax1.grid(True, alpha=0.3, axis='y')

        # Plot 2: Reliability vs time
        ax2 = self.reliability_fig.add_subplot(gs[0, 1])
        time_hours = np.linspace(0, 168, 100)  # One week

        for gen in self.generators:
            reliability = [self.reliability.calculate_reliability(gen, t) for t in time_hours]
            ax2.plot(time_hours, reliability, linewidth=2, label=gen.name)

        ax2.set_xlabel('Time (hours)')
        ax2.set_ylabel('Reliability')
        ax2.set_title('Reliability over Time')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        # Plot 3: Failure rate
        ax3 = self.reliability_fig.add_subplot(gs[1, 0])
        failure_rates = [self.reliability.get_failure_rate(g) for g in self.generators]

        ax3.bar(gen_names, failure_rates, color='red', alpha=0.7)
        ax3.set_xlabel('Generator')
        ax3.set_ylabel('Failure Rate (failures/hour)')
        ax3.set_title('Current Failure Rate')
        ax3.grid(True, alpha=0.3, axis='y')

        # Plot 4: Derating factors
        ax4 = self.reliability_fig.add_subplot(gs[1, 1])
        derating = [self.reliability.calculate_derating(g) for g in self.generators]

        colors = ['green' if d > 0.9 else 'yellow' if d > 0.7 else 'red' for d in derating]
        ax4.bar(gen_names, derating, color=colors, alpha=0.7)
        ax4.set_xlabel('Generator')
        ax4.set_ylabel('Derating Factor')
        ax4.set_title('Current Derating')
        ax4.set_ylim([0, 1.2])
        ax4.grid(True, alpha=0.3, axis='y')

        for i, (name, d) in enumerate(zip(gen_names, derating)):
            ax4.text(i, d + 0.02, f'{d:.2f}', ha='center')

        self.reliability_canvas.draw()


def main():
    root = tk.Tk()
    app = AdvancedGridSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()

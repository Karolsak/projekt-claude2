"""
Economic Load Dispatch Simulator with Interactive Visualization
Solves the optimal load scheduling problem for multiple power plants
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np


class EconomicLoadDispatch:
    """
    Economic Load Dispatch Calculator
    Finds optimal power generation for plants to minimize total cost
    """

    def __init__(self, plants_data):
        """
        Initialize with plant data
        plants_data: list of dicts with keys: 'a', 'b', 'pmin', 'pmax'
        Cost function: C = a + b*P + c*P^2
        Incremental cost: dC/dP = a + b*P
        """
        self.plants = plants_data
        self.n_plants = len(plants_data)

    def calculate_cost(self, plant_idx, power):
        """Calculate total cost for a plant at given power output"""
        plant = self.plants[plant_idx]
        # Integrate incremental cost: C = a*P + (b/2)*P^2 + constant
        cost = plant['a'] * power + (plant['b'] / 2) * power**2
        return cost

    def incremental_cost(self, plant_idx, power):
        """Calculate incremental cost (dC/dP) for a plant"""
        plant = self.plants[plant_idx]
        return plant['a'] + plant['b'] * power

    def solve_economic_dispatch(self, total_load):
        """
        Solve economic dispatch using lambda iteration method
        Returns: dict with 'powers', 'lambda', 'total_cost', 'individual_costs'
        """
        # Lambda iteration method
        lambda_min = max([plant['a'] for plant in self.plants])
        lambda_max = max([plant['a'] + plant['b'] * plant['pmax'] for plant in self.plants])

        tolerance = 0.01
        max_iterations = 100

        for iteration in range(max_iterations):
            lambda_val = (lambda_min + lambda_max) / 2

            # Calculate power for each plant at this lambda
            powers = []
            total_power = 0

            for plant in self.plants:
                # From dC/dP = lambda: a + b*P = lambda
                # P = (lambda - a) / b
                p = (lambda_val - plant['a']) / plant['b']

                # Apply constraints
                p = max(plant['pmin'], min(plant['pmax'], p))
                powers.append(p)
                total_power += p

            # Check if power balance is satisfied
            error = total_power - total_load

            if abs(error) < tolerance:
                break
            elif error > 0:
                lambda_max = lambda_val
            else:
                lambda_min = lambda_val

        # Calculate costs
        individual_costs = [self.calculate_cost(i, powers[i]) for i in range(self.n_plants)]
        total_cost = sum(individual_costs)

        # Calculate incremental costs at optimal points
        inc_costs = [self.incremental_cost(i, powers[i]) for i in range(self.n_plants)]

        return {
            'powers': powers,
            'lambda': lambda_val,
            'total_cost': total_cost,
            'individual_costs': individual_costs,
            'incremental_costs': inc_costs,
            'iterations': iteration + 1
        }


class EconomicLoadDispatchGUI:
    """GUI Application for Economic Load Dispatch Visualization"""

    def __init__(self, root):
        self.root = root
        self.root.title("Economic Load Dispatch Simulator")
        self.root.geometry("1400x900")

        # Default plant data (from the problem)
        self.default_plants = [
            {'name': 'Plant 1', 'a': 40, 'b': 0.25, 'pmin': 30, 'pmax': 150, 'color': '#FF6B6B'},
            {'name': 'Plant 2', 'a': 50, 'b': 0.30, 'pmin': 40, 'pmax': 125, 'color': '#4ECDC4'},
            {'name': 'Plant 3', 'a': 20, 'b': 0.20, 'pmin': 50, 'pmax': 225, 'color': '#95E1D3'}
        ]

        self.plants_data = self.default_plants.copy()
        self.total_load = tk.DoubleVar(value=350)

        self.setup_ui()
        self.update_calculation()

    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(0, weight=1)

        # Left panel - Controls
        self.setup_control_panel(main_container)

        # Right panel - Visualization
        self.setup_visualization_panel(main_container)

    def setup_control_panel(self, parent):
        """Setup control panel with sliders"""
        control_frame = ttk.LabelFrame(parent, text="Control Panel", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        row = 0

        # Title
        title_label = ttk.Label(control_frame, text="Economic Load Dispatch",
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1

        # Total Load Slider
        ttk.Label(control_frame, text="Total Load (MW):", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1

        load_slider = tk.Scale(control_frame, from_=120, to=500, resolution=1,
                              orient=tk.HORIZONTAL, variable=self.total_load,
                              command=lambda x: self.update_calculation(),
                              length=300)
        load_slider.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1

        self.load_label = ttk.Label(control_frame, text=f"Load: {self.total_load.get():.1f} MW",
                                   font=('Arial', 10))
        self.load_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1

        # Plant Parameters
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1

        ttk.Label(control_frame, text="Plant Parameters", font=('Arial', 12, 'bold')).grid(
            row=row, column=0, columnspan=3, pady=(0, 10))
        row += 1

        # Store slider variables
        self.plant_sliders = []

        for i, plant in enumerate(self.plants_data):
            # Plant frame
            plant_frame = ttk.LabelFrame(control_frame, text=f"{plant['name']}", padding="10")
            plant_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
            row += 1

            plant_vars = {}

            # Coefficient 'a' slider
            ttk.Label(plant_frame, text=f"Coefficient a (₹/MW):").grid(
                row=0, column=0, sticky=tk.W)
            plant_vars['a'] = tk.DoubleVar(value=plant['a'])
            a_slider = tk.Scale(plant_frame, from_=10, to=100, resolution=1,
                              orient=tk.HORIZONTAL, variable=plant_vars['a'],
                              command=lambda x, idx=i: self.update_plant_param(idx),
                              length=250)
            a_slider.grid(row=0, column=1, sticky=(tk.W, tk.E))

            # Coefficient 'b' slider
            ttk.Label(plant_frame, text=f"Coefficient b (₹/MW²):").grid(
                row=1, column=0, sticky=tk.W)
            plant_vars['b'] = tk.DoubleVar(value=plant['b'])
            b_slider = tk.Scale(plant_frame, from_=0.05, to=1.0, resolution=0.01,
                              orient=tk.HORIZONTAL, variable=plant_vars['b'],
                              command=lambda x, idx=i: self.update_plant_param(idx),
                              length=250)
            b_slider.grid(row=1, column=1, sticky=(tk.W, tk.E))

            # Min power slider
            ttk.Label(plant_frame, text=f"Min Power (MW):").grid(
                row=2, column=0, sticky=tk.W)
            plant_vars['pmin'] = tk.DoubleVar(value=plant['pmin'])
            pmin_slider = tk.Scale(plant_frame, from_=0, to=150, resolution=5,
                                  orient=tk.HORIZONTAL, variable=plant_vars['pmin'],
                                  command=lambda x, idx=i: self.update_plant_param(idx),
                                  length=250)
            pmin_slider.grid(row=2, column=1, sticky=(tk.W, tk.E))

            # Max power slider
            ttk.Label(plant_frame, text=f"Max Power (MW):").grid(
                row=3, column=0, sticky=tk.W)
            plant_vars['pmax'] = tk.DoubleVar(value=plant['pmax'])
            pmax_slider = tk.Scale(plant_frame, from_=50, to=300, resolution=5,
                                  orient=tk.HORIZONTAL, variable=plant_vars['pmax'],
                                  command=lambda x, idx=i: self.update_plant_param(idx),
                                  length=250)
            pmax_slider.grid(row=3, column=1, sticky=(tk.W, tk.E))

            self.plant_sliders.append(plant_vars)

        # Reset button
        row += 1
        ttk.Button(control_frame, text="Reset to Default",
                  command=self.reset_to_default).grid(
            row=row, column=0, columnspan=3, pady=(20, 10))
        row += 1

        # Results display
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1

        ttk.Label(control_frame, text="Optimal Results", font=('Arial', 12, 'bold')).grid(
            row=row, column=0, columnspan=3, pady=(0, 10))
        row += 1

        self.results_text = tk.Text(control_frame, height=12, width=40, font=('Courier', 9))
        self.results_text.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E))
        row += 1

    def setup_visualization_panel(self, parent):
        """Setup visualization panel with matplotlib plots"""
        viz_frame = ttk.LabelFrame(parent, text="Visualization", padding="10")
        viz_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create matplotlib figure with subplots
        self.fig = Figure(figsize=(10, 8), dpi=100)

        # Create subplots
        self.ax1 = self.fig.add_subplot(2, 2, 1)  # Power distribution
        self.ax2 = self.fig.add_subplot(2, 2, 2)  # Cost distribution
        self.ax3 = self.fig.add_subplot(2, 2, 3)  # Incremental cost curves
        self.ax4 = self.fig.add_subplot(2, 2, 4)  # Total cost curve

        self.fig.tight_layout(pad=3.0)

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_plant_param(self, plant_idx):
        """Update plant parameters from sliders"""
        self.plants_data[plant_idx]['a'] = self.plant_sliders[plant_idx]['a'].get()
        self.plants_data[plant_idx]['b'] = self.plant_sliders[plant_idx]['b'].get()
        self.plants_data[plant_idx]['pmin'] = self.plant_sliders[plant_idx]['pmin'].get()
        self.plants_data[plant_idx]['pmax'] = self.plant_sliders[plant_idx]['pmax'].get()
        self.update_calculation()

    def update_calculation(self):
        """Update calculations and visualizations"""
        # Update load label
        self.load_label.config(text=f"Load: {self.total_load.get():.1f} MW")

        # Create dispatcher and solve
        dispatcher = EconomicLoadDispatch(self.plants_data)
        result = dispatcher.solve_economic_dispatch(self.total_load.get())

        # Update results text
        self.display_results(result)

        # Update visualizations
        self.update_plots(result, dispatcher)

    def display_results(self, result):
        """Display calculation results in text widget"""
        self.results_text.delete(1.0, tk.END)

        text = "=" * 40 + "\n"
        text += "OPTIMAL LOAD DISPATCH RESULTS\n"
        text += "=" * 40 + "\n\n"

        for i, plant in enumerate(self.plants_data):
            text += f"{plant['name']}:\n"
            text += f"  Power Output: {result['powers'][i]:.2f} MW\n"
            text += f"  Inc. Cost: ₹{result['incremental_costs'][i]:.2f}/MW\n"
            text += f"  Total Cost: ₹{result['individual_costs'][i]:.2f}\n"
            text += f"  Limits: [{plant['pmin']}-{plant['pmax']}] MW\n\n"

        text += "-" * 40 + "\n"
        text += f"Lambda (λ): ₹{result['lambda']:.2f}/MW\n"
        text += f"Total Power: {sum(result['powers']):.2f} MW\n"
        text += f"Total Cost: ₹{result['total_cost']:.2f}\n"
        text += f"Iterations: {result['iterations']}\n"
        text += "=" * 40 + "\n"

        self.results_text.insert(1.0, text)

    def update_plots(self, result, dispatcher):
        """Update all visualization plots"""
        # Clear all axes
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()

        # Plot 1: Power Distribution Bar Chart
        plant_names = [p['name'] for p in self.plants_data]
        colors = [p['color'] for p in self.plants_data]

        bars = self.ax1.bar(plant_names, result['powers'], color=colors, alpha=0.7, edgecolor='black')
        self.ax1.set_ylabel('Power Output (MW)', fontweight='bold')
        self.ax1.set_title('Optimal Power Distribution', fontweight='bold', fontsize=11)
        self.ax1.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for bar, power in zip(bars, result['powers']):
            height = bar.get_height()
            self.ax1.text(bar.get_x() + bar.get_width()/2., height,
                         f'{power:.1f} MW',
                         ha='center', va='bottom', fontsize=9, fontweight='bold')

        # Plot 2: Cost Distribution Pie Chart
        self.ax2.pie(result['individual_costs'], labels=plant_names, colors=colors,
                    autopct='%1.1f%%', startangle=90, explode=[0.05]*len(plant_names))
        self.ax2.set_title('Cost Distribution', fontweight='bold', fontsize=11)

        # Plot 3: Incremental Cost Curves
        for i, plant in enumerate(self.plants_data):
            p_range = np.linspace(plant['pmin'], plant['pmax'], 100)
            inc_costs = [dispatcher.incremental_cost(i, p) for p in p_range]
            self.ax3.plot(p_range, inc_costs, label=plant['name'],
                         color=plant['color'], linewidth=2)

            # Mark optimal point
            self.ax3.plot(result['powers'][i], result['incremental_costs'][i],
                         'o', color=plant['color'], markersize=10,
                         markeredgecolor='black', markeredgewidth=2)

        # Draw lambda line
        self.ax3.axhline(y=result['lambda'], color='red', linestyle='--',
                        linewidth=2, label=f"λ = {result['lambda']:.2f}")

        self.ax3.set_xlabel('Power Output (MW)', fontweight='bold')
        self.ax3.set_ylabel('Incremental Cost (₹/MW)', fontweight='bold')
        self.ax3.set_title('Incremental Cost Curves', fontweight='bold', fontsize=11)
        self.ax3.legend(loc='best', fontsize=8)
        self.ax3.grid(True, alpha=0.3)

        # Plot 4: Total Cost vs Load
        load_range = np.linspace(120, 500, 50)
        total_costs = []

        for load in load_range:
            try:
                res = dispatcher.solve_economic_dispatch(load)
                total_costs.append(res['total_cost'])
            except:
                total_costs.append(None)

        self.ax4.plot(load_range, total_costs, 'b-', linewidth=2)

        # Mark current operating point
        self.ax4.plot(self.total_load.get(), result['total_cost'],
                     'ro', markersize=12, markeredgecolor='black',
                     markeredgewidth=2, label='Current Operation')

        self.ax4.set_xlabel('Total Load (MW)', fontweight='bold')
        self.ax4.set_ylabel('Total Cost (₹)', fontweight='bold')
        self.ax4.set_title('Total Cost vs System Load', fontweight='bold', fontsize=11)
        self.ax4.legend(fontsize=9)
        self.ax4.grid(True, alpha=0.3)

        # Refresh canvas
        self.fig.tight_layout(pad=2.5)
        self.canvas.draw()

    def reset_to_default(self):
        """Reset all parameters to default values"""
        self.total_load.set(350)

        for i, plant in enumerate(self.default_plants):
            self.plant_sliders[i]['a'].set(plant['a'])
            self.plant_sliders[i]['b'].set(plant['b'])
            self.plant_sliders[i]['pmin'].set(plant['pmin'])
            self.plant_sliders[i]['pmax'].set(plant['pmax'])

            self.plants_data[i]['a'] = plant['a']
            self.plants_data[i]['b'] = plant['b']
            self.plants_data[i]['pmin'] = plant['pmin']
            self.plants_data[i]['pmax'] = plant['pmax']

        self.update_calculation()


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = EconomicLoadDispatchGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

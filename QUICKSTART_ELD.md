# Economic Load Dispatch - Quick Start Guide

## 🚀 Installation

### 1. Install Dependencies

```bash
pip install -r requirements_eld.txt
```

For Linux systems, you may also need to install tkinter:
```bash
sudo apt-get install python3-tk
```

## 📊 Running the Application

### Option 1: GUI Version (Interactive Visualization)

```bash
python economic_load_dispatch_simulator.py
```

**Features:**
- Interactive sliders for all parameters
- Real-time visualization with 4 charts
- Study different operating conditions
- Export-quality plots

**Requirements:**
- tkinter (GUI library)
- matplotlib, numpy

### Option 2: Command-Line Version

**Default Problem (350 MW):**
```bash
python economic_dispatch_cli.py
```

**Custom Load:**
```bash
python economic_dispatch_cli.py 400
```

**Interactive Mode:**
```bash
python economic_dispatch_cli.py -i
```

## ✅ Verify Installation

```bash
python verify_eld_solution.py
```

This will verify the mathematical solution and show detailed results.

## 📖 Example Output

```
================================================================================
ECONOMIC LOAD DISPATCH - OPTIMAL SOLUTION
================================================================================

Total System Load: 350.00 MW
Lambda (λ): 62.973 ₹/MW

--------------------------------------------------------------------------------
Plant      Power (MW)      Inc. Cost       Total Cost      Limits (MW)
--------------------------------------------------------------------------------
Plant 1         91.89         62.973     ₹   4731.20     [30-150]
Plant 2         43.24         62.973     ₹   2442.67     [40-125]
Plant 3        214.87         62.973     ₹   8914.00     [50-225]
--------------------------------------------------------------------------------
TOTAL          350.00 MW               ₹  16087.88
================================================================================
```

## 🎯 Key Learning Objectives

### 1. Equal Incremental Cost Principle
All plants operate at the same incremental cost (λ) for optimal dispatch:
```
dC₁/dP₁ = dC₂/dP₂ = dC₃/dP₃ = λ
```

### 2. Economic Merit Order
Plants with lower costs generate more power:
- **Plant 3**: Cheapest (a=20) → Generates most (215 MW)
- **Plant 1**: Medium (a=40) → Generates medium (92 MW)
- **Plant 2**: Most expensive (a=50) → Generates least (43 MW)

### 3. Impact of Constraints
When plants hit their limits, they operate at their max/min instead of at λ.

### 4. System Economics
- **Lambda (λ)**: Marginal cost of supplying additional load
- **Total Cost**: Increases quadratically with load
- **Individual Costs**: Depend on generation level and cost coefficients

## 🔬 Experiment Ideas

### Experiment 1: Load Variation
```bash
python economic_dispatch_cli.py 200
python economic_dispatch_cli.py 350
python economic_dispatch_cli.py 450
```
**Observe:** How λ changes with load, which plants hit limits first

### Experiment 2: Plant Outage
In GUI: Set Plant 3 max power to 50 MW (minimum)
**Observe:** How load redistributes, cost increases

### Experiment 3: Fuel Price Change
In GUI: Increase Plant 1 coefficient 'a' from 40 to 60
**Observe:** Plant 1 generation decreases, load shifts to other plants

### Experiment 4: All Plants at Equal Cost
In GUI: Set all plants to a=40, b=0.25
**Observe:** Load distributes evenly (when limits permit)

## 📚 Understanding the Results

### When Incremental Costs ARE Equal (✓)
All plants are operating in their optimal range, no constraints active.
```
Plant 1: 62.973 ₹/MW
Plant 2: 62.973 ₹/MW  ← All equal to λ
Plant 3: 62.973 ₹/MW
```

### When Incremental Costs are NOT Equal (✗)
Some plants are at their limits (constrained):
```
Plant 1: 75.227 ₹/MW
Plant 2: 75.227 ₹/MW  ← These two at λ
Plant 3: 65.000 ₹/MW  ← At maximum limit
```

## 🐛 Troubleshooting

### Issue: "No module named 'tkinter'"
**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS (usually pre-installed)
# Windows (usually pre-installed with Python)
```

### Issue: "No module named 'numpy'"
**Solution:**
```bash
pip install -r requirements_eld.txt
```

### Issue: Infeasible Solution
**Cause:** Total load exceeds maximum generation capacity or is below minimum
**Check:**
```
Sum of Pmin ≤ Load ≤ Sum of Pmax
120 MW ≤ Load ≤ 500 MW (for default problem)
```

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `economic_load_dispatch_simulator.py` | Main GUI application |
| `economic_dispatch_cli.py` | Command-line version |
| `verify_eld_solution.py` | Verification script |
| `requirements_eld.txt` | Python dependencies |
| `README_ECONOMIC_DISPATCH.md` | Detailed documentation |
| `QUICKSTART_ELD.md` | This quick start guide |

## 🎓 Next Steps

1. ✅ Run the default problem
2. ✅ Verify the solution matches expected results
3. ✅ Launch the GUI and explore with sliders
4. ✅ Try different load levels
5. ✅ Study constrained vs unconstrained dispatch
6. ✅ Experiment with cost coefficients

## 💡 Tips

- **Start Simple**: Begin with default values, then modify one parameter at a time
- **Watch Lambda**: λ tells you the marginal cost of the next MW
- **Check Constraints**: Plants at limits show different incremental costs
- **Compare Costs**: See which plant contributes most to total cost
- **Real-time Updates**: GUI updates instantly as you move sliders

## 📞 Support

For issues or questions:
- Check README_ECONOMIC_DISPATCH.md for detailed documentation
- Review the verification output from verify_eld_solution.py
- Ensure all dependencies are installed

---

**Happy Learning! 🎉**

Master economic dispatch and power system optimization through hands-on experimentation!

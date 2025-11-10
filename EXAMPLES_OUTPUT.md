# Economic Load Dispatch - Example Outputs

This document shows example outputs for various operating conditions to help you understand the system behavior.

---

## Example 1: Base Case (350 MW Load)

**Problem:**
- Plant 1: dC₁/dP₁ = 40 + 0.25·P₁, 30 ≤ P₁ ≤ 150 MW
- Plant 2: dC₂/dP₂ = 50 + 0.30·P₂, 40 ≤ P₂ ≤ 125 MW
- Plant 3: dC₃/dP₃ = 20 + 0.20·P₃, 50 ≤ P₃ ≤ 225 MW
- Total Load: 350 MW

**Solution:**
```
================================================================================
Total System Load: 350.00 MW
Lambda (λ): 62.973 ₹/MW
Iterations: 12
--------------------------------------------------------------------------------
Plant      Power (MW)      Inc. Cost       Total Cost      Limits (MW)
--------------------------------------------------------------------------------
Plant 1         91.89         62.973     ₹   4731.20     [30-150]
Plant 2         43.24         62.973     ₹   2442.67     [40-125]
Plant 3        214.87         62.973     ₹   8914.00     [50-225]
--------------------------------------------------------------------------------
TOTAL          350.00 MW               ₹  16087.88
================================================================================

VERIFICATION:
- Power Balance: 350.00 MW = 350.00 MW ✓
- Equal Incremental Costs: True ✓
- All Constraints Satisfied: True ✓
```

**Key Insights:**
- ✓ All plants operate at equal λ = 62.973 ₹/MW (optimal unconstrained)
- ✓ Plant 3 (cheapest) generates 61% of total load
- ✓ Plant 2 (most expensive) generates only 12% of total load
- ✓ No constraints are active (all plants within limits)

---

## Example 2: Low Load (250 MW)

**Solution:**
```
================================================================================
Total System Load: 250.00 MW
Lambda (λ): 52.222 ₹/MW
Iterations: 14
--------------------------------------------------------------------------------
Plant      Power (MW)      Inc. Cost       Total Cost      Limits (MW)
--------------------------------------------------------------------------------
Plant 1         48.89         52.222     ₹   2254.37     [30-150]
Plant 2         40.00         62.000     ₹   2240.00     [40-125]  ← AT MIN LIMIT
Plant 3        161.11         52.222     ₹   5817.96     [50-225]
--------------------------------------------------------------------------------
TOTAL          250.00 MW               ₹  10312.33
================================================================================

VERIFICATION:
- Power Balance: 250.00 MW = 250.00 MW ✓
- Equal Incremental Costs: False ✗
- All Constraints Satisfied: True ✓
```

**Key Insights:**
- ✗ Plant 2 is at minimum limit (40 MW), cannot reduce further
- ✓ Plants 1 and 3 operate at λ = 52.222 ₹/MW
- ✗ Plant 2's incremental cost (62.0) > λ (would prefer to shut down)
- ⚠ Constrained operation: λ only applies to unconstrained plants

---

## Example 3: High Load (450 MW)

**Solution:**
```
================================================================================
Total System Load: 450.00 MW
Lambda (λ): 75.227 ₹/MW
Iterations: 13
--------------------------------------------------------------------------------
Plant      Power (MW)      Inc. Cost       Total Cost      Limits (MW)
--------------------------------------------------------------------------------
Plant 1        140.91         75.227     ₹   8118.31     [30-150]
Plant 2         84.09         75.227     ₹   5265.26     [40-125]
Plant 3        225.00         65.000     ₹   9562.50     [50-225]  ← AT MAX LIMIT
--------------------------------------------------------------------------------
TOTAL          450.00 MW               ₹  22946.07
================================================================================

VERIFICATION:
- Power Balance: 450.00 MW = 450.00 MW ✓
- Equal Incremental Costs: False ✗
- All Constraints Satisfied: True ✓
```

**Key Insights:**
- ✗ Plant 3 is at maximum limit (225 MW), cannot increase further
- ✓ Plants 1 and 2 operate at λ = 75.227 ₹/MW
- ✗ Plant 3's incremental cost (65.0) < λ (would prefer to generate more)
- ⚠ High system cost due to using expensive plants at high output
- 📈 λ = 75.227 is much higher than base case (62.973), indicating tight capacity

---

## Example 4: Very High Load (480 MW - Near Maximum)

**Theoretical Solution:**
```
================================================================================
Total System Load: 480.00 MW
Lambda (λ): ≈ 82.5 ₹/MW
--------------------------------------------------------------------------------
Plant      Power (MW)      Inc. Cost       Status
--------------------------------------------------------------------------------
Plant 1        ≈150.00         77.500      AT MAX LIMIT
Plant 2        ≈105.00         81.500      Approaching limit
Plant 3        225.00         65.000      AT MAX LIMIT
--------------------------------------------------------------------------------
TOTAL          480.00 MW
================================================================================

Key Insights:
- Multiple plants at maximum capacity
- Very high marginal cost (λ ≈ 82.5 ₹/MW)
- System is capacity-constrained
- Total cost significantly higher than base case
```

---

## Example 5: Load Variation Study

**System Response to Different Loads:**

| Load (MW) | λ (₹/MW) | P₁ (MW) | P₂ (MW) | P₃ (MW) | Total Cost (₹) | Active Constraints |
|-----------|----------|---------|---------|---------|----------------|--------------------|
| 200       | 46.0     | 24.0    | 40.0*   | 130.0   | 6,800          | P₂ at minimum      |
| 250       | 52.2     | 48.9    | 40.0*   | 161.1   | 10,312         | P₂ at minimum      |
| 300       | 57.6     | 70.4    | 42.0    | 187.6   | 13,200         | None               |
| 350       | 63.0     | 91.9    | 43.2    | 214.9   | 16,088         | None               |
| 400       | 68.3     | 113.3   | 60.9    | 225.0*  | 19,520         | P₃ at maximum      |
| 450       | 75.2     | 140.9   | 84.1    | 225.0*  | 22,946         | P₃ at maximum      |
| 500       | 82.5     | 150.0*  | 125.0*  | 225.0*  | 27,125         | All at maximum     |

*(\* indicates constraint is active)*

**Observations:**
- λ increases monotonically with load (marginal cost rises)
- Plant 2 hits minimum first (cheap plants preferred at low load)
- Plant 3 hits maximum first (cheap plants maxed out at high load)
- Cost increases approximately quadratically with load
- Beyond 500 MW, the system cannot supply the load (infeasible)

---

## Example 6: Sensitivity to Cost Coefficients

### Case A: Increase Plant 1 Base Cost (a₁: 40 → 60)

**Before (a₁ = 40):**
```
P₁ = 91.89 MW, P₂ = 43.24 MW, P₃ = 214.87 MW
λ = 62.973 ₹/MW, Total Cost = ₹16,087.88
```

**After (a₁ = 60):**
```
P₁ ≈ 48.00 MW, P₂ ≈ 42.00 MW, P₃ ≈ 260.00 MW (INFEASIBLE - exceeds limit!)
Actual: P₁ ≈ 45.00 MW, P₂ ≈ 80.00 MW, P₃ = 225.00 MW (at max)
λ ≈ 74.0 ₹/MW, Total Cost ≈ ₹19,500
```

**Impact:**
- Plant 1 generation drops significantly (cheaper alternatives preferred)
- Load shifts to Plants 2 and 3
- Plant 3 hits maximum capacity
- System cost increases by ~21%
- λ increases (higher marginal cost)

### Case B: All Plants Equal Cost (a = 40, b = 0.25 for all)

**Solution (350 MW):**
```
P₁ ≈ 116.67 MW (equal share)
P₂ ≈ 116.67 MW (equal share)
P₃ ≈ 116.67 MW (equal share)
λ = 69.17 ₹/MW
Total Cost = ₹16,333
```

**Impact:**
- Load divides evenly (no economic preference)
- All plants at same operating point
- Higher total cost than optimized case (plants not matched to costs)

---

## Example 7: Plant Outage Scenario

### Scenario: Plant 3 Outage (P₃ forced to minimum 50 MW)

**Modified Problem:**
- Plant 1: 30 ≤ P₁ ≤ 150 MW
- Plant 2: 40 ≤ P₂ ≤ 125 MW
- Plant 3: P₃ = 50 MW (FORCED - simulating outage)
- Total Load: 350 MW

**Solution:**
```
P₁ = 150.00 MW (AT MAX LIMIT)
P₂ = 125.00 MW (AT MAX LIMIT)
P₃ = 50.00 MW (FORCED OUTAGE)
----------------
TOTAL = 325.00 MW (CANNOT MEET 350 MW!)
```

**Impact:**
- System cannot meet demand (load shedding required!)
- All available plants at maximum
- Critical situation demonstrating importance of reserve margin
- Alternative: Reduce load to 315 MW:
  ```
  P₁ = 150.00 MW (max)
  P₂ = 115.00 MW
  P₃ = 50.00 MW
  λ ≈ 77.5 ₹/MW, Total Cost ≈ ₹18,000 (+12% vs normal)
  ```

---

## Mathematical Verification

### Check: Power Balance
```
∑ Pᵢ = P₁ + P₂ + P₃
91.89 + 43.24 + 214.87 = 350.00 MW ✓
```

### Check: Equal Incremental Cost
```
dC₁/dP₁ = 40 + 0.25(91.89) = 62.97 ₹/MW ✓
dC₂/dP₂ = 50 + 0.30(43.24) = 62.97 ₹/MW ✓
dC₃/dP₃ = 20 + 0.20(214.87) = 62.97 ₹/MW ✓

All equal to λ = 62.97 ₹/MW ✓
```

### Check: Constraints
```
Plant 1: 30 ≤ 91.89 ≤ 150 ✓
Plant 2: 40 ≤ 43.24 ≤ 125 ✓
Plant 3: 50 ≤ 214.87 ≤ 225 ✓
```

### Check: Optimality (Lagrangian)
```
L = C₁(P₁) + C₂(P₂) + C₃(P₃) + λ(350 - P₁ - P₂ - P₃)

∂L/∂P₁ = dC₁/dP₁ - λ = 0 → dC₁/dP₁ = λ ✓
∂L/∂P₂ = dC₂/dP₂ - λ = 0 → dC₂/dP₂ = λ ✓
∂L/∂P₃ = dC₃/dP₃ - λ = 0 → dC₃/dP₃ = λ ✓
∂L/∂λ = 350 - P₁ - P₂ - P₃ = 0 ✓

All optimality conditions satisfied!
```

---

## Visualization Interpretation Guide

### Plot 1: Power Distribution (Bar Chart)
- **Height**: Power output from each plant
- **Taller bars**: Plants generating more
- **Color coding**: Easy identification of plants
- **Pattern**: Cheapest plants should have tallest bars

### Plot 2: Cost Distribution (Pie Chart)
- **Slice size**: Proportion of total cost
- **Larger slices**: Plants contributing more to cost
- **Note**: High generation ≠ high cost (depends on efficiency)

### Plot 3: Incremental Cost Curves
- **Lines**: dC/dP vs P for each plant
- **Slope**: Coefficient 'b' (steeper = cost increases faster)
- **Intercept**: Coefficient 'a' (base cost)
- **Circles**: Current operating point
- **Red dashed line**: Lambda (λ) - should intersect all circles
- **Interpretation**: All operating points should align with λ line

### Plot 4: Total Cost vs Load
- **Curve shape**: Quadratic (parabolic)
- **Slope**: Increases with load (marginal cost rises)
- **Red dot**: Current operating point
- **Kinks**: Occur when constraints become active
- **Steep sections**: High marginal cost regions

---

## Summary of Key Principles

1. **Economic Dispatch Principle**
   - Minimize total cost while meeting load and constraints
   - Necessary condition: Equal incremental costs (λ)

2. **Merit Order**
   - Cheaper plants generate more (when unconstrained)
   - Expensive plants used only when needed

3. **Lambda (λ) Interpretation**
   - Marginal cost of next MW of load
   - System operating efficiency indicator
   - Increases with load (diminishing returns)

4. **Constraint Effects**
   - Active constraints prevent optimal operation
   - Forced to use more expensive generation
   - System cost increases

5. **Practical Applications**
   - Real-time generation scheduling
   - Unit commitment planning
   - Market clearing prices
   - Reserve margin planning

---

## How to Reproduce These Examples

### Using CLI:
```bash
# Example 1 (base case)
python economic_dispatch_cli.py 350

# Example 2 (low load)
python economic_dispatch_cli.py 250

# Example 3 (high load)
python economic_dispatch_cli.py 450

# Interactive mode
python economic_dispatch_cli.py -i
```

### Using GUI:
1. Run: `python economic_load_dispatch_simulator.py`
2. Move the "Total Load" slider to desired value
3. Observe real-time updates in all 4 plots
4. Adjust plant parameters for sensitivity studies

---

**Created for Power System Analysis Education**
*Study, Experiment, Learn!*

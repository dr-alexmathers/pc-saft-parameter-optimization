# PC-SAFT Parameter Optimization

This repository contains Python scripts that implement the parameter-fitted PC-SAFT framework described in:

> **A parameter-fitted PC-SAFT framework for solubility extrapolation in drug–polymer systems**

## 📜 Overview
- `Step_1.py`: Random parameter generation and RMSRD evaluation  
- `Step_2.py`: Nelder–Mead optimization of PC-SAFT parameters  

---

## ⚙️ How It Works: Nelder–Mead Optimization of PC-SAFT Parameters

1. **Start with Initial Parameters**  
   The algorithm begins with an initial guess of the eight PC-SAFT parameters [A–H], typically the best set found from previously generated random datasets.  

2. **Define the Objective Function**  
   The objective function quantifies the fit quality by:  
   - Generating an input file for the PC-SAFT model with the current parameters  
   - Running the PC-SAFT simulation program  
   - Extracting the RMSRD value, which measures the deviation between model output and experimental data  
   - Adding a penalty if parameters lie outside their allowed ranges, guiding the search within valid limits  

3. **Iterative Parameter Adjustment**  
   The Nelder–Mead algorithm iteratively refines the parameters by manipulating a simplex in parameter space (reflection, expansion, contraction, shrinkage), aiming to minimize the RMSRD.  

4. **Boundary Enforcement**  
   At each iteration, parameters outside predefined bounds are penalized in the objective function to keep the optimization physically meaningful.  

5. **Convergence and Stopping Criteria**  
   The process continues until the maximum number of iterations is reached or the RMSRD improvement becomes negligible.  

6. **Output Optimized Parameters**  
   The final output is the set of optimized parameters that yield the lowest RMSRD, representing the best fit between the PC-SAFT model and experimental data.  

---

## 🔄 Workflow Schematic

```
 ┌───────────────────────┐
 │  Initial Parameters   │
 │   (A–H from Step_1)   │
 └───────────┬───────────┘
             │
             ▼
 ┌───────────────────────┐
 │  Objective Function   │
 │  • Run PC-SAFT        │
 │  • Compute RMSRD      │
 │  • Apply Penalties    │
 └───────────┬───────────┘
             │
             ▼
 ┌───────────────────────┐
 │ Nelder–Mead Update    │
 │  • Reflection         │
 │  • Expansion          │
 │  • Contraction        │
 │  • Shrinkage          │
 └───────────┬───────────┘
             │
             ▼
 ┌───────────────────────┐
 │ Boundary Enforcement  │
 │ (Keep parameters in   │
 │   valid ranges)       │
 └───────────┬───────────┘
             │
             ▼
 ┌───────────────────────┐
 │ Convergence Check     │
 │ • Max iterations?     │
 │ • RMSRD stable?       │
 └───────────┬───────────┘
             │
             ▼
 ┌───────────────────────┐
 │  Optimized Parameters │
 │   (Lowest RMSRD set)  │
 └───────────────────────┘
```

---

## 🛠 Usage
1. Clone this repository  
2. Place `Input_ASD_template.inp` and `Exp_data_SLE.dat` in the PC-SAFT program folder  
3. Run scripts with **Python 3.x**  

---

## 🧰 Dependencies
Install required packages via:  
```bash
pip install -r requirements.txt
```

---

## 📄 License
MIT


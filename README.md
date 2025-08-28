# PC-SAFT Parameter Optimization

This repository implements a **two-step framework** for optimizing PC-SAFT parameters in drug–polymer solubility systems, based on:

> **A parameter-fitted PC-SAFT framework for solubility extrapolation in drug–polymer systems**

---

## 📜 Overview

The workflow has **two steps**:

- **Step 1 – Random Search & Pre-Optimization**  
  Generates random parameter sets (A–H), runs PC-SAFT, evaluates RMSRD, and refines the *best* set with Nelder–Mead (local search).  

- **Step 2 – Full Nelder–Mead Optimization**  
  Starts from a chosen initial dataset (e.g., from Step 1) and performs a dedicated Nelder–Mead optimization to converge on final parameters.  

---

## 🔄 Workflow (High-Level)

```
        ┌─────────────────────────┐
        │      Step 1             │
        │ Random Search + Local   │
        │ Nelder–Mead Refinement  │
        └───────────┬─────────────┘
                    │
                    ▼
        ┌─────────────────────────┐
        │      Step 2             │
        │ Full Nelder–Mead        │
        │ Optimization            │
        └───────────┬─────────────┘
                    │
                    ▼
        ┌─────────────────────────┐
        │ Final Optimized Params  │
        │  (Lowest RMSRD found)   │
        └─────────────────────────┘
```

---

## ⚙️ Step 1 – Random Dataset Generation & Pre-Optimization

1. **Input requirements**
   - `ranges_variables.txt` – defines parameter ranges and iteration counts  
   - `Input_ASD_template.inp` – PC-SAFT input template (with placeholders `A* … H*`)  
   - `Exp_data_SLE.dat` – experimental solubility data  
   - `PC_SAFT_ASD_v2022.12.exe` – PC-SAFT executable  

2. **Process**
   - Randomly generates parameter sets within defined ranges.  
   - Creates `.inp` files and runs PC-SAFT.  
   - Extracts RMSRD values from simulation output.  
   - Saves results to `generated_PC-SAFT_datasets/` and `generated_RMSRD_values/`.  
   - Identifies the **best random dataset**.  
   - Refines it with a **local Nelder–Mead optimization**.  

3. **Output**
   - Best random dataset  
   - Locally optimized parameters  
   - RMSRD values file:  
     ```
     <drug_polymer>_RMSRD_values.txt
     ```

---

## ⚙️ Step 2 – Nelder–Mead Optimization

1. **Input requirements**
   - `initial_dataset.txt` in each drug–polymer folder  
     ```
     maxiter = 5
     
     A* = <value>
     B* = <value>
     C* = <value>
     D* = <value>
     E* = <value>
     F* = <value>
     G* = <value>
     H* = <value>
     ```
   - Same template and experimental files as Step 1.  

2. **Process**
   - Reads the initial dataset (often taken from Step 1).  
   - Runs Nelder–Mead optimization of all parameters.  
   - Creates `.inp` files, runs PC-SAFT, extracts RMSRD.  
   - Logs RMSRD evolution across iterations.  

3. **Output**
   - Final optimized parameters  
   - RMSRD value for the optimized set  
   - Results appended to:  
     ```
     <drug_polymer>_RMSRD_values.txt
     ```

---

## 🔍 Detailed Workflow (Step 2 Optimization)

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

1. **Clone this repository**  
   ```bash
   git clone <repo-url>
   cd <repo>
   ```

2. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Step 1 (random generation & local refinement)**  
   ```bash
   python Step_1.py
   ```
   - Select the **main program directory** when prompted.  
   - Then select one or more **drug–polymer folders**.  

4. **Run Step 2 (full Nelder–Mead optimization)**  
   ```bash
   python Step_2.py
   ```
   - Again select the main program directory and drug–polymer folders.  
   - Make sure each folder contains a prepared `initial_dataset.txt`.  

---

## 📂 Directory Structure

```
project/
│── Step_1.py
│── Step_2.py
│── requirements.txt
│── ranges_variables.txt
│── PC_SAFT_ASD_v2022.12.exe
│
├── generated_PC-SAFT_datasets/
├── generated_inp_files/
├── generated_RMSRD_values/
└── <drug_polymer_folders>/
    ├── Input_ASD_template.inp
    ├── Exp_data_SLE.dat
    └── initial_dataset.txt   (for Step 2)
```

---

## 📑 Example Input Files

**ranges_variables.txt**
```txt
num_datasets = 20
maxiter = 5

A_range = (0.01070, 0.04980)
B_range = (2.65800, 4.76700)
C_range = (151.60000, 470.92000)
D_range = (516.46910, 2181.90000)
E_range = (0.00952, 0.08946)
F_range = (0.03130, 0.05400)
G_range = (2.71000, 3.12000)
H_range = (205.00000, 298.04700)
```

**initial_dataset.txt**
```txt
maxiter = 5

A* = 0.029245
B* = 4.828732
C* = 369.810362
D* = 725.570054
E* = 0.050751
F* = 0.049463
G* = 2.852088
H* = 250.534061
```

---

## 📄 License
MIT

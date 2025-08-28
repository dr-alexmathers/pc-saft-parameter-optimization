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

## 🔄 Workflow

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
     A* = <value>
     B* = <value>
     C* = <value>
     D* = <value>
     E* = <value>
     F* = <value>
     G* = <value>
     H* = <value>
     maxiter = 200   # optional, default = 100
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
A_range = (0.5, 2.0)
B_range = (0.1, 1.0)
C_range = (0.0, 5.0)
D_range = (0.0, 5.0)
E_range = (0.0, 5.0)
F_range = (0.0, 5.0)
G_range = (0.0, 5.0)
H_range = (0.0, 5.0)
num_datasets = 50
maxiter = 100
```

**initial_dataset.txt**
```txt
A* = 1.2
B* = 0.5
C* = 2.3
D* = 1.8
E* = 0.9
F* = 3.1
G* = 4.0
H* = 0.7
maxiter = 200
```

---

## 📄 License
MIT

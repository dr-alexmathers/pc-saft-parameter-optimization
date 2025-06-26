import os
import shutil
import subprocess
import time
import numpy as np
import logging
from scipy.optimize import minimize
from tkinter import Tk
from tkinter import filedialog


# Function to read parameter ranges from a file
def read_parameter_ranges(file_path):
    ranges = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or '=' not in line:
                continue  # Skip empty lines or lines without '='

            try:
                key, value = line.split(' = ', 1)
                ranges[key.strip()] = eval(value.strip())
            except (ValueError, SyntaxError) as e:
                print(f"Error parsing line in variables file: '{line}' - {e}")

    return ranges


# Function to read the drug_polymer name from the template file
def read_drug_polymer_name(template_file_path):
    with open(template_file_path, 'r') as file:
        lines = file.readlines()
        drug_polymer_name = lines[1].strip().split()[0]  # Extract first string from line 2
    return drug_polymer_name


# Function to select drug_polymer folders
def select_drug_polymer_folders(base_directory):
    Tk().withdraw()  # Close the root window
    selected_folders = []
    while True:
        folder = filedialog.askdirectory(title="Select a drug_polymer folder", initialdir=base_directory)
        if not folder:
            break  # Stop if the user cancels
        selected_folders.append(folder)
    return selected_folders


# Function to copy Input_ASD_template.inp and Exp_data_SLE.dat files
def copy_template_and_exp_data_files(drug_polymer_folder):
    template_file = os.path.join(drug_polymer_folder, "Input_ASD_template.inp")
    exp_data_file = os.path.join(drug_polymer_folder, "Exp_data_SLE.dat")

    # Copy Input_ASD_template.inp to pc_saft_folder
    if os.path.exists(template_file):
        shutil.copy(template_file, os.path.join(pc_saft_folder, "Input_ASD_template.inp"))
    else:
        logging.warning(f"Input_ASD_template.inp not found in {drug_polymer_folder}. Skipping copy.")

    # Copy Exp_data_SLE.dat to pc_saft_folder
    if os.path.exists(exp_data_file):
        shutil.copy(exp_data_file, os.path.join(pc_saft_folder, "Exp_data_SLE.dat"))
    else:
        logging.warning(f"Exp_data_SLE.dat not found in {drug_polymer_folder}. Skipping copy.")


# Function to read initial dataset from user-provided file
def read_initial_dataset(file_path):
    initial_dataset = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or '=' not in line:
                continue  # Skip empty lines or lines without '='

            try:
                key, value = line.split(' = ', 1)
                if key == 'maxiter':
                    initial_dataset['maxiter'] = int(value.strip())
                else:
                    initial_dataset[key.strip()] = float(value.strip())
            except ValueError as e:
                print(f"Error parsing line in initial dataset file: '{line}' - {e}")

    return initial_dataset


# Ask the user to select the main program directory using a file dialog
Tk().withdraw()  # Hide the root window
base_directory = filedialog.askdirectory(title="Select the Main Program Directory")

# Check if a valid directory was chosen
if not base_directory:
    print("No directory selected. Exiting.")
    exit()

# Make sure the directory ends with a backslash (or forward slash for cross-platform compatibility)
base_directory = base_directory.rstrip(os.sep) + os.sep

# File paths
pc_saft_folder = os.path.join(base_directory)
executable_path = os.path.join(base_directory, "PC_SAFT_ASD_v2022.12.exe")
generated_inp_files_path = os.path.join(base_directory, "generated_inp_files")
generated_RMSRD_values_path = os.path.join(base_directory, "generated_RMSRD_values")

# Print paths for verification
print(f"Executable path: {executable_path}")

# Set up logging
logging.basicConfig(level=logging.INFO)


# Step 2: Create .inp file
def create_inp_file(dataset, file_index):
    template_path = os.path.join(pc_saft_folder, "Input_ASD_template.inp")
    with open(template_path, "r") as template_file:
        content = template_file.read()

    # Replace placeholders in template with dataset values
    content = content.replace("A*", str(dataset['A']))
    content = content.replace("B*", str(dataset['B']))
    content = content.replace("C*", str(dataset['C']))
    content = content.replace("D*", str(dataset['D']))
    content = content.replace("E*", str(dataset['E']))
    content = content.replace("F*", str(dataset['F']))
    content = content.replace("G*", str(dataset['G']))
    content = content.replace("H*", str(dataset['H']))

    inp_file_path = os.path.join(generated_inp_files_path,
                                 f"{drug_polymer_name}_dataset_{file_index}.inp")  # Updated file name
    with open(inp_file_path, "w") as inp_file:
        inp_file.write(content)

    return inp_file_path


# Step 3: Run PC-SAFT
def run_pc_saft(inp_file_path):
    shutil.copy(inp_file_path, pc_saft_folder)
    target_inp_file = os.path.join(pc_saft_folder, "Input_ASD.inp")

    if os.path.exists(target_inp_file):
        os.remove(target_inp_file)

    os.rename(os.path.join(pc_saft_folder, os.path.basename(inp_file_path)), target_inp_file)

    calc_data_file = os.path.join(pc_saft_folder, "Calc_data_SLE.dat")
    if os.path.exists(calc_data_file):
        os.remove(calc_data_file)

    subprocess.run([executable_path], cwd=pc_saft_folder)

    while not os.path.exists(calc_data_file):
        time.sleep(1)

    return calc_data_file


# Step 4: Extract RMSRD
def extract_rmsrd(calc_data_file):
    with open(calc_data_file, 'r') as file:
        for line in file:
            if line.strip().startswith("# RMSRD/%"):
                target_line = line.strip().split()
                if len(target_line) > 3 and target_line[2].replace('.', '', 1).isdigit():
                    rmsrd_value = float(target_line[2])
                    return rmsrd_value if np.isfinite(rmsrd_value) else float('inf')

    raise ValueError("RMSRD value not found or is not valid.")


# Step 6: Optimize parameters using Nelder-Mead method
def optimize_parameters(initial_guess, maxiter):
    def objective_function(params):
        dataset = {
            'A': params[0],
            'B': params[1],
            'C': params[2],
            'D': params[3],
            'E': params[4],
            'F': params[5],
            'G': params[6],
            'H': params[7]
        }

        inp_file_path = create_inp_file(dataset, 1)
        calc_data_file = run_pc_saft(inp_file_path)
        rmsrd_value = extract_rmsrd(calc_data_file)

        logging.info(f"RMSRD for parameters {params} = {rmsrd_value}")
        return rmsrd_value

    result = minimize(objective_function, initial_guess, method='Nelder-Mead', options={'maxiter': maxiter})
    logging.info(f"Optimization result: {result}")
    return result.x


# Main process
selected_drug_polymer_folders = select_drug_polymer_folders(pc_saft_folder)

for folder in selected_drug_polymer_folders:
    copy_template_and_exp_data_files(folder)
    drug_polymer_name = read_drug_polymer_name(os.path.join(folder, "Input_ASD_template.inp"))

    # Read initial dataset
    initial_dataset_file = os.path.join(folder, "initial_dataset.txt")
    initial_dataset = read_initial_dataset(initial_dataset_file)
    maxiter = initial_dataset.get('maxiter', 100)

    initial_guess = [
        initial_dataset['A*'],
        initial_dataset['B*'],
        initial_dataset['C*'],
        initial_dataset['D*'],
        initial_dataset['E*'],
        initial_dataset['F*'],
        initial_dataset['G*'],
        initial_dataset['H*']
    ]

    rmsrd_file_path = os.path.join(generated_RMSRD_values_path, f"{drug_polymer_name}_RMSRD_values.txt")
    with open(rmsrd_file_path, "w") as f:
        f.write("Starting Nelder-Mead Optimization:\n")

    # Optimize parameters using the initial dataset as the starting point
    optimized_parameters = optimize_parameters(initial_guess, maxiter)
    logging.info(f"Optimized parameters: {optimized_parameters}")

    # Create an .inp file for the optimized parameters and run PC-SAFT
    optimized_dataset = {
        'A': optimized_parameters[0],
        'B': optimized_parameters[1],
        'C': optimized_parameters[2],
        'D': optimized_parameters[3],
        'E': optimized_parameters[4],
        'F': optimized_parameters[5],
        'G': optimized_parameters[6],
        'H': optimized_parameters[7]
    }
    optimized_inp_file_path = create_inp_file(optimized_dataset, 1)
    optimized_calc_data_file = run_pc_saft(optimized_inp_file_path)

    # Extract RMSRD for the optimized parameters
    optimized_rmsrd_value = extract_rmsrd(optimized_calc_data_file)

    # Write optimized parameters and RMSRD value to the file
    with open(rmsrd_file_path, "a") as f:
        f.write(f"\nOptimized Parameters: A={optimized_parameters[0]}, B={optimized_parameters[1]}, "
                f"C={optimized_parameters[2]}, D={optimized_parameters[3]}, E={optimized_parameters[4]}, "
                f"F={optimized_parameters[5]}, G={optimized_parameters[6]}, H={optimized_parameters[7]} => "
                f"RMSRD={optimized_rmsrd_value}\n")

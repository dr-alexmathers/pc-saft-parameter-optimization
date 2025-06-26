import os
import shutil
import random
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
        # Get the drug_polymer name from line 2
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


# Ask the user to select the main program directory using a file dialog
Tk().withdraw()  # Hide the root window
base_directory = filedialog.askdirectory(title="Select the Main Program Directory")

# Check if a valid directory was chosen
if not base_directory:
    print("No directory selected. Exiting.")
    exit()

# Make sure the directory ends with a backslash (or forward slash for cross-platform compatibility)
base_directory = base_directory.rstrip(os.sep) + os.sep

# File paths now relative to the base directory
ranges_variables_file_path = os.path.join(base_directory, "ranges_variables.txt")
generated_datasets_path = os.path.join(base_directory, "generated_PC-SAFT_datasets")
generated_inp_files_path = os.path.join(base_directory, "generated_inp_files")
generated_RMSRD_values_path = os.path.join(base_directory, "generated_RMSRD_values")
pc_saft_folder = base_directory
executable_path = os.path.join(base_directory, "PC_SAFT_ASD_v2022.12.exe")

# Print paths for verification
print(f"Ranges variables file: {ranges_variables_file_path}")
print(f"Generated datasets path: {generated_datasets_path}")
print(f"Executable path: {executable_path}")

# Set up logging
logging.basicConfig(level=logging.INFO)

# Read ranges from the file
ranges = read_parameter_ranges(ranges_variables_file_path)

# Define ranges for the parameters A, B, C, D, E, F, G, H from the loaded dictionary
A_range = ranges['A_range']
B_range = ranges['B_range']
C_range = ranges['C_range']
D_range = ranges['D_range']
E_range = ranges['E_range']
F_range = ranges['F_range']
G_range = ranges['G_range']
H_range = ranges['H_range']

# Set up the parameters
num_datasets = ranges.get('num_datasets', 25)  # Default to 25 if not specified
maxiter = ranges.get('maxiter', 25)  # Default to 25 if not specified


# Step 1: Generate random datasets
def generate_random_datasets(num_datasets=num_datasets):
    datasets = []
    for i in range(1, num_datasets + 1):
        A = random.uniform(*A_range)
        B = random.uniform(*B_range)
        C = random.uniform(*C_range)
        D = random.uniform(*D_range)
        E = random.uniform(*E_range)
        F = random.uniform(*F_range)
        G = random.uniform(*G_range)
        H = random.uniform(*H_range)
        dataset = {'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F, 'G': G, 'H': H}
        datasets.append(dataset)

        # Save dataset to file
        dataset_file = os.path.join(generated_datasets_path, f"{drug_polymer_name}_dataset{i}.txt")
        with open(dataset_file, "w") as f:
            f.write(f"A: {A}\nB: {B}\nC: {C}\nD: {D}\nE: {E}\nF: {F}\nG: {G}\nH: {H}\n")
    return datasets


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
            # Check if the line starts with "# RMSRD/%"
            if line.strip().startswith("# RMSRD/%"):
                # Split the line into components
                target_line = line.strip().split()
                logging.info(f"Found RMSRD line: {target_line}")

                # Check if there's enough content and that the value is numeric
                if len(target_line) > 3 and target_line[2].replace('.', '', 1).isdigit():
                    rmsrd_value = float(target_line[2])
                    return rmsrd_value if np.isfinite(rmsrd_value) else float('inf')

    raise ValueError("RMSRD value not found or is not valid.")


# Step 5: Save RMSRD values to a file
def save_rmsrd_to_file(dataset, rmsrd_value, file_index, rmsrd_file_path):
    with open(rmsrd_file_path, "a") as f:
        f.write(f"Dataset {file_index}: A={dataset['A']}, B={dataset['B']}, C={dataset['C']}, "
                f"D={dataset['D']}, E={dataset['E']}, F={dataset['F']}, G={dataset['G']}, H={dataset['H']} => RMSRD={rmsrd_value}\n")


# Step 6: Optimize parameters using Nelder-Mead method with boundary constraints
def optimize_parameters(initial_guess):
    def objective_function(params):
        # Enforce boundaries by adding a penalty for out-of-bounds parameters
        penalty = 0.0
        bounded_params = []
        for i, param in enumerate(params):
            # Get range for each parameter
            param_range = [A_range, B_range, C_range, D_range, E_range, F_range, G_range, H_range][i]
            min_val, max_val = param_range

            # Check if parameter is out of bounds and apply penalty if so
            if param < min_val:
                penalty += (min_val - param) ** 2  # Square of the distance outside the range
                bounded_params.append(min_val)  # Corrected to boundary
            elif param > max_val:
                penalty += (param - max_val) ** 2
                bounded_params.append(max_val)
            else:
                bounded_params.append(param)  # Within bounds

        # Update the dataset with bounded parameters
        dataset = {
            'A': bounded_params[0],
            'B': bounded_params[1],
            'C': bounded_params[2],
            'D': bounded_params[3],
            'E': bounded_params[4],
            'F': bounded_params[5],
            'G': bounded_params[6],
            'H': bounded_params[7]
        }

        # Create .inp file for the current parameters
        inp_file_path = create_inp_file(dataset, 1)  # Just use file index 1 for optimization
        calc_data_file = run_pc_saft(inp_file_path)

        # Get the RMSRD value
        rmsrd_value = extract_rmsrd(calc_data_file)

        # Return the RMSRD with the penalty for out-of-bound values
        return rmsrd_value + penalty

    # Ensure initial_guess is within bounds to start optimization
    bounded_initial_guess = [
        np.clip(initial_guess[0], *A_range),
        np.clip(initial_guess[1], *B_range),
        np.clip(initial_guess[2], *C_range),
        np.clip(initial_guess[3], *D_range),
        np.clip(initial_guess[4], *E_range),
        np.clip(initial_guess[5], *F_range),
        np.clip(initial_guess[6], *G_range),
        np.clip(initial_guess[7], *H_range)
    ]

    result = minimize(objective_function, bounded_initial_guess, method='Nelder-Mead', options={'maxiter': maxiter})
    logging.info(f"Optimization result: {result}")
    return result.x  # Return the optimized parameters


# Main process
selected_drug_polymer_folders = select_drug_polymer_folders(pc_saft_folder)

for folder in selected_drug_polymer_folders:
    copy_template_and_exp_data_files(folder)
    drug_polymer_name = read_drug_polymer_name(os.path.join(folder, "Input_ASD_template.inp"))

    # Display the parameters to the user
    print(f"Starting optimization for drug_polymer: {drug_polymer_name}")
    print(f"Number of randomly generated datasets: {num_datasets}")
    print(f"Maximum number of iterations for optimization: {maxiter}\n")

    datasets = generate_random_datasets(num_datasets)

    rmsrd_file_path = os.path.join(generated_RMSRD_values_path, f"{drug_polymer_name}_RMSRD_values.txt")

    # Clear the RMSRD values file
    with open(rmsrd_file_path, "w") as f:
        f.write("RMSRD values for generated datasets:\n")

    best_rmsrd_value = float('inf')
    best_parameters = None

    for index, dataset in enumerate(datasets, start=1):
        inp_file_path = create_inp_file(dataset, index)
        calc_data_file = run_pc_saft(inp_file_path)

        try:
            rmsrd_value = extract_rmsrd(calc_data_file)
            save_rmsrd_to_file(dataset, rmsrd_value, index, rmsrd_file_path)

            # Update best parameters if this RMSRD is the lowest found
            if rmsrd_value < best_rmsrd_value:
                best_rmsrd_value = rmsrd_value
                best_parameters = [dataset['A'], dataset['B'], dataset['C'], dataset['D'],
                                   dataset['E'], dataset['F'], dataset['G'], dataset['H']]
        except ValueError as e:
            logging.error(e)

    # Optimize parameters using the best dataset
    optimized_parameters = optimize_parameters(best_parameters)
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
    optimized_inp_file_path = create_inp_file(optimized_dataset, 1)  # Using index 1 for consistency
    optimized_calc_data_file = run_pc_saft(optimized_inp_file_path)

    # Extract RMSRD for the optimized parameters
    optimized_rmsrd_value = extract_rmsrd(optimized_calc_data_file)

    # Write optimized parameters and their RMSRD value to the RMSRD file
    with open(rmsrd_file_path, "a") as f:
        f.write(f"\nOptimized Parameters: A={optimized_parameters[0]}, B={optimized_parameters[1]}, "
                f"C={optimized_parameters[2]}, D={optimized_parameters[3]}, E={optimized_parameters[4]}, "
                f"F={optimized_parameters[5]}, G={optimized_parameters[6]}, H={optimized_parameters[7]} => "
                f"RMSRD={optimized_rmsrd_value}\n")

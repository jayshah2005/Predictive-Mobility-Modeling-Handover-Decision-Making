import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
import os
import ast

metrics = {
    "Num_HO": "NumHO",
    "Failed_HO": "FailHO",
    "PingPong_HO": "PingPongHO",
    "Time_HO": "TimeHO",
    "Frame_Loss": "PlrHO"
}

# algorithms = ["hcophd", "pahd", "hmudh", "mla", "nhd"]
algorithms = ["hcophd"]

script_dir = os.path.dirname(os.path.abspath(__file__))
densities = np.array([100, 200, 300, 400])
n_samples = 5
t_value = st.t.ppf(0.975, df=n_samples-1)

for metric_label, folder_name in metrics.items():
    plt.figure()
    
    for algo in algorithms:
        file_path = os.path.join(script_dir, f"../CIResults/{folder_name}/{algo}.txt")
        
        with open(file_path, "r") as f:
            lines = f.readlines()
            
        arrays = []
        for line in lines:
            if line.startswith("a: "):
                arrays.append(ast.literal_eval(line.strip()[3:]))
                if len(arrays) == len(densities):
                    break
        
        means = []
        errors = []
        print(arrays)
        
        for data in arrays:
            sample_data = np.array(data[:n_samples])
            
            mean_val = np.mean(sample_data)
            std_val = np.std(sample_data, ddof=1)
            std_err = std_val / np.sqrt(n_samples)
            margin = t_value * std_err
            
            means.append(mean_val)
            errors.append(margin)
        
        plt.errorbar(densities, means, yerr=errors, label=algo.upper(), capsize=3)

    plt.title(metric_label)
    plt.xlabel("Density")
    plt.legend()
    plt.grid(True)
    plt.show()
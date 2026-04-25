import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
import os
import ast

densities = np.array([100, 200, 300, 400])

def load_and_group(path):
    df = pd.read_csv(path)
    n = 5

    df["Density"] = np.repeat(densities, n)

    df["Throughput"] = (df["Num_HO"] - df["Failed_HO"]) / df["EndSimTime"]
    df["Frame_Loss"] = df["PLR_HO"]

    grouped = df.groupby("Density")

    mean = grouped.mean()
    std = grouped.std()

    std_err = std / np.sqrt(n)

    # t critical value
    t_value = st.t.ppf(0.975, df=n-1)

    margin = t_value * std_err

    return mean, margin

def load_txt_data(folder_name, algo="hcophd"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, f"../CIResults/{folder_name}/{algo}.txt")
    
    with open(file_path, "r") as f:
        lines = f.readlines()
        
    arrays = []
    for line in lines:
        if line.startswith("a: "):
            arrays.append(ast.literal_eval(line.strip()[3:]))
            if len(arrays) == len(densities):
                break
    
    n_samples = 5
    t_value = st.t.ppf(0.975, df=n_samples-1)
    
    means = []
    errors = []
    for data in arrays:
        sample_data = np.array(data[:n_samples])
        mean_val = np.mean(sample_data)
        std_val = np.std(sample_data, ddof=1)
        std_err = std_val / np.sqrt(n_samples)
        margin = t_value * std_err
        
        means.append(mean_val)
        errors.append(margin)
        
    return means, errors

full_mean, full_std = load_and_group(os.path.join(os.path.dirname(__file__), "../handover_performance_results_wSVR.csv"))

metrics = {
    "Num_HO": "NumHO",
    "Failed_HO": "FailHO",
    "PingPong_HO": "PingPongHO",
    "Time_HO": "TimeHO",
    "Frame_Loss": "PlrHO"
}

for metric, folder_name in metrics.items():
    plt.figure()
    
    # Load txt data for HCO-PHD
    txt_means, txt_errors = load_txt_data(folder_name, "hcophd")
    plt.errorbar(densities, txt_means, yerr=txt_errors, label="HCO-PHD", capsize=3)
    
    # Load CSV data for HCO-PHD + SVR
    plt.errorbar(densities, full_mean[metric], yerr=full_std[metric], label="HCO-PHD + SVR", capsize=3)

    plt.title(metric)
    plt.xlabel("Density")
    plt.legend()
    plt.grid(True)
    plt.show()
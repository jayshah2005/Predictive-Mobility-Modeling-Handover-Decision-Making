import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st

densities = np.arange(100, 1100, 100)

import scipy.stats as st

def load_and_group(path):
    df = pd.read_csv(path)

    df["Density"] = np.repeat(densities, 10)

    df["Throughput"] = (df["Num_HO"] - df["Failed_HO"]) / df["EndSimTime"]
    df["Frame_Loss"] = df["PLR_HO"]

    grouped = df.groupby("Density")

    mean = grouped.mean()
    std = grouped.std()

    n = 10
    std_err = std / np.sqrt(n)

    # t critical value
    t_value = st.t.ppf(0.975, df=n-1)

    margin = t_value * std_err
    
    print(mean, margin)

    return mean, margin

base_mean, base_std = load_and_group("./../handover_performance_results_without_svm.csv")
full_mean, full_std = load_and_group("./../handover_performance_results.csv")

# plt.figure(figsize=(8,5))

# plt.errorbar(densities,
#              base_mean["Frame_Loss"],
#              yerr=base_std["Frame_Loss"],
#              marker='o',
#              capsize=3,
#              label="GCN + LSTM")

# plt.errorbar(densities,
#              full_mean["Frame_Loss"],
#              yerr=full_std["Frame_Loss"],
#              marker='s',
#              capsize=3,
#              label="GCN + LSTM + SVM")

# plt.xlabel("Density of Vehicles")
# plt.ylabel("Frame Loss Ratio")
# plt.legend()
# plt.grid(True)
# plt.show()

# plt.figure()

# plt.errorbar(densities,
#              base_mean["Num_HO"],
#              yerr=base_std["Num_HO"],
#              label="GCN + LSTM")

# plt.errorbar(densities,
#              full_mean["Num_HO"],
#              yerr=full_std["Num_HO"],
#              label="GCN + LSTM + SVM")

# plt.xlabel("Density")
# plt.ylabel("Number of Handovers")
# plt.legend()
# plt.show()

# plt.figure()

# plt.errorbar(densities,
#              base_mean["Time_HO"],
#              yerr=base_std["Time_HO"],
#              label="GCN + LSTM")

# plt.errorbar(densities,
#              full_mean["Time_HO"],
#              yerr=full_std["Time_HO"],
#              label="GCN + LSTM + SVM")

# plt.xlabel("Density")
# plt.ylabel("Average HO Time")
# plt.legend()
# plt.show()

metrics = ["Num_HO", "Failed_HO", "PingPong_HO", "Time_HO", "Frame_Loss"]

for metric in metrics:
    plt.figure()
    plt.errorbar(densities, base_mean[metric], yerr=base_std[metric], label="GCN+LSTM")
    plt.errorbar(densities, full_mean[metric], yerr=full_std[metric], label="GCN+LSTM+SVR")

    # plt.plot(densities, base_mean[metric], marker='o', label="GCN+LSTM")
    # plt.plot(densities, full_mean[metric], marker='s', label="GCN+LSTM+SVR")

    plt.title(metric)
    plt.xlabel("Density")
    plt.legend()
    plt.grid(True)
    plt.show()
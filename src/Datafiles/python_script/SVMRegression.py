import numpy as np
import pandas as pd
import sys
import os

vehicleId = sys.argv[1]
predict_At = sys.argv[2]
# vehicleId = 2087
# predict_At = 69

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (Datafiles directory)
datafiles_dir = os.path.dirname(script_dir)
# Construct path to simulator_data.csv (should be in Datafiles directory, one level up from python_script/)
simulator_data_path = os.path.join(datafiles_dir, 'simulator_data.csv')

# Load the dataset with vehicle position data (Time, vehicleId, TowerID, RSSI, Distance, X, Y)
# Note: dataStorage.csv cannot be used as fallback because it lacks X,Y coordinate columns [5,6]
dataset = pd.read_csv(simulator_data_path)

HISTORY_LEN = int(os.getenv("SVR_HISTORY_LEN", "5"))
MIN_SAMPLES = HISTORY_LEN + 1

pred_1 = [0, 0]
vehicle_data = dataset.loc[dataset["vehicleId"].values == int(vehicleId)]

def build_history_features(df, history_len):
    if df.empty:
        return None

    history = df.tail(history_len)
    history_len = len(history)

    times = history['Time'].values
    xs = history['X'].values
    ys = history['Y'].values

    deltas_t = np.diff(times, prepend=times[0])
    deltas_x = np.diff(xs, prepend=xs[0])
    deltas_y = np.diff(ys, prepend=ys[0])

    feature_vector = np.concatenate([
        times,
        xs,
        ys,
        deltas_t,
        deltas_x,
        deltas_y
    ])

    return feature_vector.reshape(1, -1)

if len(vehicle_data) >= MIN_SAMPLES:
    from sklearn.preprocessing import StandardScaler
    from sklearn.multioutput import MultiOutputRegressor
    from sklearn.svm import SVR

    history_vectors = []
    targets = []

    for start in range(len(vehicle_data) - HISTORY_LEN):
        window = vehicle_data.iloc[start:start + HISTORY_LEN]
        feature_vec = build_history_features(window, HISTORY_LEN)
        if feature_vec is None:
            continue
        history_vectors.append(feature_vec[0])
        targets.append(vehicle_data.iloc[start + HISTORY_LEN][['X', 'Y']].values)

    if history_vectors:
        history_matrix = np.vstack(history_vectors)
        targets_matrix = np.vstack(targets)

        scaler = StandardScaler()
        history_scaled = scaler.fit_transform(history_matrix)

        svrRegressor = SVR(kernel='rbf')
        multiOutReg = MultiOutputRegressor(svrRegressor)
        multiOutReg.fit(history_scaled, targets_matrix)

        latest_window = vehicle_data.iloc[-HISTORY_LEN:]
        future_features = build_history_features(latest_window, HISTORY_LEN)
        if future_features is not None:
            future_features[0][HISTORY_LEN - 1] = float(predict_At)
            future_scaled = scaler.transform(future_features)
            pred_1 = multiOutReg.predict(future_scaled)

output_path = os.path.join(script_dir, 'outputSVR.txt')
with open(output_path, 'w+') as f:
    f.write('%s %s \n ' % (pred_1[0][0], pred_1[0][1]))
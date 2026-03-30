# Prediction Models Documentation: Complete Integration Guide

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture & Components](#architecture--components)
3. [gcn_lstm.py - GCN-LSTM Signal Prediction](#gcn_lstmpy---gcn-lstm-signal-prediction)
4. [SVMRegression.py - Vehicle Position Prediction](#svmregressionpy---vehicle-position-prediction)
5. [Data Collection & Flow](#data-collection--flow)
6. [C++ Integration](#c-integration)
7. [File Formats & Paths](#file-formats--paths)
8. [Build & Execution](#build--execution)
9. [Testing & Validation](#testing--validation)
10. [Troubleshooting](#troubleshooting)

---

## System Overview

### Project Purpose

Simu5G is an OMNeT++/INET-based 5G/LTE network simulator with a **proactive handover system** that uses machine learning to predict network conditions and make intelligent handover decisions **before signal quality degrades**.

### Key Innovation

**Ensemble Prediction Approach**:
- **GCN-LSTM** predicts: Signal Quality (RSSI), Base Station Load, Distance
- **SVMRegression** predicts: Vehicle position (X, Y coordinates)
- **Ensemble Decision**: All three conditions must be favorable to trigger handover

```
if ((rssi >= predictedRSSI) && (load <= predictedLoad) && (dist <= predictedDist))
    → Trigger handover to candidate base station
```

### Key Technologies

- **OMNeT++ 6.0**: Event-driven network simulator core
- **INET 4.4.0**: Network protocol stack (MAC/RLC/PDCP/IP layers)
- **Python 3**: Machine learning models
  - **PyTorch + torch_geometric**: GCN-LSTM implementation
  - **scikit-learn**: SVMRegression implementation
- **Veins/SUMO**: Vehicular mobility simulation
- **X2 Interface**: Inter-base-station handover coordination

---

## Architecture & Components

### 1. Data Collection Pipeline

#### Broadcast Reception → Metrics Collection
**File**: [src/stack/phy/layer/LtePhyUe.cc#L510-L620](src/stack/phy/layer/LtePhyUe.cc#L510-L620)

**Function**: `handoverHandler()`

**Triggered**: Every broadcast message (≈1ms intervals)

**Collects**:
- **RSSI**: Received signal strength indicator (from channel model)
- **Distance**: Vehicle distance to serving/candidate towers (from channel model)
- **Tower Load**: Base station load based on connected vehicles (calculated)
- **Speed**: Vehicle velocity (from mobility model)
- **Position**: Vehicle X,Y coordinates (from mobility model)

#### Data Storage
**Primary Storage**: `src/Datafiles/dataStorage.csv`
- Format: `Time,VehicleID,TowerID,RSSI,Distance,TowerLoad`
- Updated every broadcast (≈1ms)
- Used by: **gcn_lstm.py**

**Secondary Storage**: `src/Datafiles/simulator_data.csv`
- Format: `Time,vehicleId,TowerID,RSSI,Distance,X,Y`
- Updated every broadcast (≈1ms)
- Used by: **SVMRegression.py**

### 2. Prediction Pipeline

#### Every 10 Simulation Seconds: Run GCN-LSTM
```
t=10s, t=20s, t=30s, ... → Execute gcn_lstm.py
```

**Input**: `dataStorage.csv` (all collected metrics)
**Output**: Three predicted values (parsed from stdout)

#### Every 15 Simulation Seconds: Run SVMRegression
```
t=15s, t=30s, t=45s, ... → Execute SVMRegression.py <vehicleID> <futureTime>
```

**Input**: `simulator_data.csv` (position data only)
**Output**: Predicted X,Y coordinates

### 3. Handover Decision

**Decision Logic** [LtePhyUe.cc#L644](src/stack/phy/layer/LtePhyUe.cc#L644):
```cpp
if ((rssi >= predictedRSSI) && (eachTowerLoad <= predictedTowerLoad) && (dist <= predictedDistance))
{
    // Trigger handover
}
```

---

## gcn_lstm.py - GCN-LSTM Signal Prediction

### Purpose

Predicts three network metrics using a hybrid GCN-LSTM architecture:
1. **Tower Load**: Base station congestion level (0-1)
2. **RSSI**: Received signal strength indicator (dB)
3. **Distance**: Vehicle distance to tower (meters)

### How It's Called

**Location**: [src/stack/phy/layer/LtePhyUe.cc#L619-L624](src/stack/phy/layer/LtePhyUe.cc#L619-L624)

```cpp
if ((int)simTime().dbl() % 10 == 0 && !isRunPythonScript)
{
    callingPython(filePath_LtePhyUe+"python_script/gcn_lstm.py");
    clearHalfFileData(filePath_LtePhyUe+"dataStorage.csv");
    isRunPythonScript = true;
}
```

**Frequency**: Every 10 simulation seconds

### Input Data

**File**: `dataStorage.csv`

**Format**:
```
Time,VehicleID,TowerID,RSSI,Distance,TowerLoad
10.0,2087,1,95.3,500.2,0.45
10.01,2087,2,94.8,505.1,0.50
```

**Columns Required**:
- **TowerLoad** (Col 5): Node feature in GCN
- **RSSI** (Col 3): Edge weight in GCN
- **Distance** (Col 4): Edge weight in GCN

### Processing Logic

**Architecture**:

1. **Data Loading & Normalization**
   ```python
   features = scaler.fit_transform(df[['TowerLoad', 'RSSI', 'Distance']].values)
   ```

2. **Graph Construction**
   - Nodes: One per unique tower ID
   - Edges: Between towers with recorded data
   - Node Features: TowerLoad
   - Edge Weights: RSSI and Distance

3. **GCN Layer** - Learns graph structure and node relationships

4. **LSTM Layer** - Learns temporal patterns

5. **Training**: 25 epochs with Adam optimizer, MSE loss

### Output Data

**Format** (three print statements):
```
Final Predicted Tower Load: 0.47
Final Predicted RSSI: 92.5
Final Predicted Distance: 512.1
```

**Parsing** [LtePhyUe.cc#L424-L444](src/stack/phy/layer/LtePhyUe.cc#L424-L444):
- Uses `sscanf()` to extract double values
- Updates global variables: `predictedTowerLoad`, `predictedRSSI`, `predictedDistance`

### Critical Path Fix

**Original** (❌ Would Fail):
```python
df = pd.read_csv('/home/guest/Downloads/.../dataStorage.csv')
```

**Updated** (✅ Fixed):
```python
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '..', 'dataStorage.csv')
df = pd.read_csv(data_path, sep=",")
```

### Dependencies

```
pandas>=1.0.0
torch>=1.9.0
torch-geometric>=2.0.0
scikit-learn>=0.24.0
numpy>=1.19.0
```

---

## SVMRegression.py - Vehicle Position Prediction

### Purpose

Predicts future vehicle X,Y coordinates using Support Vector Regression to enable distance-based handover decisions.

### How It's Called

**Location**: [src/stack/phy/layer/LtePhyUe.cc#L473-L476](src/stack/phy/layer/LtePhyUe.cc#L473-L476)

```cpp
void LtePhyUe::runSVR(unsigned short vehicleID, int simTime)
{
    std::string pypredSVR_CmdPyCpp = "python3 " + filePath_LtePhyUe + 
        "python_script/SVMRegression.py " + std::to_string(vehicleID) + 
        " " + std::to_string(simTime);
    system(pypredSVR_CmdPyCpp.c_str());
}
```

**Frequency**: Every 15 simulation seconds

**Command Example**:
```bash
python3 /path/to/python_script/SVMRegression.py 2087 20
```

### Input Data

**File**: `simulator_data.csv`

**Format**:
```
Time,vehicleId,TowerID,RSSI,Distance,X,Y
10.0,2087,1,95.3,500.2,1000.45,2000.75
10.01,2087,2,94.8,505.1,1001.20,2001.30
```

**Columns Required**:
- `Time` (chronological ordering and delta computation)
- `X`, `Y` (absolute UE coordinates used both as history context and prediction targets)
- `vehicleId` (row filter so each SVR instance trains per vehicle)

### Processing Logic

1. **Load & Filter**: Read `simulator_data.csv`, then slice rows where `vehicleId == <UE>`.
2. **History Guard**: Require at least `HISTORY_LEN + 1` samples (default `HISTORY_LEN = 5`, configurable via the `SVR_HISTORY_LEN` environment variable). Until that threshold is met the script outputs `0 0`, so the C++ layer falls back to instantaneous distance.
3. **Feature Construction**:
   - Slide a window of `HISTORY_LEN` rows across `vehicle_data`.
   - For each window, flatten the last `HISTORY_LEN` `(Time, X, Y)` triples and append their first-order differences `(Δt, Δx, Δy)` computed directly from those rows. This captures both position and instantaneous velocity without introducing new logged metrics.
4. **Training**: Stack all window vectors into a matrix, scale with `StandardScaler`, and fit `MultiOutputRegressor(SVR(kernel='rbf'))` to predict the next `(X, Y)` sample following each window.
5. **Inference**: Take the most recent `HISTORY_LEN` rows, build the same feature vector, replace the final time entry with `predict_At` (future horizon), scale, and run `predict()` to obtain the next `(X, Y)` estimate.

### Output Data

**File**: `outputSVR.txt`

**Format** (two space-separated floats):
```
1010.45 2005.20
```

**Fallbacks**:
- **Insufficient history** (`len(vehicle_data) < HISTORY_LEN + 1`): script writes `0 0` so `LtePhyUe` reuses the instantaneous distance from `dist.txt`.
- **No rows for vehicle**: same `0 0` output.

**Parsing** [LtePhyUe.cc#L481-L488](src/stack/phy/layer/LtePhyUe.cc#L481-L488):
```cpp
std::pair<double, double> LtePhyUe::getParfromFileForSVR(...)
{
    file >> xCoord >> yCoord;  // Read two space-separated doubles
    return std::make_pair(xCoord, yCoord);
}
```

### Distance Calculation

**Function** [LtePhyUe.cc#L489-L501](src/stack/phy/layer/LtePhyUe.cc#L489-L501):

```cpp
double LtePhyUe::calculatePredictedDistance(double predX, double predY, const inet::Coord& towerCoord)
{
    double dx = predX - towerCoord.x;
    double dy = predY - towerCoord.y;
    return sqrt(dx * dx + dy * dy);  // Euclidean distance
}
```

### Path Robustness

**Fallback Chain** [SVMRegression.py#L16-L28](src/Datafiles/python_script/SVMRegression.py#L16-L28):

```python
script_dir = os.path.dirname(os.path.abspath(__file__))
datafiles_dir = os.path.dirname(script_dir)
simulator_data_path = os.path.join(datafiles_dir, 'simulator_data.csv')

# Note: Removed fallback to dataStorage.csv because it lacks X,Y columns
# dataStorage.csv only has: Time,VehicleID,TowerID,RSSI,Distance,TowerLoad
# SVMRegression needs columns [5,6] which don't exist in dataStorage.csv
```

### Dependencies

```
numpy>=1.19.0
pandas>=1.0.0
scikit-learn>=0.24.0
```

---

## Data Collection & Flow

### Timeline Example

#### t=0-10 seconds: Initialization & Collection
```
Every broadcast (≈1ms):
  → LtePhyUe::handoverHandler() called
  → RSSI, distance, tower load collected
  → writeToCSV(dataStorage.csv)          [for gcn_lstm.py]
  → writeVehiclePositionToCSV(...)       [for SVMRegression.py]
```

#### t=10 seconds: First GCN-LSTM Prediction
```
→ GCN-LSTM prediction triggered
→ dataStorage.csv has ~14,400 rows (100KB)
→ Model trains and predicts
→ Predictions: TowerLoad, RSSI, Distance
→ CSV reduced to half size: 7,200 rows
```

#### t=15 seconds: First SVR Prediction
```
→ runSVR(vehicleID, 20) called
→ SVMRegression.py executed
→ Position predicted at t=20
→ outputSVR.txt written
→ Distance calculated using tower coordinates
```

#### t=15+: Handover Decisions
```
For each broadcast:
  → Check: (rssi >= predictedRSSI) && (load <= predictedLoad) && (dist <= predictedDist)
  → If all true: handover triggered
  → X2 procedure executed
  → Metrics tracked
```

### Data Files Summary

| File | Location | Format | Updated | Usage |
|------|----------|--------|---------|-------|
| dataStorage.csv | Datafiles/ | CSV | Every ~1ms | gcn_lstm.py input |
| simulator_data.csv | Datafiles/ | CSV | Every ~1ms | SVMRegression.py input |
| outputSVR.txt | Datafiles/python_script/ | Text (2 nums) | Every 15s | Predicted X,Y |

---

## C++ Integration

### Core Functions

#### Data Collection
- **`writeToCSV()`** [LtePhyUe.cc#L320-L340]: Appends to dataStorage.csv
- **`writeVehiclePositionToCSV()`** [LtePhyUe.cc#L354-L373]: Appends to simulator_data.csv

#### Python Execution
- **`callingPython()`** [LtePhyUe.cc#L419-L446]: Executes gcn_lstm.py, parses output
- **`runSVR()`** [LtePhyUe.cc#L473-L476]: Executes SVMRegression.py with arguments

#### Utilities
- **`getParfromFileForSVR()`** [LtePhyUe.cc#L481-L488]: Reads outputSVR.txt
- **`calculatePredictedDistance()`** [LtePhyUe.cc#L489-L501]: Euclidean distance
- **`clearHalfFileData()`** [LtePhyUe.cc#L373-L410]: CSV size management
- **`calculateEachTowerLoad()`** [LtePhyUe.cc#L285-L309]: Base station load
- **`getDoubleValueFile()`** [LtePhyUe.cc#L311-L319]: Read metric files

### Core Handover Handler

**`handoverHandler()`** [LtePhyUe.cc#L510-L680]

Central function that:
1. Processes broadcast messages
2. Collects network metrics
3. Updates CSV files
4. Calls prediction scripts (periodically)
5. Makes handover decisions
6. Triggers handover execution

---

## File Formats & Paths

### CSV Formats

#### dataStorage.csv
```
Time,VehicleID,TowerID,RSSI,Distance,TowerLoad
10.0,2087,1,95.3,500.2,0.45
```
- Used by: gcn_lstm.py
- Size: ~1MB per hour

#### simulator_data.csv
```
Time,vehicleId,TowerID,RSSI,Distance,X,Y
10.0,2087,1,95.3,500.2,1000.45,2000.75
```
- Used by: SVMRegression.py
- Size: ~2MB per hour

### Path Resolution

#### C++ Base Path (LtePhyUe.h#L178)
```cpp
std::string filePath_LtePhyUe = 
    "/home/guest/Downloads/Predictive-Mobility-Modeling-Handover-Decision-Making/Project_GCN_LSTM_HO/simu5G/src/Datafiles/";
```
⚠️ **Hardcoded**: Must update for new machines

#### GCN-LSTM Path (gcn_lstm.py#L12-L15)
```python
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '..', 'dataStorage.csv')
```
✅ **Dynamic**: Works on any machine

#### SVMRegression Path (SVMRegression.py#L12-L28)
```python
script_dir = os.path.dirname(os.path.abspath(__file__))
datafiles_dir = os.path.dirname(script_dir)
simulator_data_path = os.path.join(datafiles_dir, 'simulator_data.csv')
```
✅ **Dynamic**: Works on any machine

---

## Build & Execution

### Build Commands

```bash
# From project root
. setenv                    # Source environment

# Generate makefiles (one-time)
make makefiles

# Build release version
make

# Build debug version
make MODE=debug

# Clean artifacts
make clean
```

### Run Simulation

```bash
# Navigate to simulation directory
cd simulations/NR/ProactiveHO

# Execute
./run
```

---

## Testing & Validation

### Test GCN-LSTM
```bash
cd src/Datafiles/python_script

# Create test dataStorage.csv with sample data
# Run the script
python3 gcn_lstm.py

# Verify output printed to console
```

### Test SVMRegression
```bash
cd src/Datafiles/python_script

# Create simulator_data.csv with sample data
python3 SVMRegression.py 2087 160

# Check outputSVR.txt
cat outputSVR.txt
```

### Performance Metrics
- **Handover Count**: Reasonable for scenario
- **Failed Handovers**: < 5%
- **Ping-Pong Rate**: < 10% of HOs
- **Packet Loss**: Minimal during handover

---

## Troubleshooting

### Common Issues

#### `ModuleNotFoundError: No module named 'torch'`
```bash
pip3 install torch torch-geometric scikit-learn pandas
```

#### `FileNotFoundError: dataStorage.csv`
- Verify simulation running (≥15 seconds for data)
- Check CSV exists: `ls -la src/Datafiles/dataStorage.csv`

#### Paths fail on new machine
Replace hardcoded path in LtePhyUe.h with relative or environment variable approach

#### CSV grows unbounded
Verify `clearHalfFileData()` called (line 623 in handoverHandler)

#### Predictions always (0, 0, 0)
- Test Python script manually
- Check output format matches sscanf pattern
- Verify dataStorage.csv has data

---

## Summary

### Key Components

1. **GCN-LSTM** (every 10s): Network quality prediction
   - Input: dataStorage.csv
   - Output: TowerLoad, RSSI, Distance predictions

2. **SVMRegression** (every 15s): Vehicle position prediction
   - Input: simulator_data.csv
   - Output: Predicted X,Y coordinates

3. **Ensemble Handover**: All conditions required
   - RSSI ≥ predicted, Load ≤ predicted, Distance ≤ predicted

4. **Data Files**: Auto-generated by C++
   - dataStorage.csv (network metrics)
   - simulator_data.csv (vehicle positions)

5. **Paths**: ✅ Python scripts portable, ⚠️ C++ hardcoded (needs fix)

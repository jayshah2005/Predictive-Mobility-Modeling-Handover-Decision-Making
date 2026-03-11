# Proactive Handover Prediction in Vehicular Networks

## Overview

This project investigates **machine learning-based handover prediction** in vehicular networks using hybrid deep learning models. We compare Graph Convolutional Networks combined with LSTM (GCN+LSTM) against an ensemble approach (GCN+LSTM+SVM) to predict optimal handover points in 5G mobile networks, minimizing latency and packet loss during vehicle mobility.

## Technologies & Skills Demonstrated

- **Networking**: 5G/LTE protocol stacks, handover mechanisms, mobility management
- **Machine Learning**: Graph Neural Networks, LSTM, ensemble methods, PyTorch/TensorFlow
- **Simulation**: Discrete event simulation, network modeling, performance analysis
- **Systems Integration**: Bridging ML frameworks with C++ simulators, data pipeline design
- **Research Methodology**: Comparative analysis, metrics definition, reproducible experiments

## Technical Approach

### Architecture
- **GCN+LSTM**: Captures temporal-spatial dependencies using graph convolutions on network topology + sequential LSTM layers for temporal patterns
- **GCN+LSTM+SVM**: Ensemble approach adding SVM for classification refinement, improving prediction accuracy

### Integration & Simulation
- **Simu5G**: 5G network simulator for realistic LTE/NR scenarios
- **OMNeT++**: Discrete event simulator providing the core simulation framework
- **VEINS**: Vehicular network integration layer
- **SUMO**: Realistic traffic and mobility patterns for vehicles

### Evaluation Metrics
- Handover success rate
- Handover latency (milliseconds)
- Packet loss ratio during transitions
- Prediction accuracy (precision, recall, F1-score)

## Key Features

**Deep Learning Integration**: Seamless integration of PyTorch/TensorFlow models with Simu5G simulation engine  
**Realistic Scenarios**: Vehicle mobility, path loss, interference, and multi-cell coverage variations  
**Ensemble Comparison**: Systematic comparison of single-model vs. ensemble approaches  
**Comprehensive Analysis**: Performance benchmarks across different vehicle speeds and traffic loads  

## Publications & Reports

Detailed documentation about the project available in: `README_PROACTIVE_HO.md`
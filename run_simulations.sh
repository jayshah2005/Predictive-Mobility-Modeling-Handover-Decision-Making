#!/bin/bash

# --- Terminal 1: run veins_launchd ---
gnome-terminal -- bash -c "
cd \$HOME/Downloads/Predictive-Mobility-Modeling-Handover-Decision-Making/Project_GCN_LSTM_HO/veins-veins-5.2
./bin/veins_launchd -vv -c /home/guest/Downloads/4F90/sumo-1.11.0/bin/sumo
exec bash
"

# --- Terminal 2: run opp_run simulations ---
OMNETPP_DIR="$HOME/Downloads/Predictive-Mobility-Modeling-Handover-Decision-Making/omnetpp-6.0"

gnome-terminal -- bash -c "

cd \"$OMNETPP_DIR\"
source setenv

cd \$HOME/Downloads/Predictive-Mobility-Modeling-Handover-Decision-Making/Project_GCN_LSTM_HO/simu5G/simulations/NR/ProactiveHO

# Only run for seed 500
for i in {0..4}; do
    echo \"  Run \$i / 5 for r=\$r\"
    start=\$(date +%s)
    opp_run -r \$i -m -u Cmdenv -c Vehicle-Uplink-Vehicle-Sender -n ../../../emulation:../..:../../../src:../../../../veins_inet/src/veins_inet:../../../../veins_inet/examples/veins_inet:../../../../inet4.4/examples:../../../../inet4.4/showcases:../../../../inet4.4/src:../../../../inet4.4/tests/validation:../../../../inet4.4/tests/networks:../../../../inet4.4/tutorials:../../../../veins-veins-5.2/examples/veins:../../../../veins-veins-5.2/src/veins --image-path=../../../images:../../../../veins_inet/images:../../../../inet4.4/images:../../../../veins-veins-5.2/images -l ../../../src/simu5g -l ../../../../veins_inet/src/veins_inet -l ../../../../inet4.4/src/INET -l ../../../../veins-veins-5.2/src/veins omnetpp.ini.500
    status=\$?
    finish=\$(date +%s)
    duration=\$((finish - start))
    if [ \$status -eq 0 ]; then
        echo \"  Run \$i completed in \${duration}s\"
    else
        echo \"  Run \$i failed after \${duration}s (exit \$status)\"
        break
    fi
done


# for r in {100..500..100}; do
#     echo \"Running simulations for seed \$r\"
#     for i in {0..4}; do
#         echo \"  Run \$i / 5 for r=\$r\"
#         start=\$(date +%s)
#         opp_run -r \$i -m -u Cmdenv -c Vehicle-Uplink-Vehicle-Sender -n ../../../emulation:../..:../../../src:../../../../veins_inet/src/veins_inet:../../../../veins_inet/examples/veins_inet:../../../../inet4.4/examples:../../../../inet4.4/showcases:../../../../inet4.4/src:../../../../inet4.4/tests/validation:../../../../inet4.4/tests/networks:../../../../inet4.4/tutorials:../../../../veins-veins-5.2/examples/veins:../../../../veins-veins-5.2/src/veins --image-path=../../../images:../../../../veins_inet/images:../../../../inet4.4/images:../../../../veins-veins-5.2/images -l ../../../src/simu5g -l ../../../../veins_inet/src/veins_inet -l ../../../../inet4.4/src/INET -l ../../../../veins-veins-5.2/src/veins omnetpp.ini.\$r
#         status=\$?
#         finish=\$(date +%s)
#         duration=\$((finish - start))
#         if [ \$status -eq 0 ]; then
#             echo \"  Run \$i completed in \${duration}s\"
#         else
#             echo \"  Run \$i failed after \${duration}s (exit \$status)\"
#             break
#         fi
#     done
# done

echo \"All simulations completed\"
exec bash
"
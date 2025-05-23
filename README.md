The given code can simulate both Free-running and DVFS-controlled CPU temperature.
For DVFS apart from dvfs_temp_limit, dvfs_hysteresis has been considered to avaoid chatter/oscillation.
Here hysteresis considered is 5C, it can be fine tune or considered as variable as well based on system requirement.
The code has simulated the given RC network, i feel the network can be further fine tuned by connecting the CPU node to package node, or even involving the TIM1 for lidded packages.

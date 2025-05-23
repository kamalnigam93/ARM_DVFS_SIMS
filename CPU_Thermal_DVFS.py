import numpy as np
import matplotlib.pyplot as plt

# Simulation Constants
dt = 0.01
duration = 10
time = np.arange(0, duration, dt)

# Thermal RC Parameters
R1, C_cpu   = 100.0,   0.01
R2, C_board = 300.0,   3.0
R3, C_amb   = 60.0,    10000.0
R4, C_pkg   = 30.0,    5.0
R5          = 30.0

T_ambient = 25.0

# Power and DVFS Constants
v_nom = 0.75
f_nom = 2.0
pleak_nom = 0.1
dvfs_temp_limit = 85.0
dvfs_hysteresis = 80.0

voltages = np.array([0.75, 0.70, 0.65, 0.60, 0.55])  # Discrete DVFS levels


# Synthetic Dynamic Power Trace
np.random.seed(0)
cdyn_trace = np.random.uniform(0.1, 1.0, len(time))  # W/GHz


# Free-Running Simulation (Fixed V/F)
def simulate_free_running():
    T_cpu = T_soc = T_board = T_pkg = T_ambient
    T_cpu_hist = []

    for i in range(len(time)):
        pdyn = cdyn_trace[i] * f_nom
        power_total = pdyn + pleak_nom

        q1 = (T_cpu - T_soc) / R1
        q2 = (T_soc - T_board) / R2
        q4 = (T_soc - T_pkg) / R4

        T_cpu += dt / C_cpu * (power_total - q1)
        T_soc += dt / C_board * (q1 - q2 - q4)
        T_pkg += dt / C_pkg * (q4 - (T_pkg - T_ambient) / R5)
        T_board += dt / C_amb * (q2 - (T_board - T_ambient) / R3)

        T_cpu_hist.append(T_cpu)

    return np.array(T_cpu_hist)


# DVFS-Controlled 
def simulate_dvfs_strict():
    T_cpu = T_soc = T_board = T_pkg = T_ambient
    T_cpu_hist, freq_hist, volt_hist = [], [], []

    voltage_index = 0  # Start at highest voltage (0.75 V)

    for i in range(len(time)):
        # DVFS logic with hysteresis
        if T_cpu > dvfs_temp_limit and voltage_index < len(voltages) - 1:
            voltage_index += 1  # Step down
        elif T_cpu < dvfs_hysteresis and voltage_index > 0:
            voltage_index -= 1  # Step up

        volt = voltages[voltage_index]
        freq = f_nom * (volt / v_nom)

        pdyn = cdyn_trace[i] * freq * (volt / v_nom)**2
        power_total = pdyn + pleak_nom

        q1 = (T_cpu - T_soc) / R1
        q2 = (T_soc - T_board) / R2
        q4 = (T_soc - T_pkg) / R4

        T_cpu += dt / C_cpu * (power_total - q1)
        T_soc += dt / C_board * (q1 - q2 - q4)
        T_pkg += dt / C_pkg * (q4 - (T_pkg - T_ambient) / R5)
        T_board += dt / C_amb * (q2 - (T_board - T_ambient) / R3)

        T_cpu_hist.append(T_cpu)
        freq_hist.append(freq)
        volt_hist.append(volt)

    return np.array(T_cpu_hist), np.array(freq_hist), np.array(volt_hist)


# Run Both Simulations
T_free = simulate_free_running()
T_dvfs, freq_dvfs, volt_dvfs = simulate_dvfs_strict()

# Plot 1: CPU Temperature Comparison
plt.figure(figsize=(12, 6))
plt.plot(time, T_free, label='Free-Running Mode', linewidth=1.5)
plt.plot(time, T_dvfs, label='DVFS-Controlled Mode', linewidth=1.5)
plt.axhline(dvfs_temp_limit, color='r', linestyle='--', label='DVFS Limit (85°C)')
plt.xlabel('Time (s)')
plt.ylabel('CPU Temperature (°C)')
plt.title('CPU Temperature Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Plot 2: DVFS Frequency and Voltage
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(time, freq_dvfs, label='Frequency (GHz)', color='blue')
plt.ylabel('Frequency (GHz)')
plt.title('DVFS Frequency Over Time')
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(time, volt_dvfs, label='Voltage (V)', color='orange')
plt.ylabel('Voltage (V)')
plt.xlabel('Time (s)')
plt.title('DVFS Voltage Over Time')
plt.grid(True)
plt.tight_layout()
plt.show()
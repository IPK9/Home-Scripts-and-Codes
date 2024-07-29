#
#       ServerStatus - V0.1
#
#   This section of the program is purely to pull data from the client
#   machines when requested by the server machine. This is just a small
#   snippet of code from what will be integrated into the main program
#   I believe this is the best way of testing as I don't need the server
#   running to get the metrics as they will be sent after being acquired.
#   
#       


# import libraries
import psutil
from psutil import *
import platform
import subprocess


# Get Hardware Statistic Values
cpu_per_core = psutil.cpu_percent(percpu=True) # CPU Usage per core
memory_info = psutil.virtual_memory() # Physical RAM details
used_memory_mb = memory_info.used / (1024 * 1024) # Used RAM converted to MB
free_memory_mb = memory_info.available / (1024 * 1024) # Free RAM converted

# Get CPU Temperature (Cross Platform)
def get_cpu_temperature():
    system = platform.system()
    if system == "Windows":
        return get_cpu_temperature_windows()
    elif system == "Linux":
        return get_cpu_temperature_linux()
    elif system == "Darwin":
        return get_cpu_temperature_mac()
    else:
        raise NotImplementedError(f"Unsupported platform: {system}")

def get_cpu_temperature_windows():
    try:
        import wmi
        w = wmi.WMI(namespace='root\\wmi')
        temperature_info = w.MSAcpi_ThermalZoneTemperature()[0]
        temperature_celsius = temperature_info.CurrentTemperature / 10.0 - 273.15
        return temperature_celsius
    except Exception as e:
        return f"Could not read temperature on Windows: {e}"
    
def get_cpu_temperature_linux():
    try:
        # using lm-sensors
        result = subprocess.run(['sensors'], stdout=subprocess.PIPE, text=True)
        for line in result.stdout.splitlines():
            if 'Core 0:' in line:
                return float(line.split()[2].replace('°C', ''))
    except Exception as e:
        return f"Could not read temperature on Linux: {e}"
    
def get_cpu_temperature_mac():
    try:
        #using osx-cpu-temp
        result = subprocess.run(['osx-cpu-temp'], stfout=subprocess.PIPE, text=True)
        return float(result.stdout.strip().replace('°C', ''))
    except Exception as e:
        return f"Could not read temperature on Mac: {e}"

cpu_temperature = get_cpu_temperature()
print(f"CPU Temperature: {cpu_temperature} °C")









# Print the statistic values
for i, percentage in enumerate(cpu_per_core):
    print(f"Core {i}: {percentage}%")
print(f"Used Physical Memory: {used_memory_mb:.2f} MB")
print(f"Free Physical Memory: {free_memory_mb:.2f} MB")





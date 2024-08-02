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
import time





# Get CPU Temperature (Cross Platform)
def get_cpu_temperature(): # attempts to retrieve cpu temperature
    system = platform.system()
    if system == "Windows":
        
        return get_cpu_temperature_windows()
    elif system == "Linux":
        return get_cpu_temperature_linux()
    elif system == "Darwin":
        return get_cpu_temperature_mac()
    else:
        raise NotImplementedError(f"Unsupported platform: {system}")

def get_cpu_temperature_windows(): # prerequisite for get_cpu_temperature
    try:
        import wmi
        w = wmi.WMI(namespace='root\\wmi')
        temperature_info = w.MSAcpi_ThermalZoneTemperature()[0]
        temperature_celsius = temperature_info.CurrentTemperature / 10.0 - 273.15
        return temperature_celsius
        
    except Exception as e:
        return f"Could not read temperature on Windows: {e}"
    
def get_cpu_temperature_linux(): # prerequisite for get_cpu_temperature
    try:
        # using lm-sensors
        result = subprocess.run(['sensors'], stdout=subprocess.PIPE, text=True)
        for line in result.stdout.splitlines():
            if 'Core 0:' in line:
                return float(line.split()[2].replace('°C', ''))
    except Exception as e:
        return f"Could not read temperature on Linux: {e}"
    
def get_cpu_temperature_mac(): # prerequisite for get_cpu_temperature
    try:
        #using osx-cpu-temp
        result = subprocess.run(['osx-cpu-temp'], stfout=subprocess.PIPE, text=True)
        return float(result.stdout.strip().replace('°C', ''))
    except Exception as e:
        return f"Could not read temperature on Mac: {e}"

def get_disk_usage(): # Disk usage in used/total/free format
    partitions = psutil.disk_partitions() # lists all of the partitions
    
    for partition in partitions:
        if partition.fstype: # Ensure the partition has a filesystem type
            try:
                disk_usage = psutil.disk_usage(partition.mountpoint) #
                
                total_gb = disk_usage.total / (1024 ** 3)
                used_gb = disk_usage.used / (1024 ** 3)
                free_gb = disk_usage.free / (1024 ** 3)
                
                print (f"Partition: {partition.device}")
                print (f"  Mountpoint: {partition.mountpoint}")
                print (f"  File system type: {partition.fstype}")
                print (f"  Total Disk Space: {total_gb:.2f} GB")
                print (f"  Used Disk Space: {used_gb:.2f} GB")
                print (f"  Free Disk Space: {free_gb:.2f} GB")
                print()
            except PermissionError: # Handle permission errors where the script doesn't have permissions
                print(f"Permission denied for partition: {partition.device}")
                print()
                
def get_disk_io_counters(interval=1): # prerequisite for monitor_disk_io
    # Get initial disk IO counters
    initial_counters = psutil.disk_io_counters()
    initial_read_bytes = initial_counters.read_bytes
    initial_write_bytes = initial_counters.write_bytes
    
    # Wait for the specified interval
    time.sleep(interval)
    
    # Get disk IO counters after the interval
    final_counters = psutil.disk_io_counters()
    final_read_bytes = final_counters.read_bytes
    final_write_bytes = final_counters.write_bytes
    
    # Calculate bytes read and written per second
    read_bytes_per_sec = (final_read_bytes - initial_read_bytes) / interval
    write_bytes_per_sec = (final_write_bytes - initial_write_bytes) / interval
    
    return read_bytes_per_sec, write_bytes_per_sec

def monitor_disk_io(interval=1, duration=10): # calculates disk usage in bytes/sec 
    start_time = time.time()
    read_bytes_per_sec, write_bytes_per_sec = get_disk_io_counters(interval)
    print(f"Read Bytes per Second: {read_bytes_per_sec:.2f} B/s")
    print(f"Write Bytes per Second: {write_bytes_per_sec:.2f} B/s")
    print()
                
def get_memory_usage(): # get ram usage in used/total/free format
    memory_info = psutil.virtual_memory() # Physical RAM details
    used_memory_mb = memory_info.used / (1024 * 1024) # Used RAM converted to MB
    free_memory_mb = memory_info.available / (1024 * 1024) # Free RAM converted
    total_memory_mb = memory_info.total / (1024 * 1024) 
    print(f"Used Physical Memory: {used_memory_mb:.2f} MB")
    print(f"Free Physical Memory: {free_memory_mb:.2f} MB")
    print (f"Total Physical Memory: {total_memory_mb: .2f} MB")

def get_cpu_usage(): # gets cpu usage per logical core.
    cpu_per_core = psutil.cpu_percent(percpu=True) # CPU Usage per core
    for i, percentage in enumerate(cpu_per_core):
        print(f"Core {i}: {percentage}%")
        
        
    
get_disk_usage()
get_memory_usage()
get_cpu_usage()
get_cpu_temperature()
print(get_cpu_temperature())
monitor_disk_io(interval=1)









#
#       ServerStatus - V1.0
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
import platform
import subprocess
import time
import win32evtlog
import datetime
import platform
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_cpu_temperature():
    """
    Retrieves CPU temperature across different operating systems.
    """
    system = platform.system()
    try:
        if system == "Windows":
            return get_cpu_temperature_windows()
        elif system == "Linux":
            return get_cpu_temperature_linux()
        elif system == "Darwin":
            return get_cpu_temperature_mac()
        else:
            raise NotImplementedError(f"Unsupported platform: {system}")
    except Exception as e:
        logging.error(f"Error getting CPU temperature: {e}", exc_info=True) # exc_info=True includes the traceback
        return None  # Or raise the exception if you want the program to halt


def get_cpu_temperature_windows():
    """Retrieves CPU temperature on Windows."""
    try:
        import wmi
        cpubins = wmi.WMI()
        for cpu in cpubins:
            # Example: Get % Processor Time
            cpu_usage = cpu.Win32_Processor()[2]  # Accessing the relevant data
            logging.info(f"CPU Temperature (Windows): {cpu_usage}")
            return cpu_usage
    except Exception as e:
        logging.error(f"Error getting CPU temperature (Windows): {e}", exc_info=True)
        return None


def get_cpu_temperature_linux():
    """Retrieves CPU temperature on Linux."""
    try:
        # Example using `sensors` command (requires `sensors` to be installed)
        import subprocess
        result = subprocess.run(['sensors'], capture_output=True, text=True, check=True)
        output = result.stdout
        # Parse the output (this part needs to be adapted based on the output format of 'sensors')
        for line in output.splitlines():
            if "temp" in line.lower():
                try:
                    temperature = float(line.split(":")[1].strip())
                    logging.info(f"CPU Temperature (Linux): {temperature}")
                    return temperature
                except ValueError:
                    logging.warning(f"Could not parse temperature from line: {line}")
                    pass
        logging.warning("No temperature found in 'sensors' output.")
        return None
    except FileNotFoundError:
        logging.error("The 'sensors' command-line tool is not installed.")
        return None
    except Exception as e:
        logging.error(f"Error getting CPU temperature (Linux): {e}", exc_info=True)
        return None


def get_cpu_temperature_mac():
    """Retrieves CPU temperature on macOS."""
    try:
        import subprocess
        result = subprocess.run(['powermetrics', '-c', 'cpu'], capture_output=True, text=True, check=True)
        output = result.stdout
        # Parse the output (this part needs to be adapted based on the output format of 'powermetrics')
        for line in output.splitlines():
            if "CPU Temperature" in line:
                try:
                    temperature = float(line.split(":")[1].strip())
                    logging.info(f"CPU Temperature (macOS): {temperature}")
                    return temperature
                except ValueError:
                    logging.warning(f"Could not parse temperature from line: {line}")
                    pass
        logging.warning("No temperature found in 'powermetrics' output.")
        return None
    except FileNotFoundError:
        logging.error("The 'powermetrics' command-line tool is not installed.")
        return None
    except Exception as e:
        logging.error(f"Error getting CPU temperature (macOS): {e}", exc_info=True)
        return None


def get_logical_drives():
    try:
        # Use WMIC to list logical drives
        command = "wmic logicaldisk get DeviceID"
        result = subprocess.check_output(command, shell=True, text=True).strip().split("\n")[1:]  # text=True handles decoding
        # Use a regular expression to extract the drive letters
        drives = [re.match(r"(\w:)", line).group(1) for line in result if line]
        return drives
    except subprocess.CalledProcessError as e:
        print(f"Failed to retrieve logical drives - {e}")
        return []

def get_disk_usage_via_wmic():
    drives = get_logical_drives()  # Get the list of logical drives

    for drive_letter in drives:
        try:
            # Execute the WMIC command to get the Size and FreeSpace of the given drive
            command = f"wmic logicaldisk where \"DeviceID='{drive_letter}'\" get Size,FreeSpace"
            result = subprocess.check_output(command, shell=True).decode().strip().split("\n")[1].split()
            
            # Extract the size and free space from the result
            total_bytes = int(result[0])
            free_bytes = int(result[1])
            used_bytes = free_bytes - total_bytes
            
            # Convert bytes to GB
            total_gb = total_bytes / (1024 ** 3)
            used_gb = used_bytes / (1024 ** 3)
            free_gb = free_bytes / (1024 ** 3)
            
            # Print the disk usage information
            print(f"Partition: {drive_letter}")
            print(f"  Total Disk Space: {total_gb:.2f} GB")
            print(f"  Used Disk Space: {used_gb:.2f} GB")
            print(f"  Free Disk Space: {free_gb:.2f} GB")
            print()
        except subprocess.CalledProcessError as e:
            print(f"Failed to retrieve disk usage for {drive_letter} - {e}")
            print()
        except Exception as e:
            print(f"An unexpected error occurred for partition: {drive_letter} - {e}")
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
        
def get_network_io_per_second(interval=1):
    

    #capture the network stats at the beginning
    network_io_start = psutil.net_io_counters(pernic=True)
    
    #wait for interval duration
    time.sleep(interval)
    
    #capture the network stats after the interval
    network_io_end = psutil.net_io_counters(pernic=True)
    
    # calculate the bytes sent and recieved per second for each adapter
    network_speed = {}
    for adapter in network_io_start.keys():
        sent_per_sec = (network_io_end[adapter].bytes_sent - network_io_start[adapter].bytes_sent) / interval
        recv_per_sec = (network_io_end[adapter].bytes_recv - network_io_start[adapter].bytes_recv / interval)
        network_speed[adapter] = {"sent_per_sec": sent_per_sec, "recv_per_sec": recv_per_sec}
        
    return network_speed

def get_process_count():
    process_count = len(psutil.pids()) # Get the list of all process IDs
    print (f"Total number of processes: {process_count}")

def get_top_processes_by_cpu(top_n=10):
    # Get all processes
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            proc.cpu_percent(interval=None)  # Initialize the CPU percent calculation
            processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Wait for a short period to allow CPU percent calculation
    time.sleep(1)
    
    # Now retrieve the actual CPU percent
    process_info = []
    for proc in processes:
        try:
            proc_info = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_info'])
            # Filter out the "System Idle Process" and normalize CPU usage
            if proc_info['name'] != "System Idle Process" and proc_info['cpu_percent'] <= 100:
                process_info.append(proc_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Sort the processes by CPU usage
    process_info = sorted(process_info, key=lambda proc: proc['cpu_percent'], reverse=True)
    
    # Display the top N processes
    print(f"Top {top_n} processes by CPU usage:")
    for proc in process_info[:top_n]:
        print(f"PID: {proc['pid']} | Name: {proc['name']} | CPU: {proc['cpu_percent']:.1f}% | Memory: {proc['memory_info'].rss / (1024 ** 2):.2f} MB")

def get_top_processes_by_mem(top_n=10):
    # Get all processes
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            proc.cpu_percent(interval=None)  # Initialize the CPU percent calculation
            processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Wait for a short period to allow CPU percent calculation
    time.sleep(1)
    
    # Now retrieve the actual CPU percent
    process_info = []
    for proc in processes:
        try:
            proc_info = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_info'])
            # Filter out the "System Idle Process" and normalize CPU usage
            if proc_info['name'] != "System Idle Process" and proc_info['cpu_percent'] <= 100:
                process_info.append(proc_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Sort the processes by CPU usage
    process_info = sorted(process_info, key=lambda proc: proc['memory_info'], reverse=True)
    
    # Display the top N processes
    print(f"Top {top_n} processes by memory usage:")
    for proc in process_info[:top_n]:
        print(f"PID: {proc['pid']} | Name: {proc['name']} | CPU: {proc['cpu_percent']:.1f}% | Memory: {proc['memory_info'].rss / (1024 ** 2):.2f} MB")

def get_event_viewer_stats(log_type='System', event_types=(win32evtlog.EVENTLOG_WARNING_TYPE, win32evtlog.EVENTLOG_ERROR_TYPE), time_period_minutes=60):
    server = 'localhost'  # The machine to monitor (use 'localhost' for local machine)
    log = log_type  # The event log type (e.g., 'System', 'Application', 'Security')
    flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    event_log_handle = win32evtlog.OpenEventLog(server, log)

    now = datetime.datetime.now()
    start_time = now - datetime.timedelta(minutes=time_period_minutes)
    
    total_errors = 0
    total_warnings = 0
    error_rate = 0
    warning_rate = 0

    events = []
    while True:
        records = win32evtlog.ReadEventLog(event_log_handle, flags, 0)
        if not records:
            break
        for event in records:
            event_time = event.TimeGenerated.Format()
            event_time = datetime.datetime.strptime(event_time, '%a %b %d %H:%M:%S %Y')

            if event_time >= start_time:
                if event.EventType == win32evtlog.EVENTLOG_ERROR_TYPE:
                    total_errors += 1
                elif event.EventType == win32evtlog.EVENTLOG_WARNING_TYPE:
                    total_warnings += 1

    win32evtlog.CloseEventLog(event_log_handle)

    elapsed_minutes = (now - start_time).total_seconds() / 60
    if elapsed_minutes > 0:
        error_rate = total_errors / elapsed_minutes
        warning_rate = total_warnings / elapsed_minutes

    return total_errors, total_warnings, error_rate, warning_rate

def display_event_viewer_stats():
    total_errors, total_warnings, error_rate, warning_rate = get_event_viewer_stats()

    print(f"Total Errors: {total_errors}")
    print(f"Total Warnings: {total_warnings}")
    print(f"Error Rate: {error_rate:.2f} per minute")
    print(f"Warning Rate: {warning_rate:.2f} per minute")

def get_system_boot_and_uptime():
    # Get the system boot time
    boot_time_timestamp = psutil.boot_time()
    boot_time = datetime.datetime.fromtimestamp(boot_time_timestamp)
    
    # Calculate the system uptime
    now = datetime.datetime.now()
    uptime = now - boot_time
    
    # Format the uptime for easier reading
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    print(f"System Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"System Uptime: {days} days, {hours} hours, {minutes} minutes, {seconds} seconds")

interval = 1
network_speeds = get_network_io_per_second(interval)
for adapter, speed in network_speeds.items():
    print(f"Adapter: {adapter}")
    print(f"Bytes sent per second: {speed['sent_per_sec']:.2f} B/s")
    print(f"Bytes received per second: {speed['recv_per_sec']:.2f} B/s\n")



get_disk_usage_via_wmic()

get_memory_usage()
get_cpu_usage()
get_cpu_temperature()
print(get_cpu_temperature())
monitor_disk_io(interval=1)
get_process_count()
get_top_processes_by_cpu(top_n=10)
get_top_processes_by_mem(top_n=10)
display_event_viewer_stats()
get_system_boot_and_uptime()






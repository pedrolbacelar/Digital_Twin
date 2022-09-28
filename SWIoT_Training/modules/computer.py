import psutil

computer_data = "Null"

def update_metrics():
    global computer_data
    global CPU_info
    global DISK_perc
    global MEM_perc
    
   
    #COPYRIGHT CARRIOTS JAVIER PASTOR 2017

    byte_to_GB = 1000000000

    # CPU informatiom
    CPU_info = psutil.cpu_percent(interval=1)

    # Memory information
    mem = psutil.virtual_memory()
    MEM_total = round(int(mem[0]) / byte_to_GB, ndigits = 2)
    MEM_perc = mem[2]
    MEM_available = round(int(mem[1]) / byte_to_GB, ndigits = 2)
    MEM_used = round(int(mem[3]) / byte_to_GB, ndigits = 2)
    MEM_free = round(int(mem[4]) / byte_to_GB, ndigits = 2)

    # Disk information
    disk = psutil.disk_usage('/')
    DISK_total = round(int(disk[0]) / byte_to_GB, ndigits = 2)
    DISK_used = round(int(disk[1]) / byte_to_GB, ndigits = 2)
    DISK_free = round(int(disk[2]) / byte_to_GB, ndigits = 2)
    DISK_perc = disk[3]

    computer_data = {
		"cpu": str(CPU_info),
		"memory": str(MEM_total),
		"memory_available": str(MEM_available),
		"memory_percentage": str(MEM_perc),
		"memory_used": str(MEM_used),
		"memory_free": str(MEM_free),	
		"disk": str(DISK_total),
		"disk_used": str(DISK_used),
		"disk_free": str(DISK_free),
		"disk_percentage": str(DISK_perc)
	}
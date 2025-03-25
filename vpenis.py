import subprocess
import platform
import psutil

def get_command_output(command):
    try:
        result = subprocess.check_output(command, shell=True, text=True)
        return result.strip().splitlines()
    except subprocess.CalledProcessError:
        return []

def main():
    MHz = 0.0
    disk_kB = 0
    mem_kB = 0
    uname_s = platform.system()

    if uname_s == "Windows":
        uptime_d = str(int(psutil.boot_time()))
    else:
        uptime_d = subprocess.check_output("uptime", shell=True, text=True).strip()
    if "up" in uptime_d and "days" in uptime_d:
        uptime_d = int(uptime_d.split("up ")[1].split(" days")[0])
    else:
        print("WARNING: Uptime format not recognised, or up for less than a day. Assuming 1 day.")
        uptime_d = 1

    if uname_s in ["NetBSD", "FreeBSD", "OpenBSD", "Darwin"]:
        for line in get_command_output("dmesg | grep '^cpu.* MHz,'"):
            MHz += float(line.split(" MHz")[0].split()[-1])

        cpufmax = float(get_command_output("sysctl -n hw.cpufrequency_max")[0])
        cpuf = float(get_command_output("sysctl -n hw.cpufrequency")[0])
        ncpu = int(get_command_output("sysctl -n hw.ncpu")[0])

        cpuf = max(cpuf, cpufmax)
        MHz = (ncpu * cpuf) / 1000000 if cpuf > 0 and MHz < 1 else MHz

        for line in get_command_output("sysctl -n hw.physmem"):
            mem_kB += float(line) / 1024

        for line in get_command_output("df -k -l"):
            if not line.startswith("Filesystem"):
                partition_size = int(line.split()[1])
                disk_kB += partition_size
                if "/dev/md" in line.split()[0]:
                    disk_kB += partition_size

    elif uname_s == "SunOS":
        for line in get_command_output("psrinfo -v | grep MHz | awk '{print $6}'"):
            MHz += float(line)

        for line in get_command_output("prtconf | grep '^Memory' | awk '{print $3}'"):
            mem_kB += 1024 * float(line)

        for line in get_command_output("df -k -l"):
            if not line.startswith("Filesystem"):
                partition_size = int(line.split()[1])
                disk_kB += partition_size
                if "/dev/md" in line.split()[0]:
                    disk_kB += partition_size

    elif uname_s == "Linux":
        for line in get_command_output("cat /proc/cpuinfo | grep '^cpu MHz' | awk '{print $4}'"):
            MHz += float(line)

        for line in get_command_output("free | grep '^Mem' | awk '{print $2}'"):
            mem_kB += float(line)

        for line in get_command_output("df -k -l"):
            if not line.startswith("Filesystem"):
                partition_size = int(line.split()[1])
                disk_kB += partition_size
                if "/dev/md" in line.split()[0] or "/dev/sd" in line.split()[0]:
                    disk_kB += partition_size
    
    elif uname_s == "Windows":
        # CPU
        for line in get_command_output("wmic cpu get CurrentClockSpeed"):
            if line.strip().isdigit():
                MHz += float(line.strip())
        # RAM
        for line in get_command_output("wmic OS get FreePhysicalMemory /Value"):
            if "FreePhysicalMemory" in line:
                mem_kB += float(line.split("=")[1].strip())
        
        # Disk
        for line in get_command_output("wmic logicaldisk get size,freespace,caption"):
            if line.strip() and not line.startswith("Caption"):
                parts = line.split()
                if len(parts) >= 2:
                    partition_size = int(parts[1]) // 1024  # Convert bytes to KB
                    disk_kB += partition_size
    else:
        print(f"SYSTEM NOT KNOWN: uname_s = '{uname_s}'")

    vpenis = 0.1 * (0.1 * uptime_d + MHz / 30.0 + mem_kB / 1024.0 / 3.0 + disk_kB / 1024.0 / 50.0 / 15.0 + 70.0)
    print(f"{vpenis:.1f}cm")

if __name__ == "__main__":
    main()
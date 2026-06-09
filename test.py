import platform
import subprocess
import socket
import uuid
import json
import psutil
from datetime import datetime


def run_powershell(command):
    """
    Runs a PowerShell command and returns the output.
    """
    try:
        completed = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                command
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if completed.returncode != 0:
            return f"Error: {completed.stderr.strip()}"

        output = completed.stdout.strip()
        return output if output else "No data returned"

    except Exception as e:
        return f"Error: {e}"


def run_powershell_json(command):
    """
    Runs a PowerShell command and tries to parse JSON output.
    """
    output = run_powershell(command)

    if output.startswith("Error:") or output == "No data returned":
        return None

    try:
        return json.loads(output)
    except Exception:
        return None


def bytes_to_gb(value):
    try:
        value = int(value)
        return round(value / 1024 / 1024 / 1024, 2)
    except Exception:
        return "Unknown"


def bytes_to_size(value):
    try:
        value = int(value)
    except Exception:
        return "Unknown"

    units = ["B", "KB", "MB", "GB", "TB", "PB"]

    for unit in units:
        if value < 1024:
            return f"{value:.2f} {unit}"
        value /= 1024

    return f"{value:.2f} EB"


def print_section(title):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def print_value(label, value):
    if value is None or value == "":
        value = "Unknown"
    print(f"{label}: {value}")


def ensure_list(data):
    if data is None:
        return []

    if isinstance(data, list):
        return data

    return [data]


def get_system_info():
    print_section("SYSTEM INFO")

    print_value("Computer Name", socket.gethostname())
    print_value("OS", f"{platform.system()} {platform.release()}")
    print_value("OS Version", platform.version())
    print_value("Architecture", platform.machine())
    print_value("Python Version", platform.python_version())

    data = run_powershell_json(
        "Get-CimInstance Win32_OperatingSystem | "
        "Select-Object Caption, Version, BuildNumber, OSArchitecture, InstallDate, LastBootUpTime | "
        "ConvertTo-Json"
    )

    if data:
        print_value("Windows Edition", data.get("Caption"))
        print_value("Windows Version", data.get("Version"))
        print_value("Build Number", data.get("BuildNumber"))
        print_value("OS Architecture", data.get("OSArchitecture"))
        print_value("Install Date", data.get("InstallDate"))
        print_value("Last Boot", data.get("LastBootUpTime"))


def get_cpu_info():
    print_section("CPU INFO")

    data = run_powershell_json(
        "Get-CimInstance Win32_Processor | "
        "Select-Object Name, Manufacturer, NumberOfCores, NumberOfLogicalProcessors, "
        "MaxClockSpeed, CurrentClockSpeed, L2CacheSize, L3CacheSize, SocketDesignation | "
        "ConvertTo-Json"
    )

    cpus = ensure_list(data)

    for index, cpu in enumerate(cpus, start=1):
        print(f"\nCPU #{index}")
        print_value("Name", cpu.get("Name"))
        print_value("Manufacturer", cpu.get("Manufacturer"))
        print_value("Socket", cpu.get("SocketDesignation"))
        print_value("Cores", cpu.get("NumberOfCores"))
        print_value("Threads", cpu.get("NumberOfLogicalProcessors"))
        print_value("Max Clock Speed", f"{cpu.get('MaxClockSpeed')} MHz")
        print_value("Current Clock Speed", f"{cpu.get('CurrentClockSpeed')} MHz")
        print_value("L2 Cache", f"{cpu.get('L2CacheSize')} KB")
        print_value("L3 Cache", f"{cpu.get('L3CacheSize')} KB")

    print_value("Current CPU Usage", f"{psutil.cpu_percent(interval=1)}%")


def get_gpu_info():
    print_section("GPU INFO")

    data = run_powershell_json(
        "Get-CimInstance Win32_VideoController | "
        "Select-Object Name, VideoProcessor, AdapterRAM, DriverVersion, DriverDate, "
        "VideoModeDescription, CurrentHorizontalResolution, CurrentVerticalResolution, CurrentRefreshRate | "
        "ConvertTo-Json"
    )

    gpus = ensure_list(data)

    if not gpus:
        print("No GPU data found.")
        return

    for index, gpu in enumerate(gpus, start=1):
        print(f"\nGPU #{index}")
        print_value("Name", gpu.get("Name"))
        print_value("Video Processor", gpu.get("VideoProcessor"))
        print_value("VRAM", f"{bytes_to_gb(gpu.get('AdapterRAM'))} GB")
        print_value("Driver Version", gpu.get("DriverVersion"))
        print_value("Driver Date", gpu.get("DriverDate"))
        print_value("Video Mode", gpu.get("VideoModeDescription"))
        print_value("Horizontal Resolution", gpu.get("CurrentHorizontalResolution"))
        print_value("Vertical Resolution", gpu.get("CurrentVerticalResolution"))
        print_value("Refresh Rate", f"{gpu.get('CurrentRefreshRate')} Hz")


def get_motherboard_info():
    print_section("MOTHERBOARD INFO")

    data = run_powershell_json(
        "Get-CimInstance Win32_BaseBoard | "
        "Select-Object Manufacturer, Product, Version, SerialNumber | "
        "ConvertTo-Json"
    )

    if not data:
        print("No motherboard data found.")
        return

    print_value("Manufacturer", data.get("Manufacturer"))
    print_value("Product", data.get("Product"))
    print_value("Version", data.get("Version"))
    print_value("Serial Number", data.get("SerialNumber"))


def get_bios_info():
    print_section("BIOS / UEFI INFO")

    data = run_powershell_json(
        "Get-CimInstance Win32_BIOS | "
        "Select-Object Manufacturer, Name, SMBIOSBIOSVersion, Version, ReleaseDate, SerialNumber | "
        "ConvertTo-Json"
    )

    if not data:
        print("No BIOS data found.")
        return

    print_value("Manufacturer", data.get("Manufacturer"))
    print_value("Name", data.get("Name"))
    print_value("SMBIOS BIOS Version", data.get("SMBIOSBIOSVersion"))
    print_value("BIOS Version", data.get("Version"))
    print_value("Release Date", data.get("ReleaseDate"))
    print_value("Serial Number", data.get("SerialNumber"))


def get_ram_info():
    print_section("RAM INFO")

    ram = psutil.virtual_memory()

    print_value("Total RAM", bytes_to_size(ram.total))
    print_value("Available RAM", bytes_to_size(ram.available))
    print_value("Used RAM", bytes_to_size(ram.used))
    print_value("RAM Usage", f"{ram.percent}%")

    data = run_powershell_json(
        "Get-CimInstance Win32_PhysicalMemory | "
        "Select-Object BankLabel, DeviceLocator, Manufacturer, PartNumber, SerialNumber, Capacity, Speed, ConfiguredClockSpeed | "
        "ConvertTo-Json"
    )

    sticks = ensure_list(data)

    if not sticks:
        print("\nNo RAM stick data found.")
        return

    for index, stick in enumerate(sticks, start=1):
        print(f"\nRAM Stick #{index}")
        print_value("Bank", stick.get("BankLabel"))
        print_value("Slot", stick.get("DeviceLocator"))
        print_value("Manufacturer", stick.get("Manufacturer"))
        print_value("Part Number", stick.get("PartNumber"))
        print_value("Serial Number", stick.get("SerialNumber"))
        print_value("Capacity", bytes_to_size(stick.get("Capacity")))
        print_value("Speed", f"{stick.get('Speed')} MHz")
        print_value("Configured Speed", f"{stick.get('ConfiguredClockSpeed')} MHz")


def get_storage_info():
    print_section("STORAGE INFO")

    data = run_powershell_json(
        "Get-CimInstance Win32_DiskDrive | "
        "Select-Object Model, Manufacturer, SerialNumber, InterfaceType, MediaType, Size, Partitions | "
        "ConvertTo-Json"
    )

    disks = ensure_list(data)

    if not disks:
        print("No physical disk data found.")
    else:
        for index, disk in enumerate(disks, start=1):
            print(f"\nPhysical Disk #{index}")
            print_value("Model", disk.get("Model"))
            print_value("Manufacturer", disk.get("Manufacturer"))
            print_value("Serial Number", disk.get("SerialNumber"))
            print_value("Interface", disk.get("InterfaceType"))
            print_value("Media Type", disk.get("MediaType"))
            print_value("Size", bytes_to_size(disk.get("Size")))
            print_value("Partitions", disk.get("Partitions"))

    print("\nLogical Drives")

    for partition in psutil.disk_partitions():
        print(f"\nDrive: {partition.device}")
        print_value("Mountpoint", partition.mountpoint)
        print_value("File System", partition.fstype)

        try:
            usage = psutil.disk_usage(partition.mountpoint)
            print_value("Total", bytes_to_size(usage.total))
            print_value("Used", bytes_to_size(usage.used))
            print_value("Free", bytes_to_size(usage.free))
            print_value("Usage", f"{usage.percent}%")
        except Exception:
            print("Could not read drive usage.")


def get_network_info():
    print_section("NETWORK INFO")

    print_value("Hostname", socket.gethostname())

    try:
        print_value("Local IP", socket.gethostbyname(socket.gethostname()))
    except Exception:
        print_value("Local IP", "Unknown")

    mac = ":".join(
        f"{(uuid.getnode() >> bits) & 0xff:02x}"
        for bits in range(40, -1, -8)
    )

    print_value("MAC Address", mac)

    interfaces = psutil.net_if_addrs()

    for name, addresses in interfaces.items():
        print(f"\nInterface: {name}")

        for address in addresses:
            print_value(str(address.family), address.address)


def get_battery_info():
    print_section("BATTERY INFO")

    battery = psutil.sensors_battery()

    if not battery:
        print("No battery detected.")
        return

    print_value("Battery Percentage", f"{battery.percent}%")
    print_value("Plugged In", battery.power_plugged)

    if battery.secsleft == psutil.POWER_TIME_UNLIMITED:
        print_value("Time Left", "Unlimited / plugged in")
    elif battery.secsleft == psutil.POWER_TIME_UNKNOWN:
        print_value("Time Left", "Unknown")
    else:
        minutes = battery.secsleft // 60
        hours = minutes // 60
        minutes = minutes % 60
        print_value("Time Left", f"{hours}h {minutes}m")


def get_display_info():
    print_section("DISPLAY / MONITOR INFO")

    data = run_powershell_json(
        "Get-CimInstance -Namespace root\\wmi -ClassName WmiMonitorID | "
        "ForEach-Object { "
        "$name = ($_.UserFriendlyName | Where-Object {$_ -ne 0} | ForEach-Object {[char]$_}) -join ''; "
        "$serial = ($_.SerialNumberID | Where-Object {$_ -ne 0} | ForEach-Object {[char]$_}) -join ''; "
        "[PSCustomObject]@{Name=$name; SerialNumber=$serial; ManufacturerName=($_.ManufacturerName -join '')} "
        "} | ConvertTo-Json"
    )

    monitors = ensure_list(data)

    if not monitors:
        print("No monitor data found.")
        return

    for index, monitor in enumerate(monitors, start=1):
        print(f"\nMonitor #{index}")
        print_value("Name", monitor.get("Name"))
        print_value("Serial Number", monitor.get("SerialNumber"))
        print_value("Manufacturer Code", monitor.get("ManufacturerName"))


def get_sound_devices():
    print_section("SOUND DEVICES")

    data = run_powershell_json(
        "Get-CimInstance Win32_SoundDevice | "
        "Select-Object Name, Manufacturer, Status | "
        "ConvertTo-Json"
    )

    devices = ensure_list(data)

    if not devices:
        print("No sound device data found.")
        return

    for index, device in enumerate(devices, start=1):
        print(f"\nSound Device #{index}")
        print_value("Name", device.get("Name"))
        print_value("Manufacturer", device.get("Manufacturer"))
        print_value("Status", device.get("Status"))


def get_temperatures_notice():
    print_section("TEMPERATURE INFO")

    print("Windows does not reliably expose CPU/GPU temperatures through built-in Python.")
    print("For temperatures, use HWiNFO, Open Hardware Monitor, or LibreHardwareMonitor.")


def save_report_to_file():
    answer = input("\nSave this report to a text file? y/n: ").strip().lower()

    if answer != "y":
        return

    filename = f"device_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

    print(f"\nTo save automatically, run this command instead:")
    print(f"python device_details_windows.py > {filename}")


def main():
    if platform.system() != "Windows":
        print("This script is designed for Windows only.")
        return

    print("WINDOWS DEVICE DETAILS SCANNER")
    print(f"Scan started: {datetime.now()}")

    get_system_info()
    get_cpu_info()
    get_gpu_info()
    get_motherboard_info()
    get_bios_info()
    get_ram_info()
    get_storage_info()
    get_network_info()
    get_battery_info()
    get_display_info()
    get_sound_devices()
    get_temperatures_notice()

    print()
    print("=" * 60)
    print("SCAN COMPLETE")
    print("=" * 60)

    save_report_to_file()


if __name__ == "__main__":
    main()
import subprocess
import sys
from os import walk

last_executed_command = None
last_executed_command_response = None
last_executed_command_errcode = None


def execute_blocking(command):
    global last_executed_command, last_executed_command_response, last_executed_command_errcode
    last_executed_command = command
    try:
        cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, err = cmd.communicate()
        out = out.decode("utf-8")
        last_executed_command_errcode = 0
        last_executed_command_response = out
    except subprocess.CalledProcessError as e:
        last_executed_command_errcode = e.returncode
        last_executed_command_response = e.output
    except:
        print("Unexpected error:", sys.exc_info()[0])
        last_executed_command_errcode = -1
        last_executed_command_response = sys.exc_info()[0]


def show_devices():
    cmd = subprocess.Popen('lsblk | grep sd | grep part', shell=True, stdout=subprocess.PIPE)
    out, err = cmd.communicate()
    devices = []
    for line in out.decode("utf-8").split("\n"):
        entries = line.split()
        # print(entries)
        if len(entries) > 3:
            dev = entries[0]
            dev = dev.encode("ascii", "ignore").decode()
            size = entries[3]
            if len(entries) == 7:
                mount_point = entries[6]
                device_data = {"name": dev, "size": size, "mount": mount_point}
            else:
                device_data = {"name": dev, "size": size}
            devices.append(device_data)
            # print("drive " + dev + " of size " + size + " mount point " + mount_point)
    return devices


def ls(folder):
    files = []
    folders = []
    for (dirpath, dirnames, filenames) in walk(folder):
        folders.extend(dirnames)
        files.extend(filenames)
        break
    files.sort()
    folders.sort()
    return folders, files


def mount(dev):
    mount_cmd = "mkdir -p /mount/DEV && mount /dev/DEV /mount/DEV"
    execute_blocking(mount_cmd.replace("DEV", dev))


def unmount(dev):
    mount_cmd = "umount /dev/DEV"
    execute_blocking(mount_cmd.replace("DEV", dev))


def copy_all(dev_from, dev_to):
    mount(dev_from)
    mount(dev_to)
    unmount(dev_from)
    unmount(dev_to)


if __name__ == '__main__':
    copy_all("sda1", "sdb2")
    show_devices()
    ls("/home/ct")

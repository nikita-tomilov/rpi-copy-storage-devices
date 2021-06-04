import subprocess
from os import walk

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
    # print("===\nFOLDERS")
    # for folder in folders:
    #     print(folder)
    # print("===\nFILES")
    # for file in files:
    #     print(file)
    return folders, files


def execute_blocking(command):
    print(command)


def copy_all(dev_from, dev_to):
    MOUNT_CMD = "mkdir -p /mount/DEV && mount /dev/DEV /mount/DEV"
    execute_blocking(MOUNT_CMD.replace("DEV", dev_from))
    execute_blocking(MOUNT_CMD.replace("DEV", dev_to))

    UMOUNT_CMD = "umount /dev/DEV"
    execute_blocking(UMOUNT_CMD.replace("DEV", dev_from))
    execute_blocking(UMOUNT_CMD.replace("DEV", dev_to))


if __name__ == '__main__':
    copy_all("sda1", "sdb2")
    show_devices()
    ls("/home/ct")

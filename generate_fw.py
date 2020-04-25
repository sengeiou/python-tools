# !/usr/bin/env python
# coding:utf-8

import os
from zlib import crc32
import re
import time
import datetime

CONFIG_FILE_PATH = 'config.dat'

class Firmware:
    def __init__(self, addr, size, crc32, ver, mcu):
        self.addr = addr
        self.size = size
        self.crc32 = crc32
        self.ver = ver
        self.mcu = mcu

    def print_fw_info(self):
        print("CPU type:%s" % self.mcu)
        print("FW ver:%s" % self.ver)
        print("FW size:%d" % self.size)
        print("FW addr:%d" % self.addr)
        print("FW crc32:%08X" % self.crc32)


def get_crc32(filename):  # 计算crc32
    with open(filename, 'rb') as f:
        return crc32(f.read())

def get_fw_info(file, ver, mcu, pre_file_addr, pre_file_len):
    size = os.path.getsize(file)
    addr = pre_file_len + pre_file_addr
    fver = ver
    fmcu = mcu
    crc32 = get_crc32(file)
    return Firmware(addr, size, crc32, fver, fmcu)

def find_info(file, key):
    with open(file, mode='r', encoding='utf-8') as f:
        for line in f.readlines():
            words = line.split()
            for i in words:
                n = re.findall(key, i)
                if n:
                    p1 = re.compile(r'["](.*?)["]', re.S)  # 最小匹配
                    res = re.findall(p1, line)
                    print(res)
                    return res[0]
    return 'null'
 
def convert_int_to_hex_string(num):
    a_bytes = bytearray()
    for i in range(0, 4):
        a_bytes.append((num >> ((3 - i) * 8)) & 0xff)
    aa = ''.join(['%02X' % b for b in a_bytes])
    return aa


if __name__ == "__main__":
    fw_ver = find_info(CONFIG_FILE_PATH, r"version")
    cpu_type = find_info(CONFIG_FILE_PATH, r"compatible")
    bin_file = find_info(CONFIG_FILE_PATH, r"filename")
    img_file = find_info(CONFIG_FILE_PATH, r"image")
    app_path = 'bin/' + bin_file
    fw_info = get_fw_info(app_path, fw_ver, cpu_type, 0x2000, 0)
    fw_info.print_fw_info()

    new_bin = bytearray()

    # CPU type (12 bytes)
    cpu_byte = bytes(cpu_type.encode("utf-8"))
    for i in range(0,12):
        if i < len(cpu_type):
            new_bin.append(cpu_byte[i])
        else:
            new_bin.append(0)

    # Firmware version (4 bytes)
    ver = bytes(fw_ver.encode('utf-8'))
    for i in range(0, 4):
        if i < len(fw_ver):
            new_bin.append(ver[i])
        else:
            new_bin.append(0)
     
    # Magic number (4 bytes)
    magic_number = 0xdeadbeef
    for i in range(0, 4):
        new_bin.append(((magic_number >> (i*8)) & 0xFF))
    
    # File offset (4 bytes)
    for i in range(0, 4):
        new_bin.append((fw_info.addr >> (i * 8)) & 0xFF)
        
    # File size (4 bytes)
    for i in range(0, 4):
        new_bin.append((fw_info.size >> (i * 8)) & 0xFF)    

    # File CRC (4 bytes)
    for i in range(0, 4):
        new_bin.append((fw_info.crc32 >> (i * 8)) & 0xFF)  
        
    # Build time (4 bytes)
    utc = int(time.time())
    for i in range(0, 4):
        new_bin.append((utc >> (i*8)) & 0xff)

    # Pad 0
    for i in range(len(new_bin), fw_info.addr):
        new_bin.append(0)
    

    with open(app_path, 'rb') as f:
        file_data = f.read()
        for tmp in file_data:
            new_bin.append(tmp)

    file_crc32 = crc32(new_bin)
    print("crc32: %08X" % file_crc32)
    localTime = time.localtime(time.time())
    strTime = time.strftime("%Y%m%d%H%M%S", localTime)
    print(strTime)

    with open(img_file, 'xb') as fw:
        fw.write(new_bin)

    print(img_file)
    print("file size: %d" % len(new_bin))

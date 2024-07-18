# EEPROM SPI
# Provides simple functions to interface an EEPROM to the Pi Pico
# Functions: read, write_byte, write_page, erase, ee2csv
#
# Copyright Per-Simon Saal 2024
# Released under the MIT License (MIT). See LICENSE.
#
# Tested with ST EEPROM M95256, M95640
#
# To adapt to your EEPROM:
# 1. Check pinning and baudrate
# 2. Check instruction bytes from datasheet
# 3. Check memory array (var num_pages, page_size)


from machine import SPI, Pin
import time

spi = machine.SPI(0, baudrate=5_000_000, sck=machine.Pin(2), miso=machine.Pin(4), mosi=machine.Pin(3))
cspin = machine.Pin(5, Pin.OUT, value=1)

spi.init
#instruction bytes from the datasheet
_READ = const(3)
_WRITE = const(2)
_WREN = const(6)  # Write enable
_RDSR = const(5)  # Read status register

# eeprom memory array M95256
num_pages = 256
page_size = 32

file_name = "dump.csv"

# read a given number of bytes from eeprom
# works
# add = 16bit, numbytes = int
def read(add, numbytes):
    global first_line
    buf = [_READ, add >> 8, add & 0xFF]
    rec = []
    cspin.value(0)
    spi.write(bytearray(buf[:4]))
    rec = spi.read(numbytes)
    cspin.value(1)
    print(rec) # enable to show data in REPL (bytes with ASCII representation will be shown as ASCII)
    ee2csv(rec, numbytes) # enable to store eeprom content to csv

# write single byte to eeprom
# works
# add = 16bit, numbytes = int
def write_byte(add, dat):
    # send write enable instruction
    buf = [_WREN]
    cspin.value(0)
    spi.write(bytearray(buf))
    cspin.value(1)
    
    # Write cmd, add byte 1 shift 8, add byte 2, data byte
    buf = [_WRITE, add >> 8, add & 0xFF, dat]
    cspin.value(0)
    spi.write(bytearray(buf[:4]))
    cspin.value(1)
    #print("Send {}".format(buf))
    time.sleep_ms(5)

# write page to eeprom (or as much databytes as provided)
# works
# add = start address, *dat = comma separated bytes (nice for REPL), (dat = list of data bytes (if you want to pass a list as argument to the function, remove *))
def write_page(add, *dat):   
    # send write enable instruction
    buf = [_WREN]
    cspin.value(0)
    spi.write(bytearray(buf))
    cspin.value(1)
    
    #convert tuple to list
    data = list(dat)
    #fill buffer with preamble
    buf = [_WRITE, add >> 8, add & 0xFF]
    #append data to preamble
    for x in range(len(data)):
        buf.append(data[x])
    #check if eeprom is ready to write
#     while rdsr() != True:
#         print("Device not ready")
#         time.sleep_ms(5)
    cspin.value(0)
    spi.write(bytearray(buf))
    cspin.value(1)
    time.sleep_ms(5)
    
# Read Status Register
def rdsr():
    buf = [_RDSR]
    rec = []
    cspin.value(0)
    spi.write(bytes(buf))
    rec = spi.read(2)
    cspin.value(1)
    print(rec)
    if rec == 0:
        return True
    else: #WIP bit is set (Write in progress)
        return False
    
# send tuple of data. Every byte is send separately with write()
# works but inefficient. Use write_page()
def send(sa, *data):
    for x in range(len(data)):
        print(sa+x,data[x])
        write(sa + x, data[x])
        
# fills the eeprom with provided value in all bytes (choose your erase value)
# works
def erase(value):
    dat = []
    # fill buffer
    for y in range(page_size):
        dat.append(value)
    for x in range(num_pages-1):
        # calculate start address of page
        add = 0 + x*page_size
        # send write enable instruction
        buf = [_WREN]
        cspin.value(0)
        spi.write(bytearray(buf))
        cspin.value(1)
        
        #fill buffer with preamble
        buf = [_WRITE, add >> 8, add & 0xFF]
        #append data to preamble
        for z in range(len(dat)):
            buf.append(dat[z])
        cspin.value(0)
        spi.write(bytearray(buf))
        cspin.value(1)
        time.sleep_ms(5)
    print("EEPROM filled with {}s".format(value))        
        
# Store EEPROM to CSV
# exports 1 page per row
# Can only save full pages (i.e. 64, 128, 256,...)
# data = list of data, numbytes = number of bytes to store
# works
def ee2csv(data, numbytes):
    # calculate needed number of pages
    cal_pages = int(numbytes / page_size)
    cnt = 0
    if numbytes % page_size != 0:
        cal_pages += 1
    print("Writing {} pages to csv".format(cal_pages))
    with open (file_name,"a") as logging:
        for i in range(cal_pages):
            logging.write("{} to {};".format(i*page_size,i*page_size+page_size-1)) 
            for j in range(page_size):
                logging.write("{};".format(data[cnt]))
                cnt+=1
            logging.write("\n")            
        logging.flush()
    logging.close()    


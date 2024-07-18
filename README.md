# micropython_eeprom_spi
Provides simple functions to interface an EEPROM to the Pi Pico  
Tested with ST M95256 and M95640

## To adapt to your EEPROM:
1. Check pinning and baudrate
2. Check instruction bytes from datasheet
3. Check memory array (var num_pages, page_size)

## Try in REPL:
### Read 10 bytes starting from address 0  
```python
>>>read(0,10)  
b'\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80
```
### Write 55 to address 128
```python
>>>write_byte(128,55)
```
### Write 10 bytes starting from address 1000
```python
>>>write_page(1000,10)
```
### Fill the memory with a specific character
```python
>>>erase(12)
```
### EEPROM 2 CSV
Enable the function `ee2csv(rec, numbytes)` in read() to store the read out data in a csv.  
The data is stored in one `page_size` per row.  
Number of bytes determines how many pages are read out.
### Limitations
Not tested with other EEPROM.  
Not to be used as filesystem.
    

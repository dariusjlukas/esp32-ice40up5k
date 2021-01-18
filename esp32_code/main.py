import time

def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('INSERT_NETWORK_HERE', 'INSERT_PASSWORD_HERE')
        fail_count = 0
        while (not wlan.isconnected()) and (fail_count < 100):
            fail_count = fail_count + 1
            time.sleep_ms(100)
            pass
        if(fail_count > 99):
            print('ERROR: Failed to connect to wifi, giving up after 100 tries.')
            return 0
    print('network config:', wlan.ifconfig())
    return 0

from machine import Pin
red = Pin(23, Pin.OUT)
blue = Pin(5, Pin.OUT)
green = Pin(0, Pin.OUT)
fpga_halt = Pin(18, Pin.OUT)

red.on()
blue.off()
green.off()

import machine
machine.freq(240000000)

# Program FPGA
import fpga
fpga.upload('blink.bin')

if(do_connect() == -1):
    red.on()
    blue.on()
else:
    red.off()
    blue.on()
fpga_halt.off()

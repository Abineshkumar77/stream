import sys
import serial
import calendar
import time
import signal
from threading import Timer
import os

cmd_query = b'\x7d\x81\xa1\x80\x80\x80\x80\x80\x80'  # Command to request live data

class RepeatedTimer:
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        if self._timer is not None:
            self._timer.cancel()
        self.is_running = False

def signal_handler(sig, frame):
    tf = calendar.timegm(time.gmtime())
    print(tf - ts, ' Seconds recorded!')
    rt.stop()
    with open(file, "a") as myfile:
        myfile.write(str(tf))
    sys.exit(0)

def maintain():
    try:
        serial.write(cmd_query)
    except Exception as e:
        print(f"Error maintaining connection: {e}")
        sys.exit(1)

def delaistart():
    print("Start recording in...")
    for i in range(5, 0, -1):
        print(i)
        time.sleep(1)

def read_data():
    while True:
        try:
            if serial.in_waiting > 0:
                data = serial.read(1024)  # Read larger chunks of data
                with open(file, "a") as myfile:
                    myfile.write(data.hex())
        except Exception as e:
            print(f"Error reading data: {e}")

signal.signal(signal.SIGINT, signal_handler)

if os.path.exists(sys.argv[2]):
    os.remove(sys.argv[2])

try:
    serial = serial.Serial(
        sys.argv[1],
        baudrate=115200,
        timeout=None,  # Use None for non-blocking read
        xonxoff=1,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
        parity=serial.PARITY_NONE
    )
except Exception as e:
    print(f"Error opening serial port: {e}")
    sys.exit(1)

delaistart()
maintain()
file = sys.argv[2]
rt = RepeatedTimer(60, maintain)
print("Recording...\n^C to stop.")

ts = calendar.timegm(time.gmtime())
with open(sys.argv[2], "a") as myfile:
    myfile.write(str(ts))

read_data()

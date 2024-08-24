import serial.tools.list_ports

def detect_cms50e_port():
    """
    Detect the serial port to which the CMS50E pulse oximeter is connected.
    """
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if "USB" in port.description or "CMS50" in port.description:
            return port.device  # Return the name of the port, e.g., 'COM3' or '/dev/ttyUSB0'
    
    return None  # Return None if no CMS50E device is detected

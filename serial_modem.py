import serial
import time

"""

ATI

"""
def registered(modem, output_ok='OK', cmd="+CREG?"):
    at_cmd = f'AT{cmd}\r'
    writed = modem.write(at_cmd.encode())
    response = []
    read_timeout = 0.1
    quantity = modem.in_waiting 
    while True:
        if quantity > 0:
            text = modem.read(quantity).decode().strip()
            text = text.replace('\r\n\r\n', ' ')
            text = text.replace('\r\n', ' ')
            text = text.replace('\n', '')
            text = text.replace('\r', '')
            response.append(text)
        else:
            time.sleep(read_timeout) 
        quantity = modem.in_waiting
        if quantity == 0:
            break
    text = ' '.join(response).upper().strip()
    if not text.endswith(output_ok):
        print('Failed')
    return text

modem = serial.Serial(port='/dev/serial0', baudrate=115200, timeout=5)
#response = registered(modem, "+SAPBR=0,1")
response = registered(modem, cmd="I")
print(f'ATI -> {response}')

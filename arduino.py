import serial
import time

arduino = serial.Serial('COM12', 9600, timeout=1)
time.sleep(2)

for letra in ['M', 'P', 'L', 'O']:
    arduino.write(letra.encode())
    print("Enviado:", letra)
    time.sleep(2)

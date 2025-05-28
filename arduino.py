import serial
import time
#verificar que los LEDs y la comunicación serial funcionen correctamente#
arduino = serial.Serial('COM12', 9600, timeout=1)
time.sleep(2)

for letra in ['M', 'P', 'L', 'O']:
    arduino.write(letra.encode())
    print("Enviado:", letra)
    time.sleep(2)

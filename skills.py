import os, webbrowser, sys, requests, subprocess, pyttsx3
import serial
import time
from camera import *
import json
import keyboard

#чтение настроек конфигурации
with open('config.json', 'r') as f:
    config = json.load(f)

# Настройки подключения
PORT = config["port_arduino"]  # Замените на свой COM-порт (например, '/dev/ttyUSB0' для Linux/Mac)
BAUD_RATE = 250000  # Скорость обмена данных (обычно 115200 для Marlin/Grbl)

ser = serial.Serial(PORT, BAUD_RATE, timeout=0.1)
#ser1 = serial.Serial(PORT, BAUD_RATE, timeout=0.1)

#Инициализация голосого движка при старте программы
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# выбираем голос
engine.setProperty('voice', voices[9].id)  # установка голоса по ID

def speaker(text):
    #Озвучка текста
    engine.say(text)
    engine.runAndWait()

def browser():
    webbrowser.open('https://www.youtube.com', new = 2)
    print('браузер запущен')

def telegram():
    subprocess.Popen("C:/Users/sasha/Telegram Desktop/Telegram.exe")
    print('telegram')

def offpc():
    #os.system('shutdown')
    print('пк выключен')

def weather():
    print('погода')

def offBot():
    sys.exit()

def passive():
    pass

#value = valueD

value = None



gcodeFANon = """
    M106
    """

gcodeFANoff = """
    M107
    """

gcodeBye = """
    M42 P44 S0
    G90
    G1 Y-7 F300
    G1 E-5 F400
    M280 P0 S90
    M280 P1 S90
    G4 P300
    M280 P0 S180
    M280 P0 S120
    M280 P0 S180
    M280 P0 S120
    M280 P0 S180
    M280 P0 S120
    M280 P0 S180
    G4 P200
    G1 Y0 E0 F300
    M280 P0 S90
    G4 S1
    M42 P44 S255
    """

gcodeHello = """
    M42 P44 S0
    G90
    G1 Y-8 F300
    M280 P0 S90
    M280 P1 S90
    G4 P300
    G1 Y-10 E-3 F200
    G4 P200
    M280 P0 S10
    G4 P500
    M280 P1 S70
    M280 P1 S110
    M280 P1 S70
    M280 P1 S110
    G4 P100
    G1 Y0 E0 F500
    M280 P0 S90
    M280 P1 S90
    """

gcodeClock = """
    G91
    G1 Z-4 F300
    """

gcodeCounterClock = """
    G91
    G1 Z4 F300
    """
gcodeCheck = """
    G90
    G1 Y-12 F400
    G4 P500
    G1 E-10 F400
    M280 P0 S90
    M280 P1 S90
    G4 P400
    G1 Z-4 F200
    G4 P800
    G1 Z0 F200
    G1 Z0 F200
    G4 P50
    M280 P1 S0
    G4 P600
    M280 P1 S180
    G4 P600
    M280 P1 S90
    G4 P600
    M280 P0 S0
    G4 P600
    M280 P0 S180
    G4 P600
    M280 P0 S90
    G4 P600
    T1
    G1 E-60 F5000
    G1 E0 F5000
    T0
    G4 S1
    T0
    G92 E-10
    G1 Y0 E0 F300
    """
gcodeMagnitOn = """
    M140 S0
    M104 S255
    """
gcodeMagnitOff = """
    M104 S0
    M140 S0
    """

gcodeLock2Fing = """
    T1
    G4 S1
    G91
    G1 E60 F3000
    G4 S5
    T0
    """
gcodeOpen2Fing = """
    T1
    G4 S1
    G91
    G1 E-60 F3000
    G4 S5
    T0
    """

gcodePowerOn = """
    M42 P44 S0
    """
gcodePowerOff = """
    M42 P44 S255
    """

def move(gcode):

    try:
        with open("number.txt", "r") as file:
            global value
            value = float(file.read())
        print(f"Значение number в other.py: {value}")
    except FileNotFoundError:
        print("Файл number.txt не найден.") 

    #print(f"Подключено к {PORT} ({BAUD_RATE} baud)")
           
    # Ждем, пока плата начнет отвечать
    time.sleep(0.5)
    #print("Инициализация...")

    if gcode == gcodeY:
        with open("number.txt", "r") as file:
            gcode = f"""
                G91
                G1 Y{int(file.read())} F200
            """
    if gcode == gcodeZ:
        with open("number.txt", "r") as file:
            gcode = f"""
                G91
                G1 Z{int(file.read())} F200
            """
    if gcode == gcodeE:
        with open("number.txt", "r") as file:
            gcode = f"""
                G91
                T0
                G1 E{int(file.read())} F200
            """
    if gcode == gcodeV:
        with open("number.txt", "r") as file:
            gcode = f"""
                G91
                M280 P1 S{int(file.read())}
            """
    if gcode == gcodeW:
        with open("number.txt", "r") as file:
            gcode = f"""
                G91
                M280 P0 S{int(file.read())}
            """
    try:        
            # Отправляем каждую строку G-кода
        for line in gcode.splitlines():
            line = line.strip()  # Удаляем лишние пробелы
            if line:  # Проверяем, что строка не пустая
                #print(f"Отправка: {line}")
                ser.write(f"{line}\n".encode('utf-8'))  # Отправляем команду
                time.sleep(0.5)  # Добавляем небольшую задержку
                    
                # Читаем ответ от платы
                #response = ser.readline().decode('utf-8').strip()
                #print(f"Ответ: {response}")
                    
    except serial.SerialException as e:
        print(f"Ошибка подключения: {e}")

def moveCam(gcode):

    try:        
            # Отправляем каждую строку G-кода
        for line in gcode.splitlines():
            line = line.strip()  # Удаляем лишние пробелы
            if line:  # Проверяем, что строка не пустая
                #print(f"Отправка: {line}")
                ser.write(f"{line}\n".encode('utf-8'))  # Отправляем команду
                #time.sleep(0.5)  # Добавляем небольшую задержку
                    
                # Читаем ответ от платы
                #response = ser.readline().decode('utf-8').strip()
                #print(f"Ответ: {response}")
                    
    except serial.SerialException as e:
        print(f"Ошибка подключения: {e}")

gcodeY = f"""
    G1 Y{value} F200
    """
gcodeZ = f"""
    G1 Z{value} F200
    """
gcodeE = f"""
    G1 E{value} F200
    """
gcodeV = f"""
    G1 P1 S{value}
    """
gcodeW = f"""
    G1 P0 S{value}
    """
powerOn = True
def manual_control(a):
    print("Ручное управление активировано. Используйте клавиши WASD для перемещения осей.")
    print("Обнулите координаты перед выходом, нажав '0'.")
    print("Включите питание перед выходом, нажав '9'.")
    print("Нажмите 'Q' для выхода из режима ручного управления.")

    import cv2
    import numpy as np

    # Инициализация камеры
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        #cv2.imshow(" ", frame)
        
        if keyboard.is_pressed('w'):  # Перемещение по оси X вперед
            #moveCam("G91")  # Относительное позиционирование
            y=-0.2
            #moveCam("G0 Y-0.2 F350")  # Перемещение на 10 мм по оси X
            #time.sleep(0.1)  # Задержка для предотвращения множественных нажатий
        elif keyboard.is_pressed('s'):  # Перемещение по оси X назад
            #moveCam("G91")
            y=0.2
            #moveCam("G0 Y0.2 F350")
            #time.sleep(0.1)
        else:
            y=0

        if keyboard.is_pressed('a'):  # Перемещение по оси Y влево
            #moveCam("G91")
            z=0.2
            #moveCam("G0 Z0.2 F250")
            #time.sleep(0.1)
        elif keyboard.is_pressed('d'):  # Перемещение по оси Y вправо
            #moveCam("G91")
            z=-0.2
            #moveCam("G0 Z-0.2 F250")
            #time.sleep(0.1)
        else:
            z=0

        if keyboard.is_pressed('x'):  # Перемещение по оси Y влево
            #moveCam("G91")
            e=0.2
            #moveCam("G0 E0.2 F350")
            #time.sleep(0.1)
        elif keyboard.is_pressed('c'):  # Перемещение по оси Y вправо
            #moveCam("G91")
            e=-0.2
            #moveCam("G0 E-0.2 F350")
            #time.sleep(0.1)
        else:
            e=0
        moveCam("G91")  # Относительное позиционирование
        moveCam(f"G0 Y{y} Z{z} E{e} F350")
        if keyboard.is_pressed('up'):  # Перемещение по оси Y влево
            moveCam("G91")
            moveCam("M280 P0 S30")
            #time.sleep(0.1)

        if keyboard.is_pressed('down'):  # Перемещение по оси Y вправо
            moveCam("G91")
            moveCam("M280 P0 S150")
            #time.sleep(0.1)

        if keyboard.is_pressed('right'):  # Перемещение по оси Y влево
            moveCam("G91")
            moveCam("M280 P1 S150")
            #time.sleep(0.1)

        if keyboard.is_pressed('left'):  # Перемещение по оси Y вправо
            moveCam("G91")
            moveCam("M280 P1 S30")
            #time.sleep(0.1)

        if keyboard.is_pressed('down + up'):  # Перемещение по оси Y вправо
            moveCam("G91")
            moveCam("M280 P0 S90")
            time.sleep(0.5)

        if keyboard.is_pressed('left + right'):  # Перемещение по оси Y влево
            moveCam("G91")
            moveCam("M280 P1 S90")
            time.sleep(0.5)
        
        if keyboard.is_pressed('alt'):
            gcode = """
            T1
            G4 P500
            G91
            G1 E-60 F3000
            G4 S1
            T0"
            """
            moveCam(gcode)
            time.sleep(0.5)

        if keyboard.is_pressed('ctrl'):
            gcode = """
            T1
            G4 P500
            G91
            G1 E60 F3000
            G4 S1
            T0"
            """
            moveCam(gcode)
            time.sleep(0.5)

        if keyboard.is_pressed('0'):
            moveCam("G91")
            moveCam("G92 Y0 Z0 E0")
            time.sleep(0.5)
            print('Координаты обнулены')

        if keyboard.is_pressed('9'):
            global powerOn
            if powerOn == False:
                moveCam("M42 P44 S0")
                print("Питание включено")
                powerOn = True
            else:
                powerOn = False
                moveCam("M42 P44 S255")
                print("Питание выключено")
            time.sleep(0.5)
        
        if keyboard.is_pressed('h'):
            print("Режим Привет")
            while True:
                move(gcodeHello)
                #time.sleep(0.5)
                if keyboard.is_pressed('q'):
                    print("Ручное управление")
                    time.sleep(1)
                    time.sleep(1)
                    break

        if keyboard.is_pressed('q'):  # Выход из режима ручного управления
            print("Выход из режима ручного управления.")
            cap.release()
            cv2.destroyAllWindows()
            time.sleep(1)
            print('готово')
            break

        time.sleep(0.01)  # Небольшая задержка для снижения нагрузки на CPU

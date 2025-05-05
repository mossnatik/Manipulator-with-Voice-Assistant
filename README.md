Manipulator by RAMPS1.4 with Voice Assistant (russian language)
Bauman Moscow State Technical University College of Space Instrumentation.
Pomozov Alrksandr, Sekachev Artem, Kaygorodtsev Gleb.
![image](https://github.com/user-attachments/assets/80c0b69d-8105-497b-8331-15ae5efffb6f)

More information *documantation* (on russian)
https://disk.yandex.ru/d/msD6nZgDhOpB-w

The manipulator is controlled by a RAMPS1.4 (3D printer board). Based on voice commands, a G-code is sent to the board via USB.
A 3D assembly of the robot arm can be found on GrabCAD: https://grabcad.com/library/manipulator-12

![image](https://github.com/user-attachments/assets/7be853da-c200-420a-b2b4-3142e79782d6)
Manipulator

![image](https://github.com/user-attachments/assets/44b73621-c790-4e25-8be1-19fcce53e6f4)
RAMPS1.4 with ArduinoMega

The main code is in the file deep.py
From the file words.py a dictionary is imported containing the names of the functions corresponding to the user's requests.
The words_data file.json contains a complete dictionary of already developed phrases and ready-made commands in the robot's arsenal.
The main functions that set the robot's mechanisms in motion are in skills.py.
Commands containing interaction with the camera are located in camera.py.
config.json contains the name of the port to which the RAMPS1.4 card is connected.


Voice assistant is AVAILABLE in RUSSIAN ONLY
READY-MADE VOICE COMMANDS:
each command must contain a TRIGGER WORD (ADDRESSING the robot)
***drive control***
move the X/Y/Z axis by *G-code units*
move the W/V axis by *degrees*
open/close the grip
turn on/off the magnet (with the magnet in the working position the organ)

***sequence of actions***
hello /hello
for now / I'm leaving
check the operation of all engines / take a test

***interaction with the camera***
follow the camera/follow the color (tracking of a red object is implemented)
pick up an object(orientation to a red object)

***Support teams***
turn on/turn off the manual control
turn on/turn on/turn off the fans/cooling/blowing
turn on/turn off the power

Similar formulations are perceived (yes/no/cancel voice confirmation is required). If the answer is "no", specify the function to perform the manipulator's actions.

![image](https://github.com/user-attachments/assets/27726fa1-4c1f-4374-b5d5-1cd04bc913eb)


****************************
****************************
***********перевод**********
Манипулятор управляется платой для 3д-принтера RAMPS1.4. Опираясь на голосовые команды на плату по USB отправляется G-код.
МТКП МГТУ им. Н.Э. Баумана
Помозов Александр, Секачёв Артём, Кайгородцев Глеб.

Полная документация
https://disk.yandex.ru/d/msD6nZgDhOpB-w

3д-сборку робота-манипулятора можно найти на GrabCAD: https://grabcad.com/library/manipulator-12

Основной код находится в файле deep.py
Из файла words.py импортируется словарь, содержащий названия функций, соответствующих запросам пользователя.
Файл words_data.json содержит полный словарь уже наработанных фраз и готовых команд в арсенале робота.
Основные функции, приводящие механизмы робота в движение, находятся в skills.py.
Команды, содержащие взаимодействие с камерой, находятся в camera.py
config.json содержит имя порта, к которому подключена плата RAMPS1.4

Голосовой ассистент ТОЛЬКО на РУССКОМ ЯЗЫКЕ
ГОТОВЫЕ ГОЛОСОВЫЕ КОМАНДЫ:
каждая команда должна содержать СЛОВО-ТРИГГЕР (ОБРАЩЕНИЕ к роботу)
***управление приводами***
перемести ось X/Y/Z на *единицы G-кода*
перемести ось W/V на *градусы*
открой/закрой захват
включи/отключи магнит (с магнитом в рабочем органе)

***последовательность действий***
привет/здорова
пока/я ухожу
проверь работу всех моторов/проведи тест

***взаимодействие с камерой***
следи по камере/следи за цветом(реализовано слежение за красным объектом)
возьми предмет(ориентация на красный объект)

***вспомогательные команды***
включи/запусти ручное управление
включи/запусти/выключи вентиляторы/охлаждение/обдув
включи/выключи питание

Воспринимаются схожие формулировки (требуется голосовое подтверждение да/нет/отмена). При ответе "нет" следует указать функцию для выполнения действий манипулятора.

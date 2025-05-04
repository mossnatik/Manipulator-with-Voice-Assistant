import pyttsx3

#Инициализация голосого движка при старте программы
engine = pyttsx3.init()
engine.setProperty('rate', 180)     #скорость речи

def speaker(text):
    #Озвучка текста
    engine.say(text)
    engine.runAndWait()



def map(x, a, b, c, d):
    """
    Преобразует число x из диапазона [a, b] в диапазон [c, d].
    """
    return c + (x - a) * (d - c) / (b - a)


def tracking_color(a):

    import cv2
    import numpy as np
    import os, webbrowser, sys, requests, subprocess, pyttsx3
    import serial
    import time
    import skills
    import deep
    import words

    window_width = 640
    window_height = 460

    tracking_cam = False
    Kp_z = 1.1
    Kd_z = 1000
    Kp_e = 1.1
    Kd_e = 1000
    Kp_y = 1.1
    Kd_y = 200
    error = 0
    cx_center = window_width/2
    cy_center = window_height/2
    old_error = error
    cx = cx_center
    cy = cy_center
    area = 0
    speedZ = 0.01
    numCam = 1
    # Инициализация камеры
    cap = cv2.VideoCapture(numCam)
    tracking_cam = True

    # Проверка, успешно ли открыта камера
    if not cap.isOpened():
        speaker('Камера не подключена')
        print("Ошибка: Не удалось открыть камеру.")
        cap.release()
        cv2.destroyAllWindows()
        return
    
    #cap = cv2.resizeWindow('Red Object Detection', window_width, window_height)


    gcode = """
        G90
        G1 Y-9 F300
        G4 P300
        G1 E-1 F300
        """
    skills.moveCam(gcode)
    gcode = """
        G91
        """
    skills.moveCam(gcode)

    while True:
        # Захват кадра
        ret, frame = cap.read()

        # Если кадр не удалось захватить, выходим из цикла
        if not ret:
            print("Ошибка: Не удалось захватить кадр.")
            break

        # Преобразование кадра в цветовое пространство HSV
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Определение диапазона красного цвета в HSV
        lower_red = np.array([0, 0, 0])
        upper_red = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv_frame, lower_red, upper_red)

        lower_red = np.array([138, 71, 113])
        upper_red = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv_frame, lower_red, upper_red)

        # Объединение масок
        #mask = cv2.bitwise_or(mask1, mask2)

        # Поиск контуров на маске
        contours, _ = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Если контуры найдены
        if contours:
            # Находим наибольший контур (предполагаем, что это наш объект)
            largest_contour = max(contours, key=cv2.contourArea)

            # Вычисляем моменты контура
            M = cv2.moments(largest_contour)

            # Если площадь контура больше нуля
            if M["m00"] > 800:
                # Вычисляем координаты центра объекта
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                # Вычисляем площадь объекта
                area = cv2.contourArea(largest_contour)

                # Рисуем контур объекта
                cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)

                # Рисуем центр объекта
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

                # Выводим координаты центра и площадь
                cv2.putText(frame, f"Center: ({cx}, {cy})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Area: {area}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            else:
                cx = 320
                cy = 230
                area = 0

        # Отображение кадра
        cv2.imshow('Red Object Detection', frame)

        if cx < 240:
            z=0.03
        elif cx > 400:
            z=-0.03
        else:
            z=0

        #print(cx)
        error = cx - cx_center
        #print(error)
        error_map = map(error, -320, 320, 0.1, -0.1)
        old_error = error_map
        errorPD_z = round((Kp_z*error_map + Kd_z*(old_error - error_map)), 4)
        #print(errorPD_z)

        
        #gcode = f"G1 Z{errorPD} F100"
        #print(gcode)
        #skills.moveCam(gcode)

        if cy < 160:
            e=-0.03
        elif cy > 280:
            e=0.03
        else:
            e=0

        error = cy - cy_center
        #print(error)
        error_map = map(error, -230, 230, -0.1, 0.1)
        old_error = error_map
        errorPD_e = round((Kp_e*error_map + Kd_e*(old_error - error_map)), 4)
        #print(errorPD_e)

        #skills.moveCam(gcode)

        if area > 20000:
            y=0.05
        if area < 10000:
            y=-0.03
        if area < 5000 or (area > 10000 and area < 20000):
            y=0

        if area > 5000 and area < 20000:
            error = area - 12500
            #print(error)
            error_map = map(error, 5000, 20000, -0.05, 0.05)
            old_error = error_map
            errorPD_y = round((Kp_y*error_map + Kd_y*(old_error - error_map)), 4)
            errorPD_z = 0
            #print(errorPD_y)
        elif area > 20000:
            errorPD_y = 0.05
            errorPD_z = 0
        elif area < 5000:
            errorPD_y = 0

        gcode = f"G1 Y{errorPD_y} Z{errorPD_z} E{errorPD_e} F100"
        print(gcode)
        skills.moveCam(gcode)

        # Выход из цикла по нажатию клавиши 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            tracking_cam = False
            break

        #response = deep.recognize_audio_input(deep.model, deep.samplerate)  # Распознаем голосовой ответ
        #if response in words.STOP:
        #    break
            

    # Освобождение ресурсов камеры и закрытие окон
    cap.release()
    cv2.destroyAllWindows()


def get_color(a):

    import cv2
    import numpy as np
    import os, webbrowser, sys, requests, subprocess, pyttsx3
    import serial
    import time
    import skills
    import deep
    import words

    window_width = 640
    window_height = 460

    tracking_cam = False
    Kp_z = 1.1
    Kd_z = 1000
    Kp_e = 1.1
    Kd_e = 1000
    Kp_y = 1.1
    Kd_y = 200
    error = 0
    cx_center = window_width/2
    cy_center = window_height/2
    old_error = error
    cx = cx_center
    cy = cy_center
    area = 0
    speedZ = 0.01
    numCam = 1
    # Инициализация камеры
    cap = cv2.VideoCapture(numCam)
    tracking_cam = True

    # Проверка, успешно ли открыта камера
    if not cap.isOpened():
        speaker('Камера не подключена')
        print("Ошибка: Не удалось открыть камеру.")
        cap.release()
        cv2.destroyAllWindows()
        return
    
    #cap = cv2.resizeWindow('Red Object Detection', window_width, window_height)


    gcode = """
        G90
        G1 Y-10 F300
        G4 P300
        G1 E-0.5 F300
        """
    skills.moveCam(gcode)
    gcode = """
        G91
        """
    skills.moveCam(gcode)

    while True:
        # Захват кадра
        ret, frame = cap.read()

        # Если кадр не удалось захватить, выходим из цикла
        if not ret:
            print("Ошибка: Не удалось захватить кадр.")
            break

        # Преобразование кадра в цветовое пространство HSV
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Определение диапазона красного цвета в HSV
        lower_red = np.array([0, 0, 0])
        upper_red = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv_frame, lower_red, upper_red)

        lower_red = np.array([138, 71, 113])
        upper_red = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv_frame, lower_red, upper_red)

        # Объединение масок
        #mask = cv2.bitwise_or(mask1, mask2)

        # Поиск контуров на маске
        contours, _ = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Если контуры найдены
        if contours:
            # Находим наибольший контур (предполагаем, что это наш объект)
            largest_contour = max(contours, key=cv2.contourArea)

            # Вычисляем моменты контура
            M = cv2.moments(largest_contour)

            # Если площадь контура больше нуля
            if M["m00"] > 800:
                # Вычисляем координаты центра объекта
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                # Вычисляем площадь объекта
                area = cv2.contourArea(largest_contour)

                # Рисуем контур объекта
                cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)

                # Рисуем центр объекта
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

                # Выводим координаты центра и площадь
                cv2.putText(frame, f"Center: ({cx}, {cy})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Area: {area}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            else:
                cx = 320
                cy = 230
                area = 0

        # Отображение кадра
        cv2.imshow('Red Object Detection', frame)

        if cx < 240:
            z=0.03
        elif cx > 400:
            z=-0.03
        else:
            z=0

        #print(cx)
        error = cx - cx_center
        #print(error)
        error_map = map(error, -320, 320, 0.1, -0.1)
        old_error = error_map
        errorPD_z = round((Kp_z*error_map + Kd_z*(old_error - error_map)), 4)
        #print(errorPD_z)

        
        #gcode = f"G1 Z{errorPD} F100"
        #print(gcode)
        #skills.moveCam(gcode)

        if cy < 160:
            e=-0.03
        elif cy > 280:
            e=0.03
        else:
            e=0

        error = cy - cy_center
        #print(error)
        error_map = map(error, -230, 230, -0.1, 0.1)
        old_error = error_map
        errorPD_e = round((Kp_e*error_map + Kd_e*(old_error - error_map)), 4)
        #print(errorPD_e)

        #skills.moveCam(gcode)

        if area > 20000:
            y=0.05
        if area < 10000:
            y=-0.03
        if area < 5000 or (area > 10000 and area < 20000):
            y=0

        if area > 5000 and area < 20000:
            error = area - 12500
            #print(error)
            error_map = map(error, 5000, 20000, -0.05, 0.05)
            old_error = error_map
            errorPD_y = round((Kp_y*error_map + Kd_y*(old_error - error_map)), 4)
            #print(errorPD_y)
        elif area > 20000:
            errorPD_y = 0.05
        elif area < 5000:
            errorPD_y = 0

        gcode = f"G1 Y{errorPD_y} Z{errorPD_z} E{errorPD_e} F100"
        print(gcode)
        skills.moveCam(gcode)

        # Выход из цикла по нажатию клавиши 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            tracking_cam = False
            break

        #response = deep.recognize_audio_input(deep.model, deep.samplerate)  # Распознаем голосовой ответ
        #if response in words.STOP:
        #    break
            

    # Освобождение ресурсов камеры и закрытие окон
    cap.release()
    cv2.destroyAllWindows()


def cameraOn(a):
    import cv2
    import numpy as np
    import os, webbrowser, sys, requests, subprocess, pyttsx3
    import serial
    import time
    import skills
    import deep
    import words

    # Инициализация камеры
    cap = cv2.VideoCapture(1)
    tracking_cam = True

    # Проверка, успешно ли открыта камера
    if not cap.isOpened():
        speaker('Камера не подключена')
        print("Ошибка: Не удалось открыть камеру.")
        cap.release()
        cv2.destroyAllWindows()
        return
    
    while True:
        # Захват кадра
        ret, frame = cap.read()

        # Если кадр не удалось захватить, выходим из цикла
        if not ret:
            print("Ошибка: Не удалось захватить кадр.")
            break

        # Преобразование кадра в цветовое пространство HSV
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Определение диапазона красного цвета в HSV
        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv_frame, lower_red, upper_red)

        lower_red = np.array([170, 120, 70])
        upper_red = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv_frame, lower_red, upper_red)

        # Объединение масок
        mask = cv2.bitwise_or(mask1, mask2)

        # Поиск контуров на маске
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)
        cv2.imshow("Red Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            tracking_cam = False
            break

        response = deep.recognize_audio_input(deep.model, deep.samplerate)  # Распознаем голосовой ответ
        if response in words.STOP:
            break
            

    # Освобождение ресурсов камеры и закрытие окон
    cap.release()
    cv2.destroyAllWindows()


def getting_color(a):

    import cv2
    import numpy as np
    import os, webbrowser, sys, requests, subprocess, pyttsx3
    import serial
    import time
    import skills
    import deep
    import words

    # Инициализация камеры
    cap = cv2.VideoCapture(1)
    tracking_cam = True

    # Проверка, успешно ли открыта камера
    if not cap.isOpened():
        speaker('Камера не подключена')
        print("Ошибка: Не удалось открыть камеру.")
        cap.release()
        cv2.destroyAllWindows()
        return

    cx = 320
    cy = 230
    area = 0

    gcode = """
        G91
        G1 Y-9 F300
        G4 P300
        G1 E-1 F300
        T1
        G1 E-60 F5000
        T0
        """
    skills.moveCam(gcode)
    gcode = """
        G91
        """
    skills.moveCam(gcode)

    while True:
        # Захват кадра
        ret, frame = cap.read()

        # Если кадр не удалось захватить, выходим из цикла
        if not ret:
            print("Ошибка: Не удалось захватить кадр.")
            break

        # Преобразование кадра в цветовое пространство HSV
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Определение диапазона красного цвета в HSV
        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv_frame, lower_red, upper_red)

        lower_red = np.array([170, 120, 70])
        upper_red = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv_frame, lower_red, upper_red)

        # Объединение масок
        mask = cv2.bitwise_or(mask1, mask2)

        # Поиск контуров на маске
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Если контуры найдены
        if contours:
            # Находим наибольший контур (предполагаем, что это наш объект)
            largest_contour = max(contours, key=cv2.contourArea)

            # Вычисляем моменты контура
            M = cv2.moments(largest_contour)

            # Если площадь контура больше нуля
            if M["m00"] > 800:
                # Вычисляем координаты центра объекта
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                # Вычисляем площадь объекта
                area = cv2.contourArea(largest_contour)

                # Рисуем контур объекта
                cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)

                # Рисуем центр объекта
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

                # Выводим координаты центра и площадь
                cv2.putText(frame, f"Center: ({cx}, {cy})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Area: {area}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            else:
                cx = 320
                cy = 230
                area = 0

        # Отображение кадра
        cv2.imshow('Red Object Detection', frame)

            
        # Ждем, пока плата начнет отвечать
        #time.sleep(0.5)
        #print("Инициализация...")

        if cx < 240:
            gcode = """
            G1 Z0.03 F100
            """
        elif cx > 400:
            gcode = """
            G1 Z-0.03 F100
            """
        else:
            gcode = """
            G1 Z0 F1000
            """

        skills.moveCam(gcode)

        if cy < 160:
            gcode = """
            G1 E-0.03 F200
            """
        elif cy > 280:
            gcode = """
            G1 E0.03 F200
            """
        else:
            gcode = """
            G1 E0 F1000
            """

        skills.moveCam(gcode)

        if area > 30000:
            gcode = """
            G1 Y0.05 F400
            """
        if area < 25000:
            gcode = """
            G1 Y-0.05 F400
            """
        if  area == 0:
            gcode = """
            G1 Y0 F1000
            """
        if (area > 25000 and area < 30000):
            gcode = """
            G1 Y0 F1000
            """
            skills.moveCam(gcode)
            time.sleep(2)
            gcode = """
            T1
            G1 E60 F5000
            T0
            """
            skills.moveCam(gcode)
            time.sleep(2)
            cap.release()
            cv2.destroyAllWindows()
            return
            


        skills.moveCam(gcode)

        # Выход из цикла по нажатию клавиши 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            tracking_cam = False
            break

        #response = deep.recognize_audio_input(deep.model, deep.samplerate)  # Распознаем голосовой ответ
        #if response in words.STOP:
        #    break
            

    # Освобождение ресурсов камеры и закрытие окон
    cap.release()
    cv2.destroyAllWindows()
import cv2
import numpy as np

def nothing(x):
    pass

# Создаем окно с ползунками для настройки диапазона
cv2.namedWindow('Trackbars')
cv2.createTrackbar('H_min', 'Trackbars', 0, 179, nothing)
cv2.createTrackbar('H_max', 'Trackbars', 179, 179, nothing)
cv2.createTrackbar('S_min', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('S_max', 'Trackbars', 255, 255, nothing)
cv2.createTrackbar('V_min', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('V_max', 'Trackbars', 255, 255, nothing)

# Для камеры (или замените на загрузку изображения)
cap = cv2.VideoCapture(0)

while True:
    # Чтение кадра
    ret, frame = cap.read()
    if not ret:
        break
    
    # Конвертация в HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Получение значений с ползунков
    h_min = cv2.getTrackbarPos('H_min', 'Trackbars')
    h_max = cv2.getTrackbarPos('H_max', 'Trackbars')
    s_min = cv2.getTrackbarPos('S_min', 'Trackbars')
    s_max = cv2.getTrackbarPos('S_max', 'Trackbars')
    v_min = cv2.getTrackbarPos('V_min', 'Trackbars')
    v_max = cv2.getTrackbarPos('V_max', 'Trackbars')
    
    # Создание масок
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(hsv, lower, upper)
    
    # Применение маски
    result = cv2.bitwise_and(frame, frame, mask=mask)
    
    # Отображение результатов
    cv2.imshow('Original', frame)
    cv2.imshow('Mask', mask)
    cv2.imshow('Result', result)
    
    # Выход по нажатию 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Освобождение ресурсов
cap.release()
cv2.destroyAllWindows()
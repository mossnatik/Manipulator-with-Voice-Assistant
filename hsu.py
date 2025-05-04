import cv2
import numpy as np

def preprocess_image(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 50])
    mask = cv2.inRange(hsv, lower_black, upper_black)
    
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=2)
    
    return mask

def find_largest_contour(mask, min_area=4500):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
    
    largest_contour = max(contours, key=cv2.contourArea)
    
    if cv2.contourArea(largest_contour) < min_area:
        return None
    
    return largest_contour

def recognize_letter(image, contour):
    x, y, w, h = cv2.boundingRect(contour)
    letter_roi = image[y:y+h, x:x+w]
    
    gray = cv2.cvtColor(letter_roi, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    
    # Проверка на H (есть ли перегородка по центру)
    center_x = w // 2
    center_region = thresh[:, center_x-5 : center_x+5]  # Полоса 10px по центру
    center_white = cv2.countNonZero(center_region)
    
    # Если в центре много белого — это H
    if center_white > 0.7 * (h * 10):  # Порог 70% заполнения
        return "H"
    
    # Проверка на U (нет перегородки снизу)
    bottom_region = thresh[2*h//3 : h, :]  # Нижняя треть
    bottom_white = cv2.countNonZero(bottom_region)
    
    # Если внизу мало белого — это U
    if bottom_white < 0.3 * (w * h//3):  # Порог 30% заполнения
        return "U"
    
    # Иначе — S
    return "S"

# Захват видеопотока
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    mask = preprocess_image(frame)
    contour = find_largest_contour(mask)
    
    if contour is not None:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        letter = recognize_letter(frame, contour)
        if letter:
            cv2.putText(frame, f"Letter: {letter}", (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    cv2.imshow("Letter Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
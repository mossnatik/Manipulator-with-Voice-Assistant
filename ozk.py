import numpy as np
from roboticstoolbox import DHRobot, RevoluteDH
import matplotlib.pyplot as plt  # Импортируем matplotlib
from math import cos, sin, radians
import time

# Определение DH-параметров
robot = DHRobot([
    RevoluteDH(a=0, alpha=np.pi/2, d=161),  # Звено 1
    RevoluteDH(a=220, alpha=0, d=0),          # Звено 2
    RevoluteDH(a=0, alpha=np.pi/2, d=0),          # Звено 3
    RevoluteDH(a=0, alpha=-np.pi/2, d=170),  # Звено 4
    RevoluteDH(a=78, alpha=0, d=0)         # Звено 5
], name="5-DOF Manipulator")

# Параметры схвата
grip_angle_deg = 0  # Угол наклона схвата
grip_angle_rad = radians(grip_angle_deg)
# Обратная задача кинематики
target = np.array([
    [1, 0, 0, 170],
    [0, 1, 0, 50],
    [0, 0, 1, 382],
    [0, 0, 0, 1]
    ])
#while True:
ik_solution = robot.ikine_LM(target)
print("Углы для достижения цели:", np.degrees(ik_solution.q))
#time.sleep(0.1)

robot.plot(ik_solution.q, block=True)

# Удерживаем окно открытым
plt.show()
import numpy as np
from roboticstoolbox import DHRobot, RevoluteDH
import matplotlib.pyplot as plt  # Импортируем matplotlib


# Определение DH-параметров
robot = DHRobot([
    RevoluteDH(a=0, alpha=np.pi/2, d=161),  # Звено 1
    RevoluteDH(a=220, alpha=0, d=0),          # Звено 2
    RevoluteDH(a=0, alpha=np.pi/2, d=0),          # Звено 3
    RevoluteDH(a=0, alpha=-np.pi/2, d=170),  # Звено 4
    RevoluteDH(a=78, alpha=0, d=0)         # Звено 5
], name="Manipulator")

# Вывод информации о роботе
print(robot)

# Углы поворота для каждого звена (в радианах)
angles = [(np.pi/180)*16.39, (np.pi/180)* 89.76 ,(np.pi/180)*(-2.24),(np.pi/180)* 0,(np.pi/180)* -2.48]

# Решение прямой задачи кинематики
T = robot.fkine(angles)

# Вывод результата
print("Матрица преобразования (положение и ориентация эндеффектора):\n", T)

# Визуализация робота
robot.plot(angles, block=True)

# Удерживаем окно открытым
plt.show()
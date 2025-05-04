#!/usr/bin/env python3
import queue
import sys
import sounddevice as sd
import vosk
import json
import words  # Импорт модуля words
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from skills import *
from vosk import Model, KaldiRecognizer
import logging
import json

#чтение настроек конфигурации
with open('config.json', 'r') as f:
    config = json.load(f)

# Настройка логирования
logging.basicConfig(filename='recognition_errors.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

q = queue.Queue()
model = vosk.Model('model_small')
device = sd.default.device
samplerate = int(sd.query_devices(device[0], 'input')['default_samplerate'])
index_n1 = None
index_n2 = None
index_n3 = None
word_number1 = None
word_number2 = None
word_number3 = None

def callback(indata, frames, time, status):
    q.put(bytes(indata))

def recognize_audio_input(model, samplerate):
    """
    Распознает голосовой ввод пользователя.
    Возвращает распознанный текст.
    """
    rec = KaldiRecognizer(model, samplerate)
    with sd.RawInputStream(samplerate=samplerate, blocksize=81600, device=device[0],
                           dtype="int16", channels=1, callback=callback):
        print("Говорите...")
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                print(result.get("text", "").strip().lower())
                return result.get("text", "").strip().lower()


word_number = None
def extract_number(text):
    """
    Преобразует числа, записанные словами, в числовое значение.
    Поддерживает числа от 0 до 999.
    """
    word_to_number = {
        "ноль": 0,
        "один": 1, "два": 2, "три": 3, "четыре": 4, "пять": 5,
        "шесть": 6, "семь": 7, "восемь": 8, "девять": 9,
        "десять": 10, "одиннадцать": 11, "двенадцать": 12,
        "тринадцать": 13, "четырнадцать": 14, "пятнадцать": 15,
        "шестнадцать": 16, "семнадцать": 17, "восемнадцать": 18,
        "девятнадцать": 19, "двадцать": 20, "тридцать": 30,
        "сорок": 40, "пятьдесят": 50, "шестьдесят": 60,
        "семьдесят": 70, "восемьдесят": 80, "девяносто": 90,
        "сто": 100, "двести": 200, "триста": 300, "четыреста": 400,
        "пятьсот": 500, "шестьсот": 600, "семьсот": 700,
        "восемьсот": 800, "девятьсот": 900,
    }
    global word_number1
    global word_number2
    global word_number3
    global index_n1
    global index_n2
    global index_n3
    index_n1 = None
    index_n2 = None
    index_n3 = None
    words = text.split()
    number = 0
    i = 0
    text = text.split()
    for word in words:
        if word in word_to_number:
            i = i + 1
            number += word_to_number[word]
            global index_n
            if i == 1:
                index_n1 = text.index(word) - 1
                print(f"Позиция числа: {index_n1}")
                word_number1 = word
            if i == 2:
                index_n2 = text.index(word) - 1
                print(f"Позиция числа: {index_n2}")
                word_number2 = word
            if i == 3:
                index_n3 = text.index(word) - 1
                print(f"Позиция числа: {index_n3}")
                word_number3 = word
            #print(words.replace(f"{word}", ""))
    if "минус" in words:
        number = number * (-1)
    #with open("number.txt", "w") as file:
    #    file.write(str(number))
    return number
number_check = None

def ask_for_confirmation(command):
    speaker(f"Вы имете ввиду: {command}?")
    global number_check
    if number_check:
        speaker(number)
    #speaker('Правильно ли я распознал команду?')
    rec = KaldiRecognizer(model, samplerate)
    data = q.get()                                  #забираются поступившие данные
    ans = True
    while True:
        response = recognize_audio_input(model, samplerate)  # Распознаем голосовой ответ
        if response in words.YES or response in words.NO or response in words.CANCEL:
            if response in words.YES:
                return True
            elif response in words.NO:
                return False
            elif response in words.CANCEL:
                return None
        else:
            print("Пожалуйста, скажите 'да' или 'нет'.")      #вывод промежуточного распознования
    #response = input("Правильно ли я распознал команду? (да/нет): ").strip().lower()
    return data == "да"

def update_words_file(new_data):
    """
    Обновляет файл words_data.json, добавляя новые данные в DATASET.
    """
    # Загружаем текущие данные из файла
    try:
        with open("words_data.json", "r", encoding="utf-8") as file:
            words_data = json.load(file)
    except FileNotFoundError:
        # Если файл не существует, создаем его с начальными данными
        words_data = {
            "TRIGGERS": [],
            "YES": [],
            "NO": [],
            "STOP": [],
            "CANCEL": [],
            "DATASET": {}
        }

    # Добавляем новые данные в DATASET
    words_data["DATASET"].update(new_data)

    # Сохраняем обновленные данные обратно в файл
    with open("words_data.json", "w", encoding="utf-8") as file:
        json.dump(words_data, file, ensure_ascii=False, indent=4)

    print("Файл words_data.json успешно обновлен.")

"""
def update_words_file(new_data):

    #Обновляет файл words.py, добавляя новые данные в DATASET.

    with open("words.py", "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Находим строку, где начинается DATASET
    start_index = None
    for i, line in enumerate(lines):
        if "DATASET = {" in line:
            start_index = i
            break

    if start_index is None:
        raise ValueError("Не удалось найти DATASET в файле words.py")

    # Добавляем новые данные в DATASET
    for phrase, action in new_data.items():
        lines.insert(start_index + 1, f"    '{phrase}': '{action}',\n")

    # Записываем обновленный файл
    with open("words.py", "w", encoding="utf-8") as file:
        file.writelines(lines)
        """

def recognize(data, vectorizer, clf, model, samplerate):
    trg = words.TRIGGERS.intersection(data.split())
    if not trg:
        return
    
    data.replace(list(trg)[0], '')
    trg = data.split()[0]
    data = data.replace(trg, '').strip()

    global number
    global number_check
    number = extract_number(data)
    value = number
    if number is not None and number != 0:
        number_check = True
        print(f"Найдено число: {number}")
        global index_n1
        global index_n2
        global index_n3
        index_n1 = index_n1+1
        with open("number.txt", "w") as file:
            file.write(str(value))
        if index_n1 != None or index_n2 != None or index_n3 != None:
            global word_number1
            print(word_number1)
            global word_number2
            print(word_number2)
            global word_number3
            print(word_number3)
            if word_number1 in data.split():
                data = data.replace(f'{word_number1}', '')
            if word_number2 in data.split():
                data = data.replace(f'{word_number2}', '')
            if word_number3 in data.split():
                data = data.replace(f'{word_number3}', '')
            if "минус" in data.split():
                data = data.replace("минус", '')
    else:
        number_check = False
    data = data.strip()
    print(f"Команда на распознование: {data}")
    # Проверка на точное совпадение
    with open("number.txt", "w") as file:
        file.write(str(value))
    if data.strip() in words.DATASET.keys():
        # Если найдено точное совпадение, выполняем команду без подтверждения
        answer = words.DATASET[data.replace(trg, '').strip()]
        func_name = answer.split()[0]
        arg = answer.split()[1]
        answer_text = answer.replace(func_name, '').replace(arg, '')
        speaker(answer_text)
        if number_check:
            speaker(number)
        exec(func_name + '(' + arg + ')')
        return

    # Если точного совпадения нет, используем классификатор
    text_vector = vectorizer.transform([data]).toarray()[0]
    answer = clf.predict([text_vector])[0]

    func_name = answer.split()[0]
    arg = answer.split()[1]
    answer_text = answer.replace(func_name, '').replace(arg, '')
    
    clarification = ask_for_confirmation(answer_text)
    # Запрос подтверждения голосом
    if clarification == True:
        new_data = {data: answer}  # Новая пара "фраза-действие"
        words.DATASET.update(new_data)  # Обновляем словарь в памяти
        update_words_file(new_data)
        with open("number.txt", "w") as file:
            file.write(str(value))
        speaker(answer_text)
        if number_check:
            speaker(number)
        exec(func_name + '(' + arg + ')')
    elif clarification == False:
        logging.info(f"Ошибка распознавания: {data} -> {answer}")
        correct_answer = input("Введите правильную команду: ")
        # Обновление модели и файла words.py
        new_data = {data: correct_answer}  # Новая пара "фраза-действие"
        words.DATASET.update(new_data)  # Обновляем словарь в памяти
        update_words_file(new_data)  # Обновляем файл words.py
        vectorizer = CountVectorizer()
        vectors = vectorizer.fit_transform(list(words.DATASET.keys()))
        clf.fit(vectors, list(words.DATASET.values()))
        print("Модель и файл words.py обновлены. Попробуйте снова.")
    elif clarification == None:
        return

def main():
    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform(list(words.DATASET.keys()))
    clf = LogisticRegression()
    clf.fit(vectors, list(words.DATASET.values()))

    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device[0],
                           dtype="int16", channels=1, callback=callback):
        rec = KaldiRecognizer(model, samplerate)
        print('Готово')
        speaker('готово')
        while True:
            current_keys = list(words.DATASET.keys())
            current_values = list(words.DATASET.values())
            
            #Переобучение только если словарь изменился
            if not hasattr(clf, 'vocabulary_') or current_keys != list(vectorizer.vocabulary_.keys()):
                vectors = vectorizer.fit_transform(current_keys)
                clf.fit(vectors, current_values)
            data = q.get()
            if rec.AcceptWaveform(data):
                data = json.loads(rec.Result())['text']
                recognize(data, vectorizer, clf, model, samplerate)
            else:
                #print(
                rec.PartialResult()
            if keyboard.is_pressed('3+0+1'):
                speaker('Активировано ручное управление')
                manual_control(None)
            if keyboard.is_pressed('q'):
                print('Завершение работы')
                speaker('Завершение работы')
                break
                


if __name__ == '__main__':
    print('Загрузка данных...')
    speaker('Загрузка данных...')
    main()
    input("Нажмите Enter для выхода...")
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

# Настройка логирования
logging.basicConfig(filename='recognition_errors.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

q = queue.Queue()
model = vosk.Model('model_small')
device = sd.default.device
samplerate = int(sd.query_devices(device[0], 'input')['default_samplerate'])

def callback(indata, frames, time, status):
    q.put(bytes(indata))

def recognize_audio_input(model, samplerate):
    """
    Распознает голосовой ввод пользователя.
    Возвращает распознанный текст.
    """
    rec = KaldiRecognizer(model, samplerate)
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device[0],
                           dtype="int16", channels=1, callback=callback):
        print("Говорите...")
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                return result.get("text", "").strip().lower()

def ask_for_confirmation(command, model, samplerate):
    """
    Запрашивает подтверждение у пользователя голосом.
    Возвращает True, если пользователь сказал "да", и False, если "нет".
    """
    print(f"Вы сказали: {command}")
    print("Правильно ли я распознал команду? Скажите 'да' или 'нет'.")
    
    while True:
        response = recognize_audio_input(model, samplerate)  # Распознаем голосовой ответ
        if response in {"да", "нет"}:
            return response == "да"
        else:
            print("Пожалуйста, скажите 'да' или 'нет'.")

def recognize(data, vectorizer, clf, model, samplerate):
    trg = words.TRIGGERS.intersection(data.split())
    if not trg:
        return
    
    data.replace(list(trg)[0], '')

    # Проверка на точное совпадение
    if data.strip() in words.DATASET:
        # Если найдено точное совпадение, выполняем команду без подтверждения
        answer = words.DATASET[data.strip()]
        func_name = answer.split()[0]
        arg = answer.split()[1]
        answer_text = answer.replace(func_name, '').replace(arg, '')
        speaker(answer_text)
        exec(func_name + '(' + arg + ')')
        return

    # Если точного совпадения нет, используем классификатор
    text_vector = vectorizer.transform([data]).toarray()[0]
    answer = clf.predict([text_vector])[0]

    func_name = answer.split()[0]
    arg = answer.split()[1]
    answer_text = answer.replace(func_name, '').replace(arg, '')
    
    # Запрос подтверждения голосом
    if ask_for_confirmation(answer_text, model, samplerate):
        speaker(answer_text)
        exec(func_name + '(' + arg + ')')
    else:
        logging.info(f"Ошибка распознавания: {data} -> {answer}")
        print("Пожалуйста, повторите команду.")

def main():
    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform(list(words.DATASET.keys()))
    clf = LogisticRegression()
    clf.fit(vectors, list(words.DATASET.values()))

    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device[0],
                           dtype="int16", channels=1, callback=callback):
        rec = KaldiRecognizer(model, samplerate)
        while True:
            vectorizer = CountVectorizer()
            vectors = vectorizer.fit_transform(list(words.DATASET.keys()))
            clf = LogisticRegression()
            clf.fit(vectors, list(words.DATASET.values()))
            data = q.get()
            if rec.AcceptWaveform(data):
                data = json.loads(rec.Result())['text']
                recognize(data, vectorizer, clf, model, samplerate)
            else:
                print(rec.PartialResult())

if __name__ == '__main__':
    main()
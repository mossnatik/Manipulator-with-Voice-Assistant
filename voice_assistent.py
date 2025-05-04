#!/usr/bin/env python3

import queue
import sys
import sounddevice as sd    #доступ к микрофону
import vosk                 #языковая модель
import json                 #для выборки текста по ключу
import words
from sklearn.feature_extraction.text import CountVectorizer     #машинное обучение
from sklearn.linear_model import LogisticRegression             #
from skills import *

from vosk import Model, KaldiRecognizer

q = queue.Queue()
model = vosk.Model('model_small')   #имя папки языковой модели

device = sd.default.device                                                          #кортеж input, output [1, 3] ///python -m sounddevice
samplerate = int(sd.query_devices(device[0], 'input')['default_samplerate'])        #48000

#функция записи
def callback(indata, frames, time, status):

    #добавляет полученную информацию
    q.put(bytes(indata))

def recognize(data, vectorizer, clf):
    trg = words.TRIGGERS.intersection(data.split())
    #если в произнесённом предложении нет триггеров, то конец функции   //.split разбивает строку на слова
    if not trg:
        return
    
    data.replace(list(trg)[0], '')                              #удаление обращения к боту из строки
    text_vector = vectorizer.transform([data]).toarray()[0]     #передача данных в вектор
    answer = clf.predict([text_vector])[0]                      #формирование ответа на вектор, на что фраза максимально похожа
    
    func_name = answer.split()[0]                               #имя функции [0] в значениях
    arg = answer.split()[1]                                     #аргумент функции [1]
    answer = answer.replace(func_name, '')                #заменить имя функции на пустоту
    speaker(answer.replace(arg, ''))
    exec(func_name + '('+ arg + ')')                      #exec выполняет строку как код с аргументом


def main():
    vectorizer = CountVectorizer()                                      #передача в fit_transforms ключи словаря
    vectors = vectorizer.fit_transform(list(words.DATASET.keys()))     #создание векторов - хэширование обращений, нахождение сходств и различей

    clf = LogisticRegression()                                          #всё выглядит как матрицы
    clf.fit(vectors, list(words.DATASET.values()))                     #передача векторов и взятие значений

    

    #сигнал с микрофона(частота дескредитации, количесвто информации на обработку в отношении к samolerate, устройство, .., .., функция записи)         python -m sounddevice
    with sd.RawInputStream(samplerate=samplerate, blocksize = 8000, device=device[0],
            dtype="int16", channels=1, callback=callback):

        #распознование(языковая модель, фрагменты распознования)
        rec = KaldiRecognizer(model, samplerate)
        while True:
            data = q.get()                                  #забираются поступившие данные
            if rec.AcceptWaveform(data):                    #если пауза в речи
                data = json.loads(rec.Result())['text']     #вывод результата по  ключу текст
                recognize(data, vectorizer, clf)
            else:
                print(rec.PartialResult())      #вывод промежуточного распознования
    
    #удаление словаря из оперативной памяти
    del words.DATASET


if __name__ == '__main__':
    main()
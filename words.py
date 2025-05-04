import json
import os

# Путь к файлу с данными
WORDS_DATA_FILE = "words_data.json"

# Загрузка данных из файла
def load_words_data():
    if os.path.exists(WORDS_DATA_FILE):
        with open(WORDS_DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {
        "TRIGGERS": set(),
        "YES": set(),
        "NO": set(),
        "STOP": set(),
        "CANCEL": set(),
        "DATASET": {}
    }
def save_words_data(data):
    with open(WORDS_DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Загрузка данных при импорте модуля
words_data = load_words_data()


TRIGGERS = set(words_data.get("TRIGGERS", []))

YES = set(words_data.get("YES", []))

NO = set(words_data.get("NO", []))

STOP = set(words_data.get("STOP", []))

CANCEL = set(words_data.get("CANCEL", []))

DATASET = words_data.get("DATASET", {})
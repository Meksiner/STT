# pip install vosk
import soundfile as sf
import numpy as np
from vosk import Model, KaldiRecognizer
import json

# Загружаем модель
model = Model(r"C:/Users/Koraku/STT/models/vosk-model-small-ru-0.22")

# Читаем WAV/OGG
data, samplerate = sf.read("e.wav", dtype="int16")

# Если стерео -> делаем моно
if len(data.shape) > 1:
    data = data.mean(axis=1).astype("int16")

rec = KaldiRecognizer(model, samplerate)

# Здесь будем копить весь текст
results = []

# Обрабатываем чанками по 0.5 сек
for i in range(0, len(data), 8000):
    chunk = data[i:i+8000]
    if rec.AcceptWaveform(chunk.tobytes()):
        res = json.loads(rec.Result())
        results.append(res.get("text", ""))

# Добавляем финальный результат
res = json.loads(rec.FinalResult())
results.append(res.get("text", ""))

# Склеиваем в единый текст
full_text = " ".join(results)

# Выводим
print(full_text)

# Можно сохранить в файл
with open("transcript.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

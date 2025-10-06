from vosk import Model
import os

model_path = r"models/vosk-model-small-ru-0.22"

print("Проверяю папку:", model_path)
print("Содержимое:", os.listdir(model_path))

try:
    model = Model(model_path)
    print("Модель загружена успешно ✅")
except Exception as e:
    print("Ошибка при загрузке модели ❌:", e)

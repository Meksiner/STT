# pip install vosk
import soundfile as sf
from vosk import Model, KaldiRecognizer

model = Model(r"C:/Users/Koraku/STT/models/vosk-model-small-ru-0.22")

# читаем ogg и преобразуем в PCM
data, samplerate = sf.read("ewa.wav", dtype="int16")

rec = KaldiRecognizer(model, samplerate)

# soundfile возвращает numpy-массив -> превращаем в bytes
import numpy as np
for i in range(0, len(data), 4000):
    chunk = data[i:i+4000]
    if rec.AcceptWaveform(chunk.tobytes()):
        print(rec.Result())
    else:
        print(rec.PartialResult())

print(rec.FinalResult())

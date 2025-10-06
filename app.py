from flask import Flask, render_template, request, jsonify
import sounddevice as sd
import queue, threading, json, os
from vosk import Model, KaldiRecognizer
import soundfile as sf

app = Flask(__name__)
q = queue.Queue()

# Подгружаем модель
MODEL_PATH = r"C:/Users/Koraku/STT/models/vosk-model-small-ru-0.22"
model = Model(MODEL_PATH)

stop_mic = False   # <-- флаг для остановки микрофона

# -------------------- РАСПОЗНАВАНИЕ ФАЙЛА --------------------
def transcribe_file(filepath):
    data, samplerate = sf.read(filepath, dtype="int16")
    rec = KaldiRecognizer(model, samplerate)
    result = []

    for chunk in range(0, len(data), 4000):
        if rec.AcceptWaveform(data[chunk:chunk+4000].tobytes()):
            res = json.loads(rec.Result())
            if res.get("text"):
                result.append(res["text"])

    res = json.loads(rec.FinalResult())
    if res.get("text"):
        result.append(res["text"])

    return " ".join(result)

@app.route("/upload", methods=["POST"])
def upload_audio():
    file = request.files["file"]
    filepath = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(filepath)

    text = transcribe_file(filepath)
    return jsonify({"text": text})


# -------------------- РАСПОЗНАВАНИЕ С МИКРОФОНА --------------------
def mic_worker(samplerate, device, callback):
    global stop_mic
    rec = KaldiRecognizer(model, samplerate)

    def sd_callback(indata, frames, time, status):
        if status:
            print("⚠", status)
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=samplerate, blocksize=8000,
                           device=device, dtype="int16", channels=1,
                           callback=sd_callback):
        while not stop_mic:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if result.get("text"):
                    callback(result["text"])

@app.route("/start_mic", methods=["POST"])
def start_mic():
    global stop_mic
    stop_mic = False
    samplerate = int(sd.query_devices(None, "input")["default_samplerate"])

    def send_update(text):
        with open("mic_result.txt", "a", encoding="utf-8") as f:
            f.write(text + "\n")

    threading.Thread(target=mic_worker, args=(samplerate, None, send_update), daemon=True).start()
    return jsonify({"status": "mic started"})

@app.route("/stop_mic", methods=["POST"])
def stop_mic_recording():
    global stop_mic
    stop_mic = True
    return jsonify({"status": "mic stopped"})

@app.route("/get_mic", methods=["GET"])
def get_mic():
    if os.path.exists("mic_result.txt"):
        with open("mic_result.txt", "r", encoding="utf-8") as f:
            return jsonify({"text": f.read()})
    return jsonify({"text": ""})


# -------------------- ФРОНТ --------------------
@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
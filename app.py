from flask import Flask, render_template, request, jsonify
import sounddevice as sd
import queue, threading, json, os
from vosk import Model, KaldiRecognizer
import soundfile as sf
from transformers import pipeline, AutoTokenizer

# -------------------- НАСТРОЙКА FLASK --------------------
app = Flask(__name__)
q = queue.Queue()

# -------------------- VOSK МОДЕЛЬ --------------------
MODEL_PATH = r"models/vosk-model-small-ru-0.22"
vosk_model = Model(MODEL_PATH)
stop_mic = False

# -------------------- RUPUNCT МОДЕЛЬ --------------------
PUNCT_MODEL_PATH = r"models/RUPunct_big"
tk = AutoTokenizer.from_pretrained(PUNCT_MODEL_PATH, strip_accents=False, add_prefix_space=True)
classifier = pipeline(
    "ner",
    model=PUNCT_MODEL_PATH,
    tokenizer=tk,
    aggregation_strategy="first",
    device=-1  # CPU
)

def process_token(token, label):
    mapping = {
        "LOWER_O": token,
        "LOWER_PERIOD": token + ".",
        "LOWER_COMMA": token + ",",
        "LOWER_QUESTION": token + "?",
        "LOWER_TIRE": token + "—",
        "LOWER_DVOETOCHIE": token + ":",
        "LOWER_VOSKL": token + "!",
        "LOWER_PERIODCOMMA": token + ";",
        "LOWER_DEFIS": token + "-",
        "LOWER_MNOGOTOCHIE": token + "...",
        "LOWER_QUESTIONVOSKL": token + "?!",
        "UPPER_O": token.capitalize(),
        "UPPER_PERIOD": token.capitalize() + ".",
        "UPPER_COMMA": token.capitalize() + ",",
        "UPPER_QUESTION": token.capitalize() + "?",
        "UPPER_TIRE": token.capitalize() + " —",
        "UPPER_DVOETOCHIE": token.capitalize() + ":",
        "UPPER_VOSKL": token.capitalize() + "!",
        "UPPER_PERIODCOMMA": token.capitalize() + ";",
        "UPPER_DEFIS": token.capitalize() + "-",
        "UPPER_MNOGOTOCHIE": token.capitalize() + "...",
        "UPPER_QUESTIONVOSKL": token.capitalize() + "?!",
        "UPPER_TOTAL_O": token.upper(),
        "UPPER_TOTAL_PERIOD": token.upper() + ".",
        "UPPER_TOTAL_COMMA": token.upper() + ",",
        "UPPER_TOTAL_QUESTION": token.upper() + "?",
        "UPPER_TOTAL_TIRE": token.upper() + " —",
        "UPPER_TOTAL_DVOETOCHIE": token.upper() + ":",
        "UPPER_TOTAL_VOSKL": token.upper() + "!",
        "UPPER_TOTAL_PERIODCOMMA": token.upper() + ";",
        "UPPER_TOTAL_DEFIS": token.upper() + "-",
        "UPPER_TOTAL_MNOGOTOCHIE": token.upper() + "...",
        "UPPER_TOTAL_QUESTIONVOSKL": token.upper() + "?!",
    }
    return mapping.get(label, token)

def split_text(text, chunk_size=200):
    """Разделяет длинный текст на части по chunk_size слов."""
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i + chunk_size])

def restore_punctuation(raw_text: str) -> str:
    """Применяет RUPunct для восстановления пунктуации"""
    output = ""
    for chunk in split_text(raw_text):
        preds = classifier(chunk)
        if not preds:
            continue
        for item in preds:
            output += " " + process_token(item["word"].strip(), item["entity_group"])
    return output.strip()

# -------------------- РАСПОЗНАВАНИЕ ФАЙЛА --------------------
def transcribe_file(filepath):
    data, samplerate = sf.read(filepath, dtype="int16")
    rec = KaldiRecognizer(vosk_model, samplerate)
    result = []

    for chunk in range(0, len(data), 16000):
        if rec.AcceptWaveform(data[chunk:chunk + 16000].tobytes()):
            res = json.loads(rec.Result())
            if res.get("text"):
                result.append(res["text"])

    res = json.loads(rec.FinalResult())
    if res.get("text"):
        result.append(res["text"])

    raw_text = " ".join(result)
    return restore_punctuation(raw_text) if raw_text else ""

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
    rec = KaldiRecognizer(vosk_model, samplerate)

    def sd_callback(indata, frames, time, status):
        if status:
            print("⚠", status)
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=samplerate, blocksize=16000,
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
        restored = restore_punctuation(text)
        with open("mic_result.txt", "a", encoding="utf-8") as f:
            f.write(restored + "\n")

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

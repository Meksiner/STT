from transformers import pipeline, AutoTokenizer

# путь к локальной модели
pt = r"models/RUPunct_big"

# загружаем токенизатор и модель
tk = AutoTokenizer.from_pretrained(pt, strip_accents=False, add_prefix_space=True)
classifier = pipeline(
    "ner",
    model=pt,
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


# --- Читаем входной файл ---
with open("transcript.txt", "r", encoding="utf-8") as f:
    input_text = f.read().strip()

print("✅ Текст загружен, длина:", len(input_text), "символов")

output = ""

# --- Обработка кусками ---
for i, chunk in enumerate(split_text(input_text)):
    print(f"\n🔹 Обработка блока {i+1}...")
    preds = classifier(chunk)
    if not preds:
        print("⚠️ Предсказаний нет для этого блока.")
        continue
    for item in preds:
        output += " " + process_token(item["word"].strip(), item["entity_group"])

# --- Вывод ---
if output.strip():
    print("\n✅ Результат:")
    print(output.strip()[:500] + "..." if len(output) > 500 else output.strip())

    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(output.strip())
    print("\n💾 Сохранено в output.txt")
else:
    print("⚠️ Модель не вернула текст. Проверь модель или путь к ней.")

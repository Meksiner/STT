const resultDiv = document.getElementById("result");
const liveDiv = document.getElementById("liveResult");

// === Загрузка файла ===
document.getElementById("uploadForm").addEventListener("submit", e => {
  e.preventDefault();
  const file = document.getElementById("fileInput").files[0];
  const formData = new FormData();
  formData.append("file", file);

  fetch("/upload", { method: "POST", body: formData })
    .then(res => res.json())
    .then(data => { resultDiv.textContent = data.text; });
});

// === Запись с микрофона ===
let mediaRecorder;
let audioChunks = [];

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");

startBtn.onclick = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  audioChunks = [];

  mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

  mediaRecorder.onstop = () => {
    const blob = new Blob(audioChunks, { type: "audio/wav" });
    const formData = new FormData();
    formData.append("audio", blob, "record.wav");

    fetch("/stream", { method: "POST", body: formData })
      .then(res => res.json())
      .then(data => { liveDiv.textContent = data.text; });
  };

  mediaRecorder.start();
  startBtn.disabled = true;
  stopBtn.disabled = false;
};

stopBtn.onclick = () => {
  mediaRecorder.stop();
  startBtn.disabled = false;
  stopBtn.disabled = true;
};

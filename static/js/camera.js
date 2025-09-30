// static/js/camera.js

let stream = null;
let video = document.getElementById('video');
let resultDiv = document.getElementById('result');
let loadingDiv = document.getElementById('loading');

// تشغيل الكاميرا
async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        document.getElementById('startBtn').style.display = 'none';
        document.getElementById('stopBtn').style.display = 'block';
    } catch (err) {
        alert("فشل في الوصول للكاميرا: " + err.message);
    }
}

// إيقاف الكاميرا
function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
    }
    document.getElementById('startBtn').style.display = 'block';
    document.getElementById('stopBtn').style.display = 'none';
}

// إرسال إطار للتحليل
async function sendFrame() {
    if (!stream) return;

    const canvas = document.createElement('canvas');
    canvas.width = 224;
    canvas.height = 224;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL('image/jpeg');

    loadingDiv.style.display = 'block';

    try {
        const response = await fetch('/api/ai-text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData })
        });

        const data = await response.json();
        if (data.text) {
            resultDiv.textContent = data.text;
        }
    } catch (err) {
        resultDiv.textContent = "خطأ في الاتصال بالذكاء الاصطناعي.";
    } finally {
        loadingDiv.style.display = 'none';
    }
}

// إرسال إطار كل ثانيتين
let intervalId;
document.getElementById('startBtn')?.addEventListener('click', () => {
    intervalId = setInterval(sendFrame, 2000);
});

document.getElementById('stopBtn')?.addEventListener('click', () => {
    if (intervalId) clearInterval(intervalId);
});
// static/js/install.js

// ❌ نزيل: let deferredPrompt;
// ✅ نستخدم window لتجنب التعارض
window.deferredPrompt = null;

// تسجيل Service Worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/pwa/service-worker.js')
            .then(reg => console.log('✅ SW مسجل:', reg.scope))
            .catch(err => console.log('❌ فشل تسجيل SW:', err));
    });
}

// التقاط حدث التثبيت
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    window.deferredPrompt = e;

    const installBtn = document.getElementById('installBtn');
    if (installBtn) {
        installBtn.classList.remove('d-none');
    }
});

// تفعيل التثبيت
document.getElementById('installBtn')?.addEventListener('click', () => {
    if (window.deferredPrompt) {
        window.deferredPrompt.prompt();

        window.deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('✅ تم قبول التثبيت');
            } else {
                console.log('❌ تم رفض التثبيت');
            }
            window.deferredPrompt = null;
            document.getElementById('installBtn')?.classList.add('d-none');
        });
    }
});
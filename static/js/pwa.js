if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker зарегистрирован: ', registration);
            })
            .catch(function(error) {
                console.log('Ошибка регистрации ServiceWorker: ', error);
            });
    });
}

// Функция для добавления на главный экран
let deferredPrompt;
const installButton = document.getElementById('install-button');

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;

    if (installButton) {
        installButton.style.display = 'block';
        installButton.addEventListener('click', installApp);
    }
});

async function installApp() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;

        if (outcome === 'accepted') {
            console.log('Приложение установлено');
            if (installButton) installButton.style.display = 'none';
        }

        deferredPrompt = null;
    }
}

// Оффлайн функциональность
window.addEventListener('online', function() {
    this.showNotification('Соединение восстановлено', 'success');
});

window.addEventListener('offline', function() {
    this.showNotification('Режим оффлайн', 'warning');
});
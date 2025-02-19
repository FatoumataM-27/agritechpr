// Service Worker Registration
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/js/sw.js')
        .then(function(registration) {
            console.log('Service Worker registered with scope:', registration.scope);
            initializePushNotifications(registration);
        })
        .catch(function(error) {
            console.error('Service Worker registration failed:', error);
        });
}

// Initialize Push Notifications
function initializePushNotifications(registration) {
    // Check if Push notification is supported
    if (!('PushManager' in window)) {
        console.log('Push notifications not supported');
        return;
    }

    // Request notification permission
    Notification.requestPermission()
        .then(function(permission) {
            if (permission === 'granted') {
                subscribeToPushNotifications(registration);
            }
        });
}

// Subscribe to Push Notifications
function subscribeToPushNotifications(registration) {
    const subscribeOptions = {
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
    };

    registration.pushManager.subscribe(subscribeOptions)
        .then(function(pushSubscription) {
            // Send the subscription to your server
            return fetch('/api/push-subscription', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(pushSubscription)
            });
        })
        .catch(function(error) {
            console.error('Error subscribing to push notifications:', error);
        });
}

// Convert VAPID key to correct format
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

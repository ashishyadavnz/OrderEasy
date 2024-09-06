importScripts("https://www.gstatic.com/firebasejs/9.17.1/firebase-app.js");
importScripts("https://www.gstatic.com/firebasejs/9.17.1/firebase-messaging.js");

firebase.initializeApp({
    apiKey: "AIzaSyBZgRCZexv8ErSYGyo6IpbO1Q438e-CFTA",
    authDomain: "timestint-st.firebaseapp.com",
    projectId: "timestint-st",
    storageBucket: "timestint-st.appspot.com",
    messagingSenderId: "507688135519",
    appId: "1:507688135519:web:1b3a39ef85863310fce4ea",
    measurementId: "G-6XJ70609DK"
});

const messaging = firebase.messaging();

messaging.setBackgroundMessageHandler(function(payload) {
    const notificationTitle = payload.notification.title;
    const notificationOptions = {
        body: payload.notification.body,
        icon: "/static/images/favicon.png",
    };

    return self.registration.showNotification(notificationTitle, notificationOptions);
});

self.addEventListener('notificationclick', event => {
    event.waitUntil(
        clients.openWindow('https://timestint.com/')
    );
    event.notification.close();
});

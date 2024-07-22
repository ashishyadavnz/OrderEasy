importScripts("https://www.gstatic.com/firebasejs/7.16.1/firebase-app.js");
importScripts(
    "https://www.gstatic.com/firebasejs/7.16.1/firebase-messaging.js",
);
// For an optimal experience using Cloud Messaging, also add the Firebase SDK for Analytics.
importScripts(
    "https://www.gstatic.com/firebasejs/7.16.1/firebase-analytics.js",
);

// Initialize the Firebase app in the service worker by passing in the
// messagingSenderId.
firebase.initializeApp({
    apiKey: "AIzaSyBZgRCZexv8ErSYGyo6IpbO1Q438e-CFTA",
    authDomain: "timestint-st.firebaseapp.com",
    projectId: "timestint-st",
    storageBucket: "timestint-st.appspot.com",
    messagingSenderId: "507688135519",
    appId: "1:507688135519:web:1b3a39ef85863310fce4ea",
    measurementId: "G-6XJ70609DK"
});

// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging();

messaging.setBackgroundMessageHandler(function(payload) {
    console.log(
        "[firebase-messaging-sw.js] Received background message ",
        payload,
    );
    // Customize notification here
    const notificationTitle = "Background Message Title";
    const notificationOptions = {
        body: "Background Message body.",
        icon: "/static/images/favicon.png",
        // data: {
        //     url: payload.body
        // }
    };

    return self.registration.showNotification(
        notificationTitle,
        notificationOptions,
    );
});

self.addEventListener('notificationclick', event => {

    event.waitUntil(
        self.clients.openWindow('https://timestint.com/')
    )
    event.notification.close()
})
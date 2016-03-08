console.log('Started', self);
self.addEventListener('install', function(event) {
  self.skipWaiting();
  console.log('Installed', event);
});
self.addEventListener('activate', function(event) {
  console.log('Activated', event);
});
self.addEventListener('push', function(event) {
  console.log('Push message', event);
  event.waitUntil(
    fetch("//pollfriend.org/get_sos_notification/").then(function(response){
        if(response.status!=200){
            console.log('Looks like there was a problem. Status Code: ' + response.status);
            throw new Error();
        }
        return response.json().then(function(data){
            if(data.error || !data.notification){
                console.error('The API returned an error.', data.error);
                throw new Error();
            }
            var title = data.notification.title;
            var message = data.notification.message;
            var icon = '//pollfriend.org/static/main/images/push-notification.png';
            var notificationTag = data.notification.tag;
            return self.registration.showNotification(title, {
              body: message,
              icon: icon,
              tag: notificationTag
            });
        });
    }).catch(function(err){
       console.log('Unable to retrieve data', err);
       var title = 'SOS - Update';
       var message = 'We were unable to get the information, please click here to know the real message.';
       var icon = '//pollfriend.org/static/main/images/push-notification.png';
       var notificationTag = 'notification-error';
       return self.registration.showNotification(title, {
           body: message,
           icon: icon,
           tag: notificationTag
       });
    })
  );
});
self.addEventListener('notificationclick', function(event) {
    console.log('Notification click: tag ', event.notification.tag);
    event.notification.close();
    var url = '//pollfriend.org/messages/inbox/';
    event.waitUntil(
        clients.matchAll({
            type: 'window'
        })
        .then(function(windowClients) {
            for (var i = 0; i < windowClients.length; i++) {
                var client = windowClients[i];
                if (client.url === url && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(url);
            }
        })
    );
});

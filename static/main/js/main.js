if ('serviceWorker' in navigator) {
	 console.log('Service Worker is supported');
	 navigator.serviceWorker.register('//localhost/static/main/js/sw.js').then(function(reg) {
	   console.log(':^) Registered Successfully!', reg);
	   reg.pushManager.subscribe({
		    userVisibleOnly: true
		}).then(function(sub) {
		    console.log('endpoint:', sub.endpoint);
		    var s = sub.endpoint.split('/');
		    console.log('Device Key: ', s[5]);
			$.ajax({
				url: '/register_web_device/',
				type: 'post',
				dataType: 'json',
				success: function (data) {
					console.log(data);
				},
				data: {device_key: s[5]}
			});
		});
	 }).catch(function(err) {
	   console.log(':^(', err);
	 });
}else{
	console.log(':^( Browser not supported!', err);
	alert("Browser not supported, please use updated Chrome!");
}
function getScoreboard(hostname, callback) {
	$.getJSON('http://' + hostname + '/json/scoreboard' + cn, function(data) {
		callback(data);
	});
}

function getClientState(hostname, cn, callback) {
	$.getJSON('http://' + hostname + '/json/clients/' + cn, function(data) {
		callback(data);
		});
}

function getClients(hostname, callback) {
	$.getJSON('http://' + hostname + '/json/clients', function(data) {
		callback(data);
		});
}

function foreachClient(hostname, callback) {
	getClients(hostname, function(clients) {
		$.each(clients, function(i, client) {
			callback(client)
			});
		});
}

function loadPlayerAdminPage(username, password) {
}

function tryLogin(hostname, username, password, error_callback, success_callback) {
	$.getJSON('http://' + hostname + '/json/login?username=' + username + '&password=' + password, function(data) {
		if(data.hasOwnProperty('result') && data.result == 'SUCCESS')
			success_callback();
		else
			error_callback();
		});
}

function loadLoginPage(hostname, callback) {
	html_page = '<div class=\"alert_box\" id=\"login_container\"><h3>Please login</h3>Username: <input type=\"text\" id=\"username_input\" /><br />Password: <input type=\"password\" id=\"password_input\" /><br /><input type=\"submit\" value=\"Login\" id=\"login_submit\" /><br /><span id=\"login_status\"></span></div>';
	$('#content').empty();
	$(html_page).fadeIn('slow').appendTo('#content');
	$('#login_submit').click(function() {
		$('#login_status').empty();
		$('#login_status').html('Trying login...');
		var username = $('#username_input').val();
		var password = $('#password_input').val();
		tryLogin(hostname, username, password, function() {
				$('#login_status').empty();
				$('#login_status').html('Invalid login.');
				},
			function() {
				$('#login_status').empty();
				$('#login_status').html('Success.');
				});
		});
}


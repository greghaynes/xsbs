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

function loadPlayerAdmin(username, password) {
}

function doLogin(callback) {
	form_html = '<div id=\"login_container\"><h3>Please login</h3><form id=\"login_form\">Username: <input type=\"text\" id=\"username_input\" /><br />Password: <input type=\"password\" id=\"password_input\" /><br /><input type=\"submit\" value=\"Login\" /></form></div>';
	$(form_html).appendTo('#content');
	$('#login_form').submit(function() {
		callback($('#username_input').val(),
			$('#password_input').val());
		});
}


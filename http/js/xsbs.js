function getScoreboard(hostname, callback) {
	$.getJSON('http://' + hostname + '/json/scoreboard', function(data) {
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

function displayAlert(text) {
	$('#content').fadeTo('slow', 0.4).attr('disabled', '');
	$('<div class=\"alert_box\" id=\"alert\">' + text + '</div>').fadeIn('slow').appendTo('#alerts');
}

function clearAlert() {
	$('#alert').fadeOut('slow', function() {
		$('#alerts').empty();
		});
	$('#content').fadeTo('slow', 1.0);
}

function kickClient(hostname, username, password, cn, callback) {
	displayAlert('Kicking client...');
	$.getJSON('http://' + hostname + '/json/admin/kick?username=' + username + '&password=' + password + '&cn=' + cn, callback);
}

function loadPlayerAdminPage(hostname, username, password) {
	$('#main_content').empty();
	html_page = "<h3>Players</h3><ul id=\"players_list\"></ul>";
	$(html_page).appendTo('#main_content');
	getScoreboard(hostname, function(data) {
		$.each(data.clients, function(i, client) {
			html_player = '<li>' + client.name + ': ' + client.frags + ' frags, '
				+ client.deaths + ' deaths (<a href=\"#\" id=\"kick_' + client.cn + '\">kick</a>)</li>';
			$(html_player).appendTo('#players_list');
			$('#kick_' + client.cn).click(function() {
				kickClient(hostname, username, password, client.cn, function(data) {
					clearAlert();
					loadPlayerAdminPage(hostname, username, password);
					});
				});
			});
		});
}

function tryMasterLogin(hostname, username, password, error_callback, success_callback) {
	$.getJSON('http://' + hostname + '/json/account?username=' + username + '&password=' + password, function(data) {
		if(data.hasOwnProperty('privileges'))
		{
			if(data.privileges.master)
				success_callback(data);
			else
				error_callback('INSUFFICIENT_PERMISSIONS');
		}
		else
			error_callback(data);
		});
}

function disableTopNav()
{
	$('#topnav_players').click(function() { });
	$('#topnav_players').click(function() { });
	$('#topnav_logout').click(function() { });
}

function enableTopNav(hostname, username, password)
{
	$('#topnav_players').click(function() { loadPlayerAdminPage(hostname, username, password); });
	$('#topnav_players').click(function() { } );
	$('#topnav_logout').click(function() { window.location.reload(); });
}

function loadLoginPage(hostname, callback) {
	html_page = '<h3>Please login</h3>Username: <input type=\"text\" id=\"username_input\" /><br />Password: <input type=\"password\" id=\"password_input\" /><br /><input type=\"submit\" value=\"Login\" id=\"login_submit\" /><br /><span id=\"login_status\"></span>';
	displayAlert(html_page);
	$('#login_submit').click(function() {
		$('#login_status').empty();
		$('#login_status').html('Trying login...');
		var username = $('#username_input').val();
		var password = $('#password_input').val();
		tryMasterLogin(hostname, username, password, function(error_code) {
				$('#login_status').empty();
				if(error_code == 'INVALID_LOGIN')
					$('#login_status').html('Invalid login.');
				else
					$('#login_status').html('Unknown error.');
				},
			function(data) {
				$('#login_status').empty();
				$('#login_status').html('Success.');
				callback(username, password);
				});
		});
}

function setup(hostname) {
	loadLoginPage(hostname, function(username, password) {
		clearAlert();
		enableTopNav(hostname, username, password);
		loadPlayerAdminPage(hostname, username, password);
		});
}


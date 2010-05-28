function authReqPath(hostname, path, username, password) {
	return 'http://' + hostname + path + '?username=' + username + '&password=' + password;
}

function tryLogin(hostname, username, password, error_callback, success_callback) {
	$.getJSON(authReqPath(hostname, '/json/account', username, password), function(data) {
		if(data.hasOwnProperty('user'))
			success_callback(data);
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

function configPluginSelected(hostname, username, password, plugin_name) {
	if($("#plugin_config_" + plugin_name).html() != "")
		$("#plugin_config_" + plugin_name).empty();
	else
	{
		$.getJSON(authReqPath(hostname, '/json/admin/config/' + plugin_name, username, password), function(data) {
			sections = $("<ul class=\"config_sections\"><h4>Sections</h4></ul>");
			$.each(data.sections, function(i, section) {
				sections.append("<li><a href=\"#\">" + section + "</a></li>");
			});
			$("#plugin_config_" + plugin_name).html(sections);
		});
	}
}

function configPageAddPlugin(hostname, username, password, plugin_name) {
	$("<h3 class=\"head\"><a href=\"#\" id=\"a_config_plugin_" + plugin_name + "\">" + plugin_name + "</a></h3><div id=\"plugin_config_" + plugin_name + "\"></div>").appendTo("#config_plugins");
	$("#a_config_plugin_" + plugin_name).click(function() { configPluginSelected(hostname, username, password, plugin_name); });
}

function configPage(hostname, username, password) {
	$.getJSON(authReqPath(hostname, '/json/admin/config', username, password), function(data) {
		if(data.hasOwnProperty('plugins'))
		{
			$.each(data.plugins, function(i, plugin_name) {
				configPageAddPlugin(hostname, username, password, plugin_name);
			});
		}
		else
			alert("Error");
	});
}

function configPageInvalidLogin() {
}

function adminPageNoLogin(hostname) {
	$("#tabs").tabs();
	configPageInvalidLogin();
}

function adminPage(hostname, username, password) {
	configPage(hostname, username, password);
}

function adminLoginDialog(hostname, callback) {
	$("<div id=\"dialog\" title=\"Please login\">Username:<input type=\"text\" id=\"username_input\" /><br />Password: <input type=\"password\" id=\"password\" /><br /><span id=\"login_status\"></span></div>").dialog(
		{
			modal: true,
			buttons: {
				"Login": function() {
					$('#login_status').empty();
					$('#login_status').html('Trying login...');
					var username = $('#username_input').val();
					var password = $('#password').val();
					tryLogin(hostname, username, password,
						function(data) {
							error_code = data.error
							$('#login_status').empty();
							if(error_code == 'INVALID_LOGIN')
								$('#login_status').html('Invalid login.');
							else
								$('#login_status').html('Unknown error.');
							},
						function(data) {
								$('#login_status').empty();
								$('#login_status').html('Success.');
								$("#dialog").dialog('close');
								callback(username, password);
							});
					}
				}
		});
}

function setup(hostname) {
	adminPageNoLogin(hostname);
	adminLoginDialog(hostname, function(username, password) { 
		adminPage(hostname, username, password);
		});
}


function getClientState(hostname, cn, callback) {
	$.getJSON('http://' + hostname + '/json/clients/' + cn), function(data) {
		callback(data);
	}
}

function getClients(hostname, callback) {
	$.getJSON('http://' + hostname + '/json/clients', function(data) {
		callback(data);
		});
}


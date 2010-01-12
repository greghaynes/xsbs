function getClientState(hostname, cn) {
	$.getJSON('http://' + hostname + '/json/clients/' + cn), function(data) {
		return data.items
	}
}

function getClients(hostname) {
	$.getJSON('http://' + hostname + '/json/clients', function(data) {
		return data.items
		});
}


package net.greghaynes.client;

import com.google.gwt.jsonp.client.JsonpRequestBuilder;

class XsbsRequestBuilder extends JsonpRequestBuilder {

	private String server_url;
	private String api_path;

	public XsbsRequestBuilder(String server_url,
	                          String api_path="/json") {
		super();
		this.server_url = server_url;
		this.api_path = api_path;
	}

	public JsonpRequest<User> requestUser(String username, AsyncCallback<User> callback) {
		
	}

}


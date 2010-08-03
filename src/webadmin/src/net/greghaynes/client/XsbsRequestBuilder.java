package net.greghaynes.client;

import com.google.gwt.jsonp.client.JsonpRequestBuilder;
import com.google.gwt.jsonp.client.JsonpRequest;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.user.client.rpc.AsyncCallback;

public class XsbsRequestBuilder extends JsonpRequestBuilder {

	public static String JSON_PATH_PREFIX = "json";

	public static String JSON_PATH_SCOREBOARD = "game/scoreboard";
	public static String JSON_PATH_SERVERINFO = "game/serverinfo";
	public static String JSON_PATH_SESSION_CREATE = "session/create";

	private String server_url;
	private String api_path;
	private String session_key;

	public XsbsRequestBuilder(String server_url) {
		super();
		this.server_url = server_url;
		this.api_path = api_path;
		this.session_key = null;
	}

	public void setSessionKey(String session_key) {
		this.session_key = session_key;
	}

	public String getSessionKey() {
		return this.session_key;
	}

	public <T extends JavaScriptObject> JsonpRequest<T> requestScoreboard(String username, AsyncCallback<T> callback) {
		return requestObject(getXsbsRequestUrl(XsbsRequestBuilder.JSON_PATH_SCOREBOARD),
		                     callback);
	}

	public <T extends JavaScriptObject> JsonpRequest<T> requestServerInfo(AsyncCallback<T> callback) {
		return requestObject(getXsbsRequestUrl(XsbsRequestBuilder.JSON_PATH_SERVERINFO),
		                     callback);
	}

	public <T extends JavaScriptObject> JsonpRequest<T> requestSessionCreate(AsyncCallback<T> callback) {
		return requestObject(getXsbsRequestUrl(XsbsRequestBuilder.JSON_PATH_SESSION_CREATE),
			callback);
	}

	private String getXsbsRequestUrl(String json_path) {
		String ret = this.server_url + "/" + XsbsRequestBuilder.JSON_PATH_PREFIX + "/" + json_path;
		if(this.session_key != null)
		{
			ret += "?sessionkey=" + this.session_key;
		}
		return ret;
	}

}


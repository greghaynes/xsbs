package net.greghaynes.client;

import java.util.ArrayList;
import com.google.gwt.jsonp.client.JsonpRequestBuilder;
import com.google.gwt.jsonp.client.JsonpRequest;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.user.client.ui.PopupPanel;
import java.util.Iterator;

public class LoginManager implements AsyncCallback<JavaScriptObject> {

	private static String loginReqPath = "/json/login";

	private String serverUrl;

	private String username;
	private String sessionKey;
	private ArrayList<LoginListener> loginListeners;

	public LoginManager(String serverUrl) {
		this.serverUrl = serverUrl;
		this.loginListeners = new ArrayList<LoginListener>();
	}

	public boolean isLoggedIn() {
		return !this.sessionKey.isEmpty();
	}

	public String getSessionKey() {
		return this.sessionKey;
	}

	public String getUsername() {
		return this.username;
	}

	public void addLoginListener(LoginListener l) {
		this.loginListeners.add(l);
	}

	public void tryLogin(String username, String password) {
		String reqUrl = this.serverUrl + LoginManager.loginReqPath +
		                "?username=" + username + "&password=" +
		                password;
		JsonpRequestBuilder jsonp = new JsonpRequestBuilder();
		jsonp.requestObject(reqUrl, this);

		LoginEvent event = new LoginEvent(this, username, "", LoginEvent.LOGIN_INITIATED);
		LoginListener l;
		Iterator<LoginListener> itr = loginListeners.iterator();
		while(itr.hasNext()) {
			l = itr.next();
			l.loginInitiated(event);
		}
	}

	public void onFailure(java.lang.Throwable caught) {
		LoginEvent event = new LoginEvent(this, username, "", LoginEvent.LOGIN_FAILED);
		LoginListener l;
		Iterator<LoginListener> itr = loginListeners.iterator();
		while(itr.hasNext()) {
			l = itr.next();
			l.loginFailed(event, caught);
		}
	}

	public void onSuccess(JavaScriptObject obj) {
		
	}

}


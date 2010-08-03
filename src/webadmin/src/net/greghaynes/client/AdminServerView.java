package net.greghaynes.client;

import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.core.client.JavaScriptObject;

public class AdminServerView {

	private xsbsAdmin admin;
	private SessionManager sessionManager;
	private XsbsRequestBuilder requestBuilder;
	private LoginDialog loginDialog;

	public AdminServerView(xsbsAdmin admin, String serverUrl) {
		this.admin = admin;
		this.requestBuilder = new XsbsRequestBuilder(serverUrl);
		this.sessionManager = new SessionManager(this, requestBuilder);

		this.sessionManager.initiateSession();
	}

	public void onSessionStarted(String sessionKey) {
		this.requestBuilder.setSessionKey(sessionKey);
	}

	public void onSessionEnded() {
		this.requestBuilder.setSessionKey(null);
	}

	public void onLoginSelected(String username, String password) {
	}

	public void onLoggedIn() {
	}

	public void onLoggedOut() {
	}

	public void onLoginError(String error) {
	}

	public void setVisible(boolean value) {
	}

	public void show() {
		this.setVisible(true);
	}

	public void hide() {
		this.setVisible(false);
	}

}


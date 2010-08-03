package net.greghaynes.client;

import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.user.client.ui.PushButton;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.ClickEvent;

public class SessionManager extends DialogBox implements AsyncCallback<JavaScriptObject>, ClickHandler {

	private AdminServerView adminView;
	private XsbsRequestBuilder requestBuilder;
	private HTML mainHtml;
	private PushButton retryButton;
	private VerticalPanel mainPanel;

	public SessionManager(AdminServerView adminView, XsbsRequestBuilder requestBuilder) {
		this.adminView = adminView;
		this.requestBuilder = requestBuilder;

		this.mainHtml = new HTML("");
		this.retryButton = new PushButton("Retry");
		this.retryButton.addClickHandler(this);
		this.mainPanel = new VerticalPanel();

		this.mainPanel.add(mainHtml);

		this.add(mainPanel);
	}

	public void initiateSession() {
		this.setHTML("Please wait");
		this.mainHtml.setHTML("Establishing session with server...");
		this.center();

		this.requestBuilder.requestSessionCreate(this);
	}

	public void onSuccess(JavaScriptObject jsObj) {
		this.adminView.onSessionStarted("testkey");
		this.hide();
	}

	public void onFailure(Throwable e) {
		this.showError("Could not establish session with server");
	}

	public void showError(String description) {
		this.setHTML("Error");
		this.mainHtml.setHTML(description);
		this.mainPanel.add(retryButton);
	}

	public void onClick(ClickEvent e) {
		this.mainPanel.remove(retryButton);
		this.initiateSession();
	}

}


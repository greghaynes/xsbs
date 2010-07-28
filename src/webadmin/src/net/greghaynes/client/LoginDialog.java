package net.greghaynes.client;

import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.DeckPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.PushButton;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.ClickEvent;

public class LoginDialog extends PopupPanel implements LoginListener, ClickHandler {

	private LoginManager loginManager;
	private DeckPanel deckPanel;
	private TextBox usernameBox;
	private TextBox passwordBox;
	private PushButton loginButton;
	private PushButton retryButton;

	public LoginDialog(LoginManager manager) {
		this.loginManager = manager;
		this.loginManager.addLoginListener(this);

		this.usernameBox = new TextBox();
		this.passwordBox = new TextBox();

		this.loginButton = new PushButton("Login");
		this.loginButton.addClickHandler(this);

		this.retryButton = new PushButton("Retry");
		this.retryButton.addClickHandler(this);

		HorizontalPanel usernameHorizPanel = new HorizontalPanel();
		usernameHorizPanel.add(new HTML("Username:"));
		usernameHorizPanel.add(this.usernameBox);

		HorizontalPanel passwordHorizPanel = new HorizontalPanel();
		passwordHorizPanel.add(new HTML("Password:"));
		passwordHorizPanel.add(this.passwordBox);

		HorizontalPanel loginHorizPanel = new HorizontalPanel();
		loginHorizPanel.add(this.loginButton);

		VerticalPanel inputVertPanel = new VerticalPanel();
		inputVertPanel.add(new HTML("<h3>Please login</h3>"));
		inputVertPanel.add(usernameHorizPanel);
		inputVertPanel.add(passwordHorizPanel);
		inputVertPanel.add(loginHorizPanel);

		HorizontalPanel retryHorizPanel = new HorizontalPanel();
		retryHorizPanel.add(this.retryButton);

		VerticalPanel loginErrorPanel = new VerticalPanel();
		loginErrorPanel.add(new HTML("<h3>Error</h3><p>An error was encountered while logging in."));
		loginErrorPanel.add(retryHorizPanel);

		this.deckPanel = new DeckPanel();
		this.deckPanel.add(new HTML("Logging in..."));
		this.deckPanel.add(loginErrorPanel);
		this.deckPanel.add(inputVertPanel);
		this.deckPanel.showWidget(2);

		this.add(deckPanel);
	}

	public void loginInitiated(LoginEvent e) {
		this.deckPanel.showWidget(0);
		this.center();
	}

	public void loginSucceeded(LoginEvent e) {
		this.hide();
	}

	public void loginEnded(LoginEvent e) {
		this.deckPanel.showWidget(2);
		this.center();
	}

	public void loginFailed(LoginEvent e, java.lang.Throwable caught) {
		this.deckPanel.showWidget(1);
		this.center();
	}

	public void onClick(ClickEvent e) {
		Object o = e.getSource();
		if(o == this.loginButton) {
			this.loginManager.tryLogin(this.usernameBox.getText(),
						   this.passwordBox.getText());
		}
		else if(o == retryButton) {
			this.deckPanel.showWidget(2);
			this.center();
		}
	}

}


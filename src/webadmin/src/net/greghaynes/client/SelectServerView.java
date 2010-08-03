package net.greghaynes.client;

import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.PushButton;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.ClickEvent;

public class SelectServerView extends DialogBox implements ClickHandler {

	private xsbsAdmin admin;
	private PushButton connectButton;
	private TextBox urlBox;

	public SelectServerView(xsbsAdmin admin) {
		super();
		this.setHTML("Select Server");

		this.admin = admin;
		urlBox = new TextBox();
		connectButton = new PushButton("Connect");
		connectButton.addClickHandler(this);

		HorizontalPanel urlHorizPanel = new HorizontalPanel();
		urlHorizPanel.add(new HTML("Server Location:"));
		urlHorizPanel.add(urlBox);

		HorizontalPanel buttonHorizPanel = new HorizontalPanel();
		buttonHorizPanel.add(connectButton);

		VerticalPanel mainVertPanel = new VerticalPanel();
		mainVertPanel.add(new HTML("<h3>Enter a server location to connect to</h3>"));
		mainVertPanel.add(urlHorizPanel);
		mainVertPanel.add(buttonHorizPanel);
		
		this.add(mainVertPanel);
	}

	public void onClick(ClickEvent e) {
		this.admin.serverSelected(this.urlBox.getText());
	}

}


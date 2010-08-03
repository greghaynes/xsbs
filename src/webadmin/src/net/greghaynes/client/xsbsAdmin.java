package net.greghaynes.client;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.DockPanel;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HTML;

/**
 * Entry point classes define <code>onModuleLoad()</code>.
 */
public class xsbsAdmin implements EntryPoint {

	private SelectServerView selectServerView;
	private AdminServerView adminServerView;

	/**
	* The message displayed to the user when the server cannot be reached or
	* returns an error.
	*/
	private static final String SERVER_ERROR = "An error occurred while "
	+ "attempting to contact the server. Please check your network "
	+ "connection and try again.";

	/**
	* This is the entry point method.
	*/
	public void onModuleLoad() {
		this.selectServerView = new SelectServerView(this);
		this.selectServerView.center();
	}

	public void serverSelected(String url) {
		this.selectServerView.hide();
		this.adminServerView = new AdminServerView(this, url);
		this.adminServerView.setVisible(true);
	}

	public void serverDeselected() {
		this.adminServerView.hide();
		this.selectServerView.center();
	}

}

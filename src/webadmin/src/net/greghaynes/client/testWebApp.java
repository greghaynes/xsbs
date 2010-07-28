package net.greghaynes.client;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.DockPanel;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HTML;

/**
 * Entry point classes define <code>onModuleLoad()</code>.
 */
public class testWebApp implements EntryPoint {
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
		RootPanel rootPanel = RootPanel.get();

		DockPanel basePanel = new DockPanel();
		basePanel.setWidth("100%");

		HTML topTextBar = new HTML("Top text");
		topTextBar.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);
		topTextBar.setStyleName("topTextBar");
		basePanel.add(topTextBar, DockPanel.NORTH);

		rootPanel.add(basePanel);

		LoginManager m = new LoginManager("localhost:8081");

		LoginDialog ld = new LoginDialog(m);
		ld.center();
	}

}

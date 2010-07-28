package net.greghaynes.client;

public interface LoginListener {

	public void loginInitiated(LoginEvent e);
	public void loginSucceeded(LoginEvent e);
	public void loginEnded(LoginEvent e);
	public void loginFailed(LoginEvent e, java.lang.Throwable caught);

}


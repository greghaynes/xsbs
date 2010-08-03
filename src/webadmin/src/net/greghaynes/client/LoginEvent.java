package net.greghaynes.client;

public class LoginEvent {

	public static int LOGIN_INITIATED = 1;
	public static int LOGIN_SUCCEEDED = 2;
	public static int LOGIN_ENDED = 3;
	public static int LOGIN_FAILED = 4;

	private int event;
	private String username;

	public LoginEvent(String username, String key,
	                  int event) {
	}

	public LoginEvent() {
		this.event = event;
	}

	public int getEvent() {
		return this.event;
	}

	public String getUsername() {
		return this.username;
	}

}


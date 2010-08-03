package net.greghaynes.client;

public class User {

	private int id;
	private String username;

	public User(int id, String username) {
		this.id = id;
		this.username = username;
	}

	public int getId() {
		return this.id;
	}

	public String getUsername() {
		return this.username;
	}

}


package net.greghaynes.client;

import java.lang.Error;

public class InvalidResponseError extends Error {

	public InvalidResponseError(String cause) {
		super(cause);
	}

}


package net.greghaynes.client;

import java.util.ArrayList;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.json.client.JSONArray;

public class Scoreboard {

	private ArrayList<Player> players;
	private ArrayList<Team> teams;

	public static Scoreboard createScoreboard(JSONObject json) {
		JSONValue jsonPlayers = json.get("players");
		if(jsonPlayers == null)
			return null;
		JSONValue jsonTeams = json.get("teams");
		if(jsonTeams == null)
			return null;

		JSONArray jsonArrayPlayers = jsonPlayers.isArray();
		if(jsonArrayPlayers == null)
			return null;

		JSONArray jsonArrayTeams = jsonTeams.isArray();
		if(jsonArrayTeams == null)
			return null;

		ArrayList<Player> players = new ArrayList<Player>();
		int i, playersSize = jsonArrayPlayers.size();
		for(i = 0;i < playersSize; i++) {
			JSONObject objP = jsonArrayPlayers.get(i).isObject();
			if(objP == null)
				continue;
			Player p = new Player(objP);
			if(p == null)
				continue;
			players.add(p);
		}

		ArrayList<Team> teams = new ArrayList<Team>();
		int teamsSize = jsonArrayTeams.size();
		for(i = 0;i < teamsSize; i++) {
			JSONObject objT = jsonArrayTeams.get(i).isObject();
			if(objT == null)
				continue;
			Team t = Team.createTeam(objT);
			if(t == null)
				continue;
			teams.add(t);
		}

		return new Scoreboard(players, teams);
	}

	public Scoreboard(JSONObject object) {
		JSONValue val;
		JSONArray arr;
		int i;

		this.players = new ArrayList<Player>();
		val = object.get("players");
		if(val != null) {
			arr = val.isArray();
			if(arr != null) {
				for(i = 0;i < arr.size();i++) {
					Player p = new Player(arr.get(i).isObject());
					this.players.add(p);
				}
			}
		}
	}

	public Scoreboard(ArrayList<Player> players, ArrayList<Team> teams) {
		this.players = players;
		this.teams = teams;
	}

	public ArrayList<Player> getPlayers() {
		return this.players;
	}
	

	public ArrayList<Team> getTeams() {
		return this.teams;
	}

}


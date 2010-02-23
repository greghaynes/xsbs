#include "server.h"
#include "sbcs.h"
#include <string>

// returned on error if we're returning an int
const int RINT_ERROR = -1;

// boolean constants, since cubescript doesn't have them
const int CS_FALSE = 0;
const int CS_TRUE = 1;

#define CN_INFO_RET(ret) server::clientinfo *ci = server::getinfo(*cn); \
		if(!ci) \
		{ \
			intret(RINT_ERROR); \
			return; \
		} \
		intret(ret);
		

namespace SbCs
{
	int cseval(std::string data)
	{
		return execute(data.c_str());
	}

	void playershots(int *cn)
	{
		CN_INFO_RET(ci->state.shots);
		/*server::clientinfo *ci = server::getinfo(*cn);

		if(!ci)
		{
			// todo: some error mechanism
			intret(RINT_ERROR);
			return;
		}

		intret(ci->state.shots);*/
	}

	void playerhits(int *cn)
	{
		CN_INFO_RET(ci->state.hits);
	}

	void playerfrags(int *cn)
	{
		CN_INFO_RET(ci->state.frags)
	}

	void playertks(int *cn)
	{
		CN_INFO_RET(ci->state.teamkills)
	}

	void playerdeaths(int *cn)
	{
		CN_INFO_RET(ci->state.deaths)
	}

	void playerping(int *cn)
	{
		CN_INFO_RET(ci->ping);
	}

	void playerscore(int *cn)
	{
		CN_INFO_RET(ci->state.flags)
	}

	void playername(int *cn)
	{
		server::clientinfo *ci = server::getinfo(*cn);

		if(!ci)
		{
			// todo: some error mechanism
			result("error");
			return;
		}

		result(ci->name);
	}

	void playermessage(int *cn, char *msg)
	{
		server::clientinfo *ci = server::getinfo(*cn);

		if(!ci)
		{
			// todo: some error mechanism
			intret(RINT_ERROR);
			return;
		}

		if(ci->state.aitype != AI_NONE)
		{
			// todo: error
			intret(RINT_ERROR);
			return;
		}

		sendf(*cn, 1, "ris", SV_SERVMSG, msg);
	}

	void playersessionid(int *cn)
	{
		CN_INFO_RET(getclientip(ci->sessionid))
	}

	void playeriplong(int *cn)
	{
		CN_INFO_RET(getclientip(ci->clientnum))
	}

	void playerkick(int *cn)
	{
		server::clientinfo *ci = server::getinfo(*cn);

		if(!ci)
		{
			// todo: some error mechanism
			intret(RINT_ERROR);
			return;
		}

		disconnect_client(*cn, DISC_KICK);
	}

	void playerspectate(int *cn)
	{
		server::clientinfo *ci = server::getinfo(*cn);

		if(!ci)
		{
			// todo: some error mechanism
			intret(RINT_ERROR);
			return;
		}

		printf("going to spectate %d\n", *cn);
		server::spectate(ci, true, *cn);
	}

	void playerunspectate(int *cn)
	{
		server::clientinfo *ci = server::getinfo(*cn);

		if(!ci)
		{
			// todo: some error mechanism
			intret(RINT_ERROR);
			return;
		}

		server::spectate(ci, false, *cn);
	}

	void playerisspectator(int *cn)
	{
		CN_INFO_RET(((ci->state.state == CS_SPECTATOR) ? CS_TRUE : CS_FALSE))
	}

	void playersetteam(int *cn, char *team)
	{
		server::clientinfo *ci = server::getinfo(*cn);

		if(!ci)
		{
			// todo: some error mechanism
			intret(RINT_ERROR);
			return;
		}

		server::setteam(ci, team);
	}

	void playerteam(int *cn)
	{
		server::clientinfo *ci = server::getinfo(*cn);

		if(!ci)
		{
			// todo: some error mechanism
			intret(RINT_ERROR);
			return;
		}

		if(ci->state.state==CS_SPECTATOR)
		{
			result("error");
			return;
		}

		result(ci->team);
	}

	void setpaused(int *v)
	{
		bool b = (*v == CS_TRUE) ? true : false;

		server::pausegame(b);
	}

	void ispaused()
	{
		intret( (server::gamepaused == true) ? CS_TRUE : CS_FALSE );
	}

	void setmap(char *map, int *mode)
	{
		server::setmap(map, *mode);
	}

	void setmastermode(int *mm)
	{
		server::setmastermode(*mm);
	}

	void mastermode()
	{
		intret(server::mastermode);
	}

	void gamemode()
	{
		intret(server::gamemode);
	}
	
	void mapname()
	{
		result(server::smapname);
	}

	void modename(int *mm)
	{
		if(!m_valid(*mm))
		{
			result("Invalid mode");
			return;
		}

		result(server::modename(*mm));
	}

	void uptime()
	{
		intret(totalmillis);
	}


	// command list
	COMMAND(playershots, "i");
	COMMAND(playerhits, "i");
	COMMAND(playerfrags, "i");
	COMMAND(playertks, "i");
	COMMAND(playerdeaths, "i");
	COMMAND(playerping, "i");
	COMMAND(playerscore, "i");
	COMMAND(playername, "i");
	COMMAND(playermessage, "is");
	COMMAND(playersessionid, "i");
	COMMAND(playeriplong, "i");
	COMMAND(playerkick, "i");
	COMMAND(playerspectate, "i");
	COMMAND(playerunspectate, "i");
	COMMAND(playerisspectator, "i");
	COMMAND(playersetteam, "is");
	COMMAND(playerteam, "i");
	COMMAND(setpaused, "i");
	COMMAND(ispaused, "");
	COMMAND(setmap, "si");
	COMMAND(setmastermode, "i");
	COMMAND(mastermode, "");
	COMMAND(gamemode, "");
	COMMAND(mapname, "");
	COMMAND(modename, "i");
	COMMAND(uptime, "");
}
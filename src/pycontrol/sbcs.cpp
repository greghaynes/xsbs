#include "server.h"
#include "sbcs.h"
#include <string>

namespace SbCs
{
	int cseval(std::string data)
	{
		return execute(data.c_str());
	}

	void xsbs_test(int *one, int *two)
	{
		intret(*one + *two + 1);
	}

	void player_shots(int *cn)
	{
		server::clientinfo *ci = server::getinfo(*cn);

		if(!ci)
		{
			// todo: some error mechanism
			intret(0);
			return;
		}

		intret(ci->state.shots);
	}


	COMMAND(player_shots, "i");
	COMMAND(xsbs_test, "ii");
}
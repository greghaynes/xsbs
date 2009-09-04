/*

 This portion of the header is a redistribution of code origininally in the sauerbraten source code.

 */

#ifndef SB_SERVER_H
#define SB_SERVER_H

#include "game.h"
#include "logging.h"

namespace server
{

    struct server_entity            // server side version of "entity" type
    {
        int type;
        int spawntime;
        char spawned;
    };
	
    static const int DEATHMILLIS = 300;
	
    struct clientinfo;
	
    struct gameevent
    {
        virtual ~gameevent() {}
		
        virtual bool flush(clientinfo *ci, int fmillis);
        virtual void process(clientinfo *ci) {}
		
        virtual bool keepable() const { return false; }
    };
	
    struct timedevent : gameevent
    {
        int millis;
		
        bool flush(clientinfo *ci, int fmillis);
    };
	
    struct hitinfo
    {
        int target;
        int lifesequence;
        union
        {
            int rays;
            float dist;
        };
        vec dir;
    };
	
    struct shotevent : timedevent
    {
        int id, gun;
        vec from, to;
        vector<hitinfo> hits;
		
        void process(clientinfo *ci);
    };
	
    struct explodeevent : timedevent
    {
        int id, gun;
        vector<hitinfo> hits;
		
        bool keepable() const { return true; }
		
        void process(clientinfo *ci);
    };
	
    struct suicideevent : gameevent
    {
        void process(clientinfo *ci);
    };
	
    struct pickupevent : gameevent
    {
        int ent;
		
        void process(clientinfo *ci);
    };
	
    template <int N>
    struct projectilestate
    {
        int projs[N];
        int numprojs;
		
        projectilestate() : numprojs(0) {}
		
        void reset() { numprojs = 0; }
		
        void add(int val)
        {
            if(numprojs>=N) numprojs = 0;
            projs[numprojs++] = val;
        }
		
        bool remove(int val)
        {
            loopi(numprojs) if(projs[i]==val)
            {
                projs[i] = projs[--numprojs];
                return true;
            }
            return false;
        }
    };
	
    struct gamestate : fpsstate
    {
        vec o;
        int state, editstate;
        int lastdeath, lastspawn, lifesequence;
        int lastshot;
        projectilestate<8> rockets, grenades;
        int frags, flags, deaths, teamkills, shotdamage, damage;
        int lasttimeplayed, timeplayed;
		int shots, hits;
        float effectiveness;
		
        gamestate() : state(CS_DEAD), editstate(CS_DEAD) {}
		
        bool isalive(int gamemillis)
        {
            return state==CS_ALIVE || (state==CS_DEAD && gamemillis - lastdeath <= DEATHMILLIS);
        }
		
        bool waitexpired(int gamemillis)
        {
            return gamemillis - lastshot >= gunwait;
        }
		
        void reset()
        {
            if(state!=CS_SPECTATOR) state = editstate = CS_DEAD;
            maxhealth = 100;
            rockets.reset();
            grenades.reset();
            timeplayed = 0;
            effectiveness = 0;
            frags = flags = deaths = teamkills = shotdamage = damage = 0;
            shots = hits = 0;
            respawn();
        }
		
        void respawn()
        {
            fpsstate::respawn();
            o = vec(-1e10f, -1e10f, -1e10f);
            lastdeath = 0;
            lastspawn = -1;
            lastshot = 0;
        }
		
        void reassign()
        {
            respawn();
            rockets.reset();
            grenades.reset();
        }
    };
	
    struct savedscore
    {
        uint ip;
        string name;
        int maxhealth, frags, flags, deaths, teamkills, shotdamage, damage;
        int timeplayed;
        float effectiveness;
		
        void save(gamestate &gs)
        {
            maxhealth = gs.maxhealth;
            frags = gs.frags;
            flags = gs.flags;
            deaths = gs.deaths;
            teamkills = gs.teamkills;
            shotdamage = gs.shotdamage;
            damage = gs.damage;
            timeplayed = gs.timeplayed;
            effectiveness = gs.effectiveness;
        }
		
        void restore(gamestate &gs)
        {
            if(gs.health==gs.maxhealth) gs.health = maxhealth;
            gs.maxhealth = maxhealth;
            gs.frags = frags;
            gs.flags = flags;
            gs.deaths = deaths;
            gs.teamkills = teamkills;
            gs.shotdamage = shotdamage;
            gs.damage = damage;
            gs.timeplayed = timeplayed;
            gs.effectiveness = effectiveness;
        }
    };
	
    struct clientinfo
    {
        int clientnum, ownernum, connectmillis, sessionid;
        string name, team, mapvote;
        int playermodel;
        int modevote;
        int privilege;
        bool connected, local, timesync;
        int gameoffset, lastevent;
        gamestate state;
        vector<gameevent *> events;
        vector<uchar> position, messages;
        int posoff, poslen, msgoff, msglen;
        vector<clientinfo *> bots;
        uint authreq;
        string authname;
        int ping, aireinit;
        string clientmap;
        int mapcrc;
        bool warned, gameclip, active;
		
        clientinfo() { reset(); }
        ~clientinfo() { events.deletecontentsp(); }
		
        void addevent(gameevent *e)
        {
            if(state.state==CS_SPECTATOR || events.length()>100) delete e;
            else events.add(e);
        }
		
        void mapchange()
        {
            mapvote[0] = 0;
            state.reset();
            events.deletecontentsp();
            timesync = false;
            lastevent = 0;
            clientmap[0] = '\0';
            mapcrc = 0;
            warned = false;
            gameclip = false;
        }
		
        void reassign()
        {
            state.reassign();
            events.deletecontentsp();
            timesync = false;
            lastevent = 0;
        }
		
        void reset()
        {
            name[0] = team[0] = 0;
            playermodel = -1;
            privilege = PRIV_NONE;
            connected = local = false;
            authreq = 0;
            position.setsizenodelete(0);
            messages.setsizenodelete(0);
            ping = 0;
            aireinit = 0;
            mapchange();
        }
		
        int geteventmillis(int servmillis, int clientmillis)
        {
            if(!timesync || (events.empty() && state.waitexpired(servmillis)))
            {
                timesync = true;
                gameoffset = servmillis - clientmillis;
                return servmillis;
            }
            else return gameoffset + clientmillis;
        }
    };
	
    struct worldstate
    {
        int uses;
        vector<uchar> positions, messages;
    };
	
    struct ban
    {
        int time;
        uint ip;
    };
	
    namespace aiman
    {
        extern void removeai(clientinfo *ci);
        extern void clearai();
        extern void checkai();
        extern void reqadd(clientinfo *ci, int skill);
        extern void reqdel(clientinfo *ci);
        extern void setbotlimit(clientinfo *ci, int limit);
        extern void setbotbalance(clientinfo *ci, bool balance);
        extern void changemap();
        extern void addclient(clientinfo *ci);
        extern void changeteam(clientinfo *ci);
    }

}

/*

 This portion of the header is a modified version of the sauerbraten source code.

*/
namespace server
{

	extern vector<clientinfo *> connects, clients, bots;
	extern Log eventlog;

	int numclients(int exclude = -1, bool nospec = true, bool noai = true);
	void sendservmsg(const char *s);
	clientinfo *getinfo(int n);

}

#endif


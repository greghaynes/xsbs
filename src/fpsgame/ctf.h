#ifndef PARSEMESSAGES

#define SERVMODE 1

#define ctfteamflag(s) (!strcmp(s, "good") ? 1 : (!strcmp(s, "evil") ? 2 : 0))
#define ctfflagteam(i) (i==1 ? "good" : (i==2 ? "evil" : NULL))

#ifdef SERVMODE
struct ctfservmode : servmode
#else
struct ctfclientmode : clientmode
#endif
{
    static const int MAXFLAGS = 20;
    static const int FLAGRADIUS = 16;
    static const int FLAGLIMIT = 10;

    struct flag
    {
        int id;
        vec droploc, spawnloc;
        int team, droptime;
#ifdef SERVMODE
        int owner, invistime;
#else
        fpsent *owner;
        float dropangle, spawnangle;
        entitylight light;
        vec interploc;
        float interpangle;
        int interptime, vistime;
#endif

        flag() { reset(); }

        void reset()
        {
            droploc = spawnloc = vec(0, 0, 0);
#ifdef SERVMODE
            owner = -1;
            invistime = 0;
#else
            loopv(players) players[i]->flagpickup &= ~(1<<id);
            owner = NULL;
            dropangle = spawnangle = 0;
            interploc = vec(0, 0, 0);
            interpangle = 0;
            interptime = 0;
            vistime = -1000;
#endif
            team = 0;
            droptime = 0;
        }

#ifndef SERVMODE
        const vec &pos()
        {
        	if(owner) return vec(owner->o).sub(owner->eyeheight);
        	if(droptime) return droploc;
        	return spawnloc;
        }
#endif
    };
    vector<flag> flags;
    int scores[2];

    void resetflags()
    {
        flags.setsize(0);
        loopk(2) scores[k] = 0;
    }

#ifdef SERVMODE
    void addflag(int i, const vec &o, int team, int invistime = 0)
#else
    void addflag(int i, const vec &o, int team, int vistime = -1000)
#endif
    {
        if(i<0 || i>=MAXFLAGS) return;
        while(flags.length()<=i) flags.add();
        flag &f = flags[i];
        f.reset();
        f.id = i;
        f.team = team;
        f.spawnloc = o;
#ifdef SERVMODE
        f.invistime = invistime;
#else
        f.vistime = vistime;
#endif
    }

#ifdef SERVMODE
    void ownflag(int i, int owner)
#else
    void ownflag(int i, fpsent *owner, int owntime)
#endif
    {
        flag &f = flags[i];
        f.owner = owner;
#ifdef SERVMODE
        f.invistime = 0;
#else
        loopv(players) players[i]->flagpickup &= ~(1<<f.id);
        if(!f.vistime) f.vistime = owntime;
#endif
    }

#ifdef SERVMODE
    void dropflag(int i, const vec &o, int droptime)
#else
    void dropflag(int i, const vec &o, float yaw, int droptime)
#endif
    {
        flag &f = flags[i];
        f.droploc = o;
        f.droptime = droptime;
#ifdef SERVMODE
        f.owner = -1;
        f.invistime = 0;
#else
        loopv(players) players[i]->flagpickup &= ~(1<<f.id);
        f.owner = NULL;
        f.dropangle = yaw;
        if(!f.vistime) f.vistime = droptime;
#endif
    }

#ifdef SERVMODE
    void returnflag(int i, int invistime = 0)
#else
    void returnflag(int i, int vistime = -1000)
#endif
    {
        flag &f = flags[i];
        f.droptime = 0;
#ifdef SERVMODE
        f.owner = -1;
        f.invistime = invistime;
#else
        loopv(players) players[i]->flagpickup &= ~(1<<f.id);
        f.vistime = vistime;
        f.owner = NULL;
#endif
    }

    int totalscore(int team)
    {
        return team >= 1 && team <= 2 ? scores[team-1] : 0;
    }

    int setscore(int team, int score)
    {
        if(team >= 1 && team <= 2) return scores[team-1] = score;
        return 0;
    }

    int addscore(int team, int score)
    {
        if(team >= 1 && team <= 2) return scores[team-1] += score;
        return 0;
    }

    bool hidefrags() { return true; }

    int getteamscore(const char *team)
    {
        return totalscore(ctfteamflag(team));
    }

    void getteamscores(vector<teamscore> &tscores)
    {
        loopk(2) if(scores[k]) tscores.add(teamscore(ctfflagteam(k+1), scores[k]));
    }

#ifdef SERVMODE
    static const int RESETFLAGTIME = 10000;
    static const int INVISFLAGTIME = 20000;

    bool notgotflags;

    ctfservmode() : notgotflags(false) {}

    void reset(bool empty)
    {
        resetflags();
        notgotflags = !empty;
    }

    void dropflag(clientinfo *ci)
    {
        if(notgotflags) return;
        loopv(flags) if(flags[i].owner==ci->clientnum)
        {
            ivec o(vec(ci->state.o).mul(DMF));
            sendf(-1, 1, "ri6", SV_DROPFLAG, ci->clientnum, i, o.x, o.y, o.z);
            dropflag(i, o.tovec().div(DMF), lastmillis);
        }
    }

    void leavegame(clientinfo *ci, bool disconnecting = false)
    {
        dropflag(ci);
    }

    void died(clientinfo *ci, clientinfo *actor)
    {
        dropflag(ci);
    }

    bool canchangeteam(clientinfo *ci, const char *oldteam, const char *newteam)
    {
        return ctfteamflag(newteam) > 0;
    }

    void changeteam(clientinfo *ci, const char *oldteam, const char *newteam)
    {
        dropflag(ci);
    }

    void scoreflag(clientinfo *ci, int goal, int relay = -1)
    {
        returnflag(relay >= 0 ? relay : goal, relay >= 0 ? 0 : lastmillis);
        ci->state.flags++;
        int team = ctfteamflag(ci->team), score = addscore(team, 1);
        sendf(-1, 1, "ri6", SV_SCOREFLAG, ci->clientnum, relay, goal, team, score);
        if(score >= FLAGLIMIT) startintermission();
    }

    void takeflag(clientinfo *ci, int i)
    {
        if(notgotflags || !flags.inrange(i) || ci->state.state!=CS_ALIVE || !ci->team[0]) return;
        flag &f = flags[i];
        if(!ctfflagteam(f.team) || f.owner>=0) return;
        int team = ctfteamflag(ci->team);
        if(m_protect == (f.team==team))
        {
            loopvj(flags) if(flags[j].owner==ci->clientnum) return;
            ownflag(i, ci->clientnum);
            sendf(-1, 1, "ri3", SV_TAKEFLAG, ci->clientnum, i);
        }
        else if(m_protect)
        {
            if(!f.invistime) scoreflag(ci, i);
        }
        else if(f.droptime)
        {
            returnflag(i);
            sendf(-1, 1, "ri3", SV_RETURNFLAG, ci->clientnum, i);
        }
        else
        {
            loopvj(flags) if(flags[j].owner==ci->clientnum) { scoreflag(ci, i, j); break; }
        }
    }

    void update()
    {
        if(minremain<=0 || notgotflags) return;
        loopv(flags)
        {
            flag &f = flags[i];
            if(f.owner<0 && f.droptime && lastmillis - f.droptime >= RESETFLAGTIME)
            {
                returnflag(i, m_protect ? lastmillis : 0);
                sendf(-1, 1, "ri4", SV_RESETFLAG, i, f.team, addscore(f.team, m_protect ? -1 : 0));
            }
            if(f.invistime && lastmillis - f.invistime >= INVISFLAGTIME)
            {
                f.invistime = 0;
                sendf(-1, 1, "ri3", SV_INVISFLAG, i, 0);
            }
        }
    }

    void initclient(clientinfo *ci, packetbuf &p, bool connecting)
    {
        putint(p, SV_INITFLAGS);
        loopk(2) putint(p, scores[k]);
        putint(p, flags.length());
        loopv(flags)
        {
            flag &f = flags[i];
            putint(p, f.owner);
            putint(p, f.invistime ? 1 : 0);
            if(f.owner<0)
            {
                putint(p, f.droptime ? 1 : 0);
                if(f.droptime)
                {
                    putint(p, int(f.droploc.x*DMF));
                    putint(p, int(f.droploc.y*DMF));
                    putint(p, int(f.droploc.z*DMF));
                }
            }
        }
    }

    void parseflags(ucharbuf &p, bool commit)
    {
        int numflags = getint(p);
        loopi(numflags)
        {
            int team = getint(p);
            vec o;
            loopk(3) o[k] = getint(p)/DMF;
            if(p.overread()) break;
            if(commit && notgotflags) addflag(i, o, team, m_protect ? lastmillis : 0);
        }
        if(commit) notgotflags = false;
    }
};
#else
    static const int RESPAWNSECS = 5;

    float radarscale;

    ctfclientmode() : radarscale(0)
    {
        CCOMMAND(dropflag, "", (ctfclientmode *self), { self->trydropflag(); });
    }

    void preload()
    {
        static const char *flagmodels[2] = { "flags/red", "flags/blue" };
        loopi(2) preloadmodel(flagmodels[i]);
    }

    void drawradar(float x, float y, float s)
    {
        glTexCoord2f(0.0f, 0.0f); glVertex2f(x,   y);
        glTexCoord2f(1.0f, 0.0f); glVertex2f(x+s, y);
        glTexCoord2f(1.0f, 1.0f); glVertex2f(x+s, y+s);
        glTexCoord2f(0.0f, 1.0f); glVertex2f(x,   y+s);
    }

    void drawblips(fpsent *d, int x, int y, int s, int i, bool flagblip)
    {
        flag &f = flags[i];
        settexture(f.team==ctfteamflag(player1->team) ?
                    (flagblip ? "packages/hud/blip_blue_flag.png" : "packages/hud/blip_blue.png") :
                    (flagblip ? "packages/hud/blip_red_flag.png" : "packages/hud/blip_red.png"));
        float scale = radarscale<=0 || radarscale>maxradarscale ? maxradarscale : radarscale;
        vec dir;
        if(flagblip) dir = f.owner ? f.owner->o : (f.droptime ? f.droploc : f.spawnloc);
        else dir = f.spawnloc;
        dir.sub(d->o);
        dir.z = 0.0f;
        float size = flagblip ? 0.1f : 0.05f,
              xoffset = flagblip ? -2*(3/32.0f)*size : -size,
              yoffset = flagblip ? -2*(1 - 3/32.0f)*size : -size,
              dist = dir.magnitude();
        if(dist >= scale*(1 - 0.05f)) dir.mul(scale*(1 - 0.05f)/dist);
        dir.rotate_around_z(-d->yaw*RAD);
        glBegin(GL_QUADS);
        drawradar(x + s*0.5f*(1.0f + dir.x/scale + xoffset), y + s*0.5f*(1.0f + dir.y/scale + yoffset), size*s);
        glEnd();
    }

    int clipconsole(int w, int h)
    {
        return w*6/40;
    }

    void drawhud(fpsent *d, int w, int h)
    {
        if(d->state == CS_ALIVE)
        {
            loopv(flags) if(flags[i].owner == d)
            {
                drawicon(flags[i].team==ctfteamflag(d->team) ? HICON_BLUE_FLAG : HICON_RED_FLAG, HICON_X + 3*HICON_STEP + (d->quadmillis ? HICON_SIZE + HICON_SPACE : 0), HICON_Y);
                break;
            }
        }

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        int x = 1800*w/h*34/40, y = 1800*1/40, s = 1800*w/h*5/40;
        glColor3f(1, 1, 1);
        settexture("packages/hud/radar.png");
        glBegin(GL_QUADS);
        drawradar(float(x), float(y), float(s));
        glEnd();
        loopv(flags)
        {
            flag &f = flags[i];
            if(!ctfflagteam(f.team)) continue;
            drawblips(d, x, y, s, i, false);
            if(f.owner)
            {
                if(lastmillis%1000 >= 500) continue;
            }
            else if(f.droptime && (f.droploc.x < 0 || lastmillis%300 >= 150)) continue;
            drawblips(d, x, y, s, i, true);
        }
        if(d->state == CS_DEAD && !m_protect)
        {
            int wait = respawnwait(d);
            if(wait>=0)
            {
                glPushMatrix();
                glScalef(2, 2, 1);
                bool flash = wait>0 && d==player1 && lastspawnattempt>=d->lastpain && lastmillis < lastspawnattempt+100;
                draw_textf("%s%d", (x+s/2)/2-(wait>=10 ? 28 : 16), (y+s/2)/2-32, flash ? "\f3" : "", wait);
                glPopMatrix();
            }
        }
    }

    void removeplayer(fpsent *d)
    {
        loopv(flags) if(flags[i].owner == d)
        {
            flag &f = flags[i];
            f.interploc.x = -1;
            f.interptime = 0;
            dropflag(i, f.owner->o, f.owner->yaw, 1);
        }
    }

    vec interpflagpos(flag &f, float &angle)
    {
        vec pos = f.owner ? vec(f.owner->abovehead()).add(vec(0, 0, 1)) : (f.droptime ? f.droploc : f.spawnloc);
        angle = f.owner ? f.owner->yaw : (f.droptime ? f.dropangle : f.spawnangle);
        if(pos.x < 0) return pos;
        if(f.interptime && f.interploc.x >= 0)
        {
            float t = min((lastmillis - f.interptime)/500.0f, 1.0f);
            pos.lerp(f.interploc, pos, t);
            angle += (1-t)*(f.interpangle - angle);
        }
        return pos;
    }

    vec interpflagpos(flag &f) { float angle; return interpflagpos(f, angle); }

    void rendergame()
    {
        loopv(flags)
        {
            flag &f = flags[i];
            if(!f.owner && f.droptime && f.droploc.x < 0) continue;
            const char *flagname = f.team==ctfteamflag(player1->team) ? "flags/blue" : "flags/red";
            float angle;
            vec pos = interpflagpos(f, angle);
            rendermodel(!f.droptime && !f.owner ? &f.light : NULL, flagname, ANIM_MAPMODEL|ANIM_LOOP,
                        interpflagpos(f), angle, 0,
                        MDL_DYNSHADOW | MDL_CULL_VFC | MDL_CULL_OCCLUDED | (f.droptime || f.owner ? MDL_LIGHT : 0),
                        NULL, NULL, 0, 0, 0.3f + (f.vistime ? 0.7f*min((lastmillis - f.vistime)/1000.0f, 1.0f) : 0.0f));
        }
    }

    void setup()
    {
        resetflags();
        loopv(entities::ents)
        {
            extentity *e = entities::ents[i];
            if(e->type!=FLAG || e->attr2<1 || e->attr2>2) continue;
            int index = flags.length();
            addflag(index, e->o, e->attr2, m_protect ? 0 : -1000);
            flags[index].spawnangle = e->attr1;
            flags[index].light = e->light;
        }
        vec center(0, 0, 0);
        loopv(flags) center.add(flags[i].spawnloc);
        center.div(flags.length());
        radarscale = 0;
        loopv(flags) radarscale = max(radarscale, 2*center.dist(flags[i].spawnloc));
    }

    void senditems(packetbuf &p)
    {
        putint(p, SV_INITFLAGS);
        putint(p, flags.length());
        loopv(flags)
        {
            flag &f = flags[i];
            putint(p, f.team);
            loopk(3) putint(p, int(f.spawnloc[k]*DMF));
        }
    }

    void parseflags(ucharbuf &p, bool commit)
    {
        loopk(2)
        {
            int score = getint(p);
            if(commit) scores[k] = score;
        }
        int numflags = getint(p);
        loopi(numflags)
        {
            int owner = getint(p), invis = getint(p), dropped = 0;
            vec droploc(0, 0, 0);
            if(owner<0)
            {
                dropped = getint(p);
                if(dropped) loopk(3) droploc[k] = getint(p)/DMF;
            }
            if(commit && flags.inrange(i))
            {
                flag &f = flags[i];
                f.owner = owner>=0 ? (owner==player1->clientnum ? player1 : newclient(owner)) : NULL;
                f.droptime = dropped;
                f.droploc = dropped ? droploc : f.spawnloc;
                f.vistime = invis>0 ? 0 : -1000;
                f.interptime = 0;

                if(dropped)
                {
                    f.droploc.z += 4;
                    if(!droptofloor(f.droploc, 4, 0)) f.droploc = vec(-1, -1, -1);
                }
            }
        }
    }

    void trydropflag()
    {
        if(!m_ctf) return;
        loopv(flags) if(flags[i].owner == player1)
        {
            addmsg(SV_TRYDROPFLAG, "rc", player1);
            return;
        }
    }

    void dropflag(fpsent *d, int i, const vec &droploc)
    {
        if(!flags.inrange(i)) return;
        flag &f = flags[i];
        f.interploc = interpflagpos(f, f.interpangle);
        f.interptime = lastmillis;
        dropflag(i, droploc, d->yaw, 1);
        f.droploc.z += 4;
        d->flagpickup |= 1<<f.id;
        if(!droptofloor(f.droploc, 4, 0))
        {
            f.droploc = vec(-1, -1, -1);
            f.interptime = 0;
        }
        conoutf(CON_GAMEINFO, "%s dropped %s flag", d==player1 ? "you" : colorname(d), f.team==ctfteamflag(player1->team) ? "your" : "the enemy");
        playsound(S_FLAGDROP);
    }

    void flagexplosion(int i, int team, const vec &loc)
    {
        int fcolor;
        vec color;
        if(team==ctfteamflag(player1->team)) { fcolor = 0x2020FF; color = vec(0.25f, 0.25f, 1); }
        else { fcolor = 0x802020; color = vec(1, 0.25f, 0.25f); }
        particle_fireball(loc, 30, PART_EXPLOSION, -1, fcolor, 4.8f);
        adddynlight(loc, 35, color, 900, 100);
        particle_splash(PART_SPARK, 150, 300, loc, 0xB49B4B, 0.24f);
    }

    void flageffect(int i, int team, const vec &from, const vec &to)
    {
        vec fromexp(from), toexp(to);
        if(from.x >= 0)
        {
            fromexp.z += 8;
            flagexplosion(i, team, fromexp);
        }
        if(from==to) return;
        if(to.x >= 0)
        {
            toexp.z += 8;
            flagexplosion(i, team, toexp);
        }
        if(from.x >= 0 && to.x >= 0)
            particle_flare(fromexp, toexp, 600, PART_LIGHTNING, team==ctfteamflag(player1->team) ? 0x2222FF : 0xFF2222, 0.28f);
    }

    void returnflag(fpsent *d, int i)
    {
        if(!flags.inrange(i)) return;
        flag &f = flags[i];
        flageffect(i, f.team, interpflagpos(f), f.spawnloc);
        f.interptime = 0;
        returnflag(i);
        conoutf(CON_GAMEINFO, "%s returned %s flag", d==player1 ? "you" : colorname(d), f.team==ctfteamflag(player1->team) ? "your" : "the enemy");
        playsound(S_FLAGRETURN);
    }

    void resetflag(int i, int team, int score)
    {
        setscore(team, score);
        if(!flags.inrange(i)) return;
        flag &f = flags[i];
        flageffect(i, team, interpflagpos(f), f.spawnloc);
        f.interptime = 0;
        returnflag(i, m_protect ? 0 : -1000);
        conoutf(CON_GAMEINFO, "%s flag reset", f.team==ctfteamflag(player1->team) ? "your" : "the enemy");
        playsound(S_FLAGRESET);
    }

    void scoreflag(fpsent *d, int relay, int goal, int team, int score)
    {
        setscore(team, score);
        if(flags.inrange(goal))
        {
            flag &f = flags[goal];
            if(relay >= 0) flageffect(goal, team, f.spawnloc, flags[relay].spawnloc);
            else flageffect(goal, team, interpflagpos(f), f.spawnloc);
            f.interptime = 0;
            returnflag(relay >= 0 ? relay : goal, relay < 0 ? 0 : -1000);
            d->flagpickup &= ~(1<<f.id);
            if(d->feetpos().dist(f.spawnloc) < FLAGRADIUS) d->flagpickup |= 1<<f.id;
        }
        if(d!=player1)
        {
            defformatstring(ds)("@%d", score);
            particle_text(d->abovehead(), ds, PART_TEXT, 2000, 0x32FF64, 4.0f, -8);
        }
        conoutf(CON_GAMEINFO, "%s scored for %s team", d==player1 ? "you" : colorname(d), team==ctfteamflag(player1->team) ? "your" : "the enemy");
        playsound(S_FLAGSCORE);

        if(score >= FLAGLIMIT) conoutf(CON_GAMEINFO, "%s team captured %d flags", team==ctfteamflag(player1->team) ? "your" : "the enemy", score);
    }

    void takeflag(fpsent *d, int i)
    {
        if(!flags.inrange(i)) return;
        flag &f = flags[i];
        f.interploc = interpflagpos(f, f.interpangle);
        f.interptime = lastmillis;
        conoutf(CON_GAMEINFO, "%s %s %s flag", d==player1 ? "you" : colorname(d), m_protect || f.droptime ? "picked up" : "stole", f.team==ctfteamflag(player1->team) ? "your" : "the enemy");
        ownflag(i, d, lastmillis);
        playsound(S_FLAGPICKUP);
    }

    void invisflag(int i, int invis)
    {
        if(!flags.inrange(i)) return;
        flag &f = flags[i];
        if(invis>0) f.vistime = 0;
        else if(!f.vistime) f.vistime = lastmillis;
    }

    void checkitems(fpsent *d)
    {
        vec o = d->feetpos();
        loopv(flags)
        {
            flag &f = flags[i];
            if(!ctfflagteam(f.team) || f.owner || (f.droptime && f.droploc.x<0)) continue;
            const vec &loc = f.droptime ? f.droploc : f.spawnloc;
            if(o.dist(loc) < FLAGRADIUS)
            {
                if(d->flagpickup&(1<<f.id)) continue;
                if((lookupmaterial(o)&MATF_CLIP) != MAT_GAMECLIP && (lookupmaterial(loc)&MATF_CLIP) != MAT_GAMECLIP)
                    addmsg(SV_TAKEFLAG, "rci", d, i);
                d->flagpickup |= 1<<f.id;
            }
            else d->flagpickup &= ~(1<<f.id);
       }
    }

    void respawned(fpsent *d)
    {
        vec o = d->feetpos();
        d->flagpickup = 0;
        loopv(flags)
        {
            flag &f = flags[i];
            if(!ctfflagteam(f.team) || f.owner || (f.droptime && f.droploc.x<0)) continue;
            if(o.dist(f.droptime ? f.droploc : f.spawnloc) < FLAGRADIUS) d->flagpickup |= 1<<f.id;
       }
    }

    int respawnwait(fpsent *d)
    {
        return m_protect ? 0 : max(0, RESPAWNSECS-(lastmillis-d->lastpain)/1000);
    }

    void pickspawn(fpsent *d)
    {
        findplayerspawn(d, -1, ctfteamflag(d->team));
    }

    const char *prefixnextmap() { return "ctf_"; }

	bool aihomerun(fpsent *d, ai::aistate &b)
	{
		vec pos = d->feetpos();
		loopk(2)
		{
			int goal = -1;
			loopv(flags)
			{
				flag &g = flags[i];
				if(g.team == ctfteamflag(d->team) && (k || (!g.owner && !g.droptime)) &&
					(!flags.inrange(goal) || g.spawnloc.squaredist(pos) < flags[goal].spawnloc.squaredist(pos)))
				{
					goal = i;
				}
			}
			if(flags.inrange(goal) && ai::makeroute(d, b, flags[goal].spawnloc, false))
			{
				d->ai->addstate(ai::AI_S_PURSUE, ai::AI_T_AFFINITY, goal);
				return true;
			}
		}
		return false;
	}

	bool aicheck(fpsent *d, ai::aistate &b)
	{
		if(!m_protect)
		{
			static vector<int> hasflags, takenflags;
			hasflags.setsizenodelete(0);
			takenflags.setsizenodelete(0);
			loopv(flags)
			{
				flag &g = flags[i];
				if(g.owner == d) hasflags.add(i);
				else if(g.team == ctfteamflag(d->team) && ((g.owner && g.team != ctfteamflag(g.owner->team)) || g.droptime))
					takenflags.add(i);
			}
			if(!hasflags.empty())
			{
				aihomerun(d, b);
				return true;
			}
			if(!ai::badhealth(d) && !takenflags.empty())
			{
				int flag = takenflags.length() > 2 ? rnd(takenflags.length()) : 0;
				d->ai->addstate(ai::AI_S_PURSUE, ai::AI_T_AFFINITY, takenflags[flag]);
				return true;
			}
		}
		return false;
	}

	void aifind(fpsent *d, ai::aistate &b, vector<ai::interest> &interests)
	{
		vec pos = d->feetpos();
		loopvj(flags)
		{
			flag &f = flags[j];
			if(!m_protect || f.owner != d)
			{
				static vector<int> targets; // build a list of others who are interested in this
				targets.setsizenodelete(0);
				bool home = f.team == ctfteamflag(d->team);
				ai::checkothers(targets, d, home ? ai::AI_S_DEFEND : ai::AI_S_PURSUE, ai::AI_T_AFFINITY, j, true);
				fpsent *e = NULL;
				loopi(numdynents()) if((e = (fpsent *)iterdynents(i)) && ai::targetable(d, e, false) && !e->ai && !strcmp(d->team, e->team))
				{ // try to guess what non ai are doing
					vec ep = e->feetpos();
					if(targets.find(e->clientnum) < 0 && (ep.squaredist(f.pos()) <= (FLAGRADIUS*FLAGRADIUS*4) || f.owner == e))
						targets.add(e->clientnum);
				}
				if(home)
				{
					bool guard = false;
					if((f.owner && f.team != ctfteamflag(f.owner->team)) || f.droptime || targets.empty()) guard = true;
					else if(d->hasammo(d->ai->weappref))
					{ // see if we can relieve someone who only has a piece of crap
						fpsent *t;
						loopvk(targets) if((t = getclient(targets[k])))
						{
							if((t->ai && !t->hasammo(t->ai->weappref)) || (!t->ai && (t->gunselect == GUN_FIST || t->gunselect == GUN_PISTOL)))
							{
								guard = true;
								break;
							}
						}
					}
					if(guard)
					{ // defend the flag
						ai::interest &n = interests.add();
						n.state = ai::AI_S_DEFEND;
						n.node = ai::closestwaypoint(f.pos(), ai::NEARDIST, true);
						n.target = j;
						n.targtype = ai::AI_T_AFFINITY;
						n.score = pos.squaredist(f.pos())/100.f;
					}
				}
				else
				{
					if(targets.empty())
					{ // attack the flag
						ai::interest &n = interests.add();
						n.state = ai::AI_S_PURSUE;
						n.node = ai::closestwaypoint(f.pos(), ai::NEARDIST, true);
						n.target = j;
						n.targtype = ai::AI_T_AFFINITY;
						n.score = pos.squaredist(f.pos());
					}
					else
					{ // help by defending the attacker
						fpsent *t;
						loopvk(targets) if((t = getclient(targets[k])))
						{
							ai::interest &n = interests.add();
							n.state = ai::AI_S_DEFEND;
							n.node = t->lastnode;
							n.target = t->clientnum;
							n.targtype = ai::AI_T_PLAYER;
							n.score = d->o.squaredist(t->o);
						}
					}
				}
			}
		}
	}

	bool aidefend(fpsent *d, ai::aistate &b)
	{
		if(flags.inrange(b.target))
		{
			flag &f = flags[b.target];
			if(f.droptime && ai::makeroute(d, b, f.pos())) return true;
			if(!m_protect)
			{
				static vector<int> hasflags;
				hasflags.setsizenodelete(0);
				loopv(flags)
				{
					flag &g = flags[i];
					if(g.owner == d) hasflags.add(i);
				}
				if(!hasflags.empty())
				{
					aihomerun(d, b);
					return true;
				}
				if(f.owner && ai::violence(d, b, f.owner, true)) return true;
			}
			else if(f.owner == d) return false; // pop the state and do something else
			int walk = 0;
			if(lastmillis-b.millis >= (201-d->skill)*33)
			{
				static vector<int> targets; // build a list of others who are interested in this
				targets.setsizenodelete(0);
				ai::checkothers(targets, d, ai::AI_S_DEFEND, ai::AI_T_AFFINITY, b.target, true);
				fpsent *e = NULL;
				loopi(numdynents()) if((e = (fpsent *)iterdynents(i)) && ai::targetable(d, e, false) && !e->ai && !strcmp(d->team, e->team))
				{ // try to guess what non ai are doing
					vec ep = e->feetpos();
					if(targets.find(e->clientnum) < 0 && (ep.squaredist(f.pos()) <= (FLAGRADIUS*FLAGRADIUS*4) || f.owner == e))
						targets.add(e->clientnum);
				}
				if(!targets.empty())
				{
					d->ai->clear = true; // re-evaluate so as not to herd
					return true;
				}
				else
				{
					walk = 2;
					b.millis = lastmillis;
				}
			}
			vec pos = d->feetpos();
			float mindist = float(FLAGRADIUS*FLAGRADIUS*8);
			loopv(flags)
			{ // get out of the way of the returnee!
				flag &g = flags[i];
				if(pos.squaredist(g.pos()) <= mindist)
				{
					if(!m_protect && g.owner && !strcmp(g.owner->team, d->team)) walk = 1;
					if(g.droptime && ai::makeroute(d, b, g.pos())) return true;
				}
			}
			return ai::defend(d, b, f.pos(), float(FLAGRADIUS*2), float(FLAGRADIUS*(2+(walk*2))), walk);
		}
		return false;
	}

	bool aipursue(fpsent *d, ai::aistate &b)
	{
		if(flags.inrange(b.target))
		{
			flag &f = flags[b.target];
			if(!m_protect && f.owner && f.owner == d)
			{
				aihomerun(d, b);
				return true;
			}
			if(f.team == ctfteamflag(d->team))
			{
				if(f.droptime && ai::makeroute(d, b, f.pos())) return true;
				if(!m_protect)
				{
					static vector<int> hasflags;
					hasflags.setsizenodelete(0);
					loopv(flags)
					{
						flag &g = flags[i];
						if(g.owner == d) hasflags.add(i);
					}
					if(!hasflags.empty())
					{
						ai::makeroute(d, b, f.spawnloc);
						return true;
					}
					if(f.owner && ai::violence(d, b, f.owner, true)) return true;
				}
				else if(f.owner == d) return false; // pop and do something else
			}
			else
			{
				if(m_protect && f.owner && ai::violence(d, b, f.owner, true)) return true;
				return ai::makeroute(d, b, f.pos());
			}
		}
		return false;
	}
};
#endif

#elif SERVMODE

case SV_TRYDROPFLAG:
{
    if(ci->state.state!=CS_SPECTATOR && cq && smode==&ctfmode) ctfmode.dropflag(cq);
    break;
}

case SV_TAKEFLAG:
{
    int flag = getint(p);
    if(ci->state.state!=CS_SPECTATOR && cq && smode==&ctfmode) ctfmode.takeflag(cq, flag);
    break;
}

case SV_INITFLAGS:
    if(smode==&ctfmode) ctfmode.parseflags(p, (ci->state.state!=CS_SPECTATOR || ci->privilege || ci->local) && !strcmp(ci->clientmap, smapname));
    break;

#else

case SV_INITFLAGS:
{
    ctfmode.parseflags(p, m_ctf);
    break;
}

case SV_DROPFLAG:
{
    int ocn = getint(p), flag = getint(p);
    vec droploc;
    loopk(3) droploc[k] = getint(p)/DMF;
    fpsent *o = ocn==player1->clientnum ? player1 : newclient(ocn);
    if(o && m_ctf) ctfmode.dropflag(o, flag, droploc);
    break;
}

case SV_SCOREFLAG:
{
    int ocn = getint(p), relayflag = getint(p), goalflag = getint(p), team = getint(p), score = getint(p);
    fpsent *o = ocn==player1->clientnum ? player1 : newclient(ocn);
    if(o && m_ctf) ctfmode.scoreflag(o, relayflag, goalflag, team, score);
    break;
}

case SV_RETURNFLAG:
{
    int ocn = getint(p), flag = getint(p);
    fpsent *o = ocn==player1->clientnum ? player1 : newclient(ocn);
    if(o && m_ctf) ctfmode.returnflag(o, flag);
    break;
}

case SV_TAKEFLAG:
{
    int ocn = getint(p), flag = getint(p);
    fpsent *o = ocn==player1->clientnum ? player1 : newclient(ocn);
    if(o && m_ctf) ctfmode.takeflag(o, flag);
    break;
}

case SV_RESETFLAG:
{
    int flag = getint(p), team = getint(p), score = getint(p);
    if(m_ctf) ctfmode.resetflag(flag, team, score);
    break;
}

case SV_INVISFLAG:
{
    int flag = getint(p), invis = getint(p);
    if(m_ctf) ctfmode.invisflag(flag, invis);
    break;
}

#endif


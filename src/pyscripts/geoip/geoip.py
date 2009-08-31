import sbevents, sbserver, sbtools, pygeoip
db = pygeoip.Database('geoip/GeoIP.dat')

def getCountry(ip): 
	 return db.lookup(pygeoip.num_to_addr(ip)).country

def announce(cn):
	sbserver.message(sbtools.orange(sbserver.playerName(cn) + " is connected from " + str(getCountry(sbserver.playerIpLong(cn)))))

def init():
	sbevents.registerEventHandler("player_active", announce)

init()

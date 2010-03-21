db = pygeoip.GeoIP('pygeoip/GeoIP.dat')

def getCountry(ip): 
	country = db.country_name_by_addr(ipLongToString(ip))
	if country == '':
		country = 'Unknown'
	return country


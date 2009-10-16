def ipLongToString(num):
	return '%d.%d.%d.%d' % ((num & 0xff),
		(num >> 8) & 0xff,
		(num >> 16) & 0xff,
		(num >> 24) & 0xff)

def ipStringToLong(st):
	st = st.split('.')
	if len(st) != 4:
		raise ValueError('Not a valid ipv4 address')

	i = int(st[3])
	i = i << 8
	i = i | int(st[2])
	i = i << 8
	i = i | int(st[1])
	i = i << 8
	i = i | int(st[0])
	return i


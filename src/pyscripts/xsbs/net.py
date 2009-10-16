def ipLongToString(num):
	return '%d.%d.%d.%d' % ((num & 0xff),
		(num >> 8) & 0xff,
		(num >> 16) & 0xff,
		(num >> 24) & 0xff)

def ipStringToLong(st):
	st = st.split('.')
	i = 0
	for item in st:
		n = int(item)
		i = i | n
		i << 4
	return i


#!/usr/bin/env python2.5

'''
Pure Python reader for GeoIP Country Edition databases.
'''

__author__ = 'David Wilson <dw@botanicus.net>'


import os
import struct

from cStringIO import StringIO


#
# Constants.
#

# From GeoIP.h.
SEGMENT_RECORD_LENGTH = 3
STANDARD_RECORD_LENGTH = 3
ORG_RECORD_LENGTH = 4
MAX_RECORD_LENGTH = 4
NUM_DB_TYPES = 20

GEOIP_COUNTRY_EDITION     = 1
GEOIP_REGION_EDITION_REV0 = 7
GEOIP_CITY_EDITION_REV0   = 6
GEOIP_ORG_EDITION         = 5
GEOIP_ISP_EDITION         = 4
GEOIP_CITY_EDITION_REV1   = 2
GEOIP_REGION_EDITION_REV1 = 3
GEOIP_PROXY_EDITION       = 8
GEOIP_ASNUM_EDITION       = 9
GEOIP_NETSPEED_EDITION    = 10
GEOIP_DOMAIN_EDITION      = 11
GEOIP_COUNTRY_EDITION_V6  = 12

COUNTRY_BEGIN = 16776960
STATE_BEGIN_REV0 = 16700000
STATE_BEGIN_REV1 = 16000000
STRUCTURE_INFO_MAX_SIZE = 20
DATABASE_INFO_MAX_SIZE = 100

GeoIP_country_code = '''
    AP EU AD AE AF AG AI AL AM AN AO AQ AR AS AT AU AW AZ BA BB BD BE BF BG BH
    BI BJ BM BN BO BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL CM CN CO CR
    CU CV CX CY CZ DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR FX
    GA GB GD GE GF GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID
    IE IL IN IO IQ IR IS IT JM JO JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC
    LI LK LR LS LT LU LV LY MA MC MD MG MH MK ML MM MN MO MP MQ MR MS MT MU MV
    MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM
    PN PR PS PT PW PY QA RE RO RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO
    SR ST SV SY SZ TC TD TF TG TH TJ TK TM TN TO TL TR TT TV TW TZ UA UG UM US
    UY UZ VA VC VE VG VI VN VU WF WS YE YT RS ZA ZM ME ZW A1 A2 O1 AX GG IM JE
    BL MF
'''.split()


#
# Helper functions.
#

def addr_to_num(ip):
    '''
    Convert an IPv4 address from a string to its integer representation.

    @param[in]  ip      IPv4 address as a string.
    @returns            Address as an integer.
    '''

    try:
        w, x, y, z = map(int, ip.split('.'))
        if w>255 or x>255 or y>255 or z>255:
            raise ValueError()
    except ValueError, TypeError:
        raise ValueError('%r is not an IPv4 address.' % (ip,))

    return (w << 24) | (x << 16) | (y << 8) | z


def num_to_addr(num):
    '''
    Convert an IPv4 address from its integer representation to a string.

    @param[in]  num     Address as an integer.
    @returns            IPv4 address as a string.
    '''

    return '%d.%d.%d.%d' % ((num >> 24) & 0xff,
                            (num >> 16) & 0xff,
                            (num >> 8) & 0xff,
                            (num & 0xff))


#
# Classes.
#

class AddressInfo(object):
    '''
    Representation of a database lookup result.
    '''

    __slots__ = [ 'ip', 'ipnum', 'prefix', 'country' ]

    def __init__(self, ip=None, ipnum=None, prefix=None, country=None):
        self.ip = ip
        self.ipnum = ipnum
        self.prefix = prefix
        self.country = country

    network = property(lambda self:
        num_to_addr(self.ipnum & ~((32-self.prefix)**2-1)))

    def __str__(self):
        return '[%s of network %s/%d in country %s]' %\
               (self.ip, self.network, self.prefix, self.country)


class Database(object):
    '''
    GeoIP database reader implementation. Currently only supports country
    edition.
    '''

    def __init__(self, filename):
        '''
        Initialize a new GeoIP reader instance.

        @param[in]  filename    Path to GeoIP.dat as a string.
        '''

        self.filename = filename
        self.cache = file(filename).read()
        self._setup_segments()

        if self.db_type != GEOIP_COUNTRY_EDITION:
            raise NotImplemented('GeoIP.dat is not Country Edition; '
                                 'other editions are not supported yet.')

    def _setup_segments(self):
        self.segments = None

        # default to GeoIP Country Edition
        db_type = GEOIP_COUNTRY_EDITION
        record_length = STANDARD_RECORD_LENGTH

        fp = StringIO(self.cache)
        fp.seek(-31, os.SEEK_END)

        for i in range(STRUCTURE_INFO_MAX_SIZE):
            delim = fp.read(3)

            if delim != '\xFF\xFF\xFF':
                fp.seek(-4, os.SEEK_CUR)
                continue

            db_type = ord(fp.read(1))

            # Region Edition, pre June 2003.
            if db_type == GEOIP_REGION_EDITION_REV0:
                segments = [STATE_BEGIN_REV0]

            # Region Edition, post June 2003.
            elif db_type == GEOIP_REGION_EDITION_REV1:
                segments = [STATE_BEGIN_REV1]

            # City/Org Editions have two segments, read offset of second segment
            elif db_type in (GEOIP_CITY_EDITION_REV0, GEOIP_CITY_EDITION_REV1,
                             GEOIP_ORG_EDITION, GEOIP_ISP_EDITION,
                             GEOIP_ASNUM_EDITION):
                segments = [0]

                for idx, ch in enumerate(fp.read(SEGMENT_RECORD_LENGTH)):
                    segments[0] += ch << (idx * 8)

                if db_type in (GEOIP_ORG_EDITION, GEOIP_ISP_EDITION):
                    record_length = ORG_RECORD_LENGTH

            break

        if db_type in (GEOIP_COUNTRY_EDITION, GEOIP_PROXY_EDITION,
                       GEOIP_NETSPEED_EDITION, GEOIP_COUNTRY_EDITION_V6):
            self.segments = [COUNTRY_BEGIN]

        self.db_type = db_type
        self.record_length = record_length

    def info(self):
        '''
        Return a string describing the loaded database version.

        @returns    English text string, or None if database is ancient.
        '''

        fp = StringIO(self.cache)
        fp.seek(-31, os.SEEK_END)

        hasStructureInfo = False

        # first get past the database structure information
        for i in range(STRUCTURE_INFO_MAX_SIZE):
            if fp.read(3) == '\xFF\xFF\xFF':
                hasStructureInfo = True
                break

            fp.seek(-4, os.SEEK_CUR)

        if hasStructureInfo:
            fp.seek(-6, os.SEEK_CUR)
        else:
            # no structure info, must be pre Sep 2002 database, go back to end.
            fp.seek(-3, os.SEEK_END)

        for i in range(DATABASE_INFO_MAX_SIZE):
            if fp.read(3) == '\0\0\0':
                return fp.read(i)

            fp.seek(-4, os.SEEK_CUR)

    def _decode(self, buf, branch):
        '''
        @param[in]  buf         Record buffer.
        @param[in]  branch      1 for left, 2 for right.
        @returns                X.
        '''

        offset = 3 * branch
        if self.record_length == 3:
            return buf[offset] | (buf[offset+1] << 8) | (buf[offset+2] << 16)

        # General case.
        end = branch * self.record_length
        x = 0

        for j in range(self.record_length):
            x = (x << 8) | buf[end - j]

        return x

    def _seek_record(self, ipnum):
        fp = StringIO(self.cache)
        offset = 0

        for depth in range(31, -1, -1):
            fp.seek(self.record_length * 2 * offset)
            buf = map(ord, fp.read(self.record_length * 2))

            x = self._decode(buf, int(bool(ipnum & (1 << depth))))
            if x >= self.segments[0]:
                return 32 - depth, x

            offset = x

        assert False, \
            "Error Traversing Database for ipnum = %lu: "\
            "Perhaps database is corrupt?" % ipnum


    def lookup(self, ip):
        '''
        Lookup an IP address returning an AddressInfo instance describing its
        location.

        @param[in]  ip      IPv4 address as a string.
        @returns            AddressInfo instance.
        '''

        ipnum = addr_to_num(ip)
        prefix, num = self._seek_record(ipnum)

        num -= COUNTRY_BEGIN
        if num:
            country = GeoIP_country_code[num - 1]
        else:
            country = None

        return AddressInfo(country=country, ip=ip, ipnum=ipnum, prefix=prefix)




if __name__ == '__main__':
    import time

    t1 = time.time()
    db = Database('GeoIP.dat')
    t2 = time.time()

    print db.info()

    t3 = time.time()

    tests = '''
        127.0.0.1
        83.198.135.28
        83.126.35.59
        192.168.1.1
        194.168.1.255
    '''.split()

    for test in tests:
        print db.lookup(test)

    t4 = time.time()

    print "Open: %dms" % ((t2-t1) * 1000,)
    print "Info: %dms" % ((t3-t2) * 1000,)
    print "Lookup: %dms" % ((t4-t3) * 1000,)

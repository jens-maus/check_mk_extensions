#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) 2019 Heinlein Support GmbH
#          Robert Sander <r.sander@heinlein-support.de>

#
# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

def _item_acgateway_mediarealm(i, line):
    return "%s %s" % (i, line[1])

def parse_acgateway_mediarealm(info):
    rowStatus = {
        u'1': u'active',
        u'2': u'notInService',
        u'3': u'notReady',
    }
    sysInterfaceApplicationType = {
        u'0': u'oam',
        u'1': u'media',
        u'2': u'control',
        u'3': u'oamAndMedia',
        u'4': u'oamAndControl',
        u'5': u'mediaAndControl',
        u'6': u'oamAndMediaAndControl',
        u'99': u'maintenance',
        }
    sysInterfaceMode = {
        u'3': u'IPv6PrefixManual',
        u'4': u'IPv6Manual',
        u'10': u'IPv4Manual',
        }
    parsed = {}
    for i, line in enumerate(info[0]):
        item = _item_acgateway_mediarealm(i, line)
        parsed[item] = {u'realmstatus': rowStatus.get(line[0], u'unknown'),
                        u'portrangestart': line[3],
                        u'portrangeend': line[4],
                        u'name': line[1]}
        if line[2].startswith('.1.3.6.1.4.1.5003.9.10.10.1.3.1.30.22.1.11.'):
            idx = int(line[2][43:])
            sysiface = info[1][idx]
            parsed[item].update({u'sysrowstatus': rowStatus.get(sysiface[0], u'unknown'),
                                 u'sysapptype': sysInterfaceApplicationType.get(sysiface[1], u'unknown'),
                                 u'sysmode': sysInterfaceMode.get(sysiface[2], u'unknown'),
                                 u'sysip': "%s/%s" % (sysiface[3], sysiface[4]),
                                 u'sysgateway': sysiface[5],
                                 u'sysvlan': sysiface[6],
                                 u'sysname': sysiface[7]})
            if sysiface[11].startswith('.1.3.6.1.4.1.5003.9.10.10.1.3.1.30.26.1.7.'):
                idx = int(sysiface[11][42:])
                device = info[2][idx]
                parsed[item].update({u'devrowstatus': rowStatus.get(device[0], u'unknown'),
                                     u'devvlan': device[3],
                                     u'devname': device[4]})
    return parsed

def inventory_acgateway_mediarealm(parsed):
    for item, data in parsed.iteritems():
        yield (item, {'realmstatus': data.get('realmstatus'),
                      'sysrowstatus': data.get('sysrowstatus'),
                      'devrowstatus': data.get('devrowstatus')})

def check_acgateway_mediarealm(item, params, parsed):
    if item in parsed:
        data = parsed[item]
        yield 0, 'realm port range %s-%s' % (data[u'portrangestart'], data[u'portrangeend'])
        yield 0, 'system interface %s on device %s' % (data.get(u'sysname'), data.get(u'devname'))
        if u'sysip' in data:
            yield 0, data[u'sysip']
        if u'sysgateway' in data and data[u'sysgateway']:
            yield 0, 'gateway: %s' % data[u'sysgateway']
        for param, value in params.iteritems():
            if value != data.get(param):
                yield 2, '%s is %s(!!)' % (param, data.get(param))

# check_info['acgateway_mediarealm'] = {
#     'parse_function'        : parse_acgateway_mediarealm,
#     'inventory_function'    : inventory_acgateway_mediarealm,
#     'check_function'        : check_acgateway_mediarealm,
#     'service_description'   : 'Media Realm %s',
#     'has_perfdata'          : False,
#     'snmp_info'             : [ ( '.1.3.6.1.4.1.5003.9.10.5.1.1.6.21.1', [ '2',  # 0  AC-CONTROL-MIB::acCPMediaRealmRowStatus
#                                                                             '5',  # 1  AC-CONTROL-MIB::acCPMediaRealmName
#                                                                             '6',  # 2  AC-CONTROL-MIB::acCPMediaRealmIPv4If
#                                                                             '8',  # 3  AC-CONTROL-MIB::acCPMediaRealmPortRangeStart
#                                                                             '10', # 4  AC-CONTROL-MIB::acCPMediaRealmPortRangeEnd
#                                                                           ] ),
#                                 ( '.1.3.6.1.4.1.5003.9.10.10.1.3.1.30.22.1', [ '2',  # 0  AC-SYSTEM-MIB::acSysInterfaceRowStatus
#                                                                                '5',  # 1  AC-SYSTEM-MIB::acSysInterfaceApplicationTypes
#                                                                                '6',  # 2  AC-SYSTEM-MIB::acSysInterfaceMode
#                                                                                '7',  # 3  AC-SYSTEM-MIB::acSysInterfaceIPAddress
#                                                                                '8',  # 4  AC-SYSTEM-MIB::acSysInterfacePrefixLength
#                                                                                '9',  # 5  AC-SYSTEM-MIB::acSysInterfaceGateway
#                                                                                '10', # 6  AC-SYSTEM-MIB::acSysInterfaceVlanID
#                                                                                '11', # 7  AC-SYSTEM-MIB::acSysInterfaceName
#                                                                                '12', # 8  AC-SYSTEM-MIB::acSysInterfacePrimaryDNSServerIPAddress
#                                                                                '13', # 9  AC-SYSTEM-MIB::acSysInterfaceSecondaryDNSServerIPAddress
#                                                                                '14', # 10 AC-SYSTEM-MIB::acSysInterfaceUnderlyingInterface
#                                                                                '15', # 11 AC-SYSTEM-MIB::acSysInterfaceUnderlyingDevice
#                                                                             ] ),
#                                 ( '.1.3.6.1.4.1.5003.9.10.10.1.3.1.30.26.1', [ '2',  # 0  AC-SYSTEM-MIB::acSysEthernetDeviceRowStatus
#                                                                                '3',  # 1  AC-SYSTEM-MIB::acSysEthernetDeviceAction
#                                                                                '4',  # 2  AC-SYSTEM-MIB::acSysEthernetDeviceActionRes
#                                                                                '5',  # 3  AC-SYSTEM-MIB::acSysEthernetDeviceVlanID
#                                                                                '7',  # 4  AC-SYSTEM-MIB::acSysEthernetDeviceName
#                                                                             ] ) ],
#     'snmp_scan_function'    : lambda oid: oid('.1.3.6.1.2.1.1.2.0').startswith('.1.3.6.1.4.1.5003.8.1.1'),
# }

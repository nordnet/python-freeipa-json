# -[python-freeipa-json]-------------------------------------------------------
# This is a very basic quick and dirty way to communicate with FreeIPA/IdM
# without having to install their toolchain, also you do not have to rely on
# kerberos implementations in python.
#
# This sorry excuse for a module have 1 requirement outside of the python
# standard library:
# * requests
#
# Todo:
# - Pull in the rest of the FreeIPA methods
# - Fix the "API version not sent" message
# -----------------------------------------------------------------------------

import requests
import json
import logging

class ipa(object):

    def __init__(self, server, sslverify=False):
        self.server = server
        self.sslverify = sslverify
        self.log = logging.getLogger(__name__)
        self.session = requests.Session()

    def login(self, user, password):
        rv = None
        ipaurl = 'https://{0}/ipa/session/login_password'.format(self.server)
        header = {'referer': ipaurl, 'Content-Type':
                  'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
        login = {'user': user, 'password': password}
        rv = self.session.post(ipaurl, headers=header, data=login,
                               verify=self.sslverify)

        if rv.status_code != 200:
            self.log.warning('Failed to log {0} in to {1}'.format(
                user,
                self.server)
            )
            rv = None
        else:
            self.log.info('Successfully logged in as {0}'.format(user))
            # set login_user for use when changing password for self
            self.login_user = user
        return rv

    def makeReq(self, pdict):
        results = None
        ipaurl = 'https://{0}/ipa'.format(self.server)
        session_url = '{0}/session/json'.format(ipaurl)
        header = {'referer': ipaurl, 'Content-Type': 'application/json',
                  'Accept': 'application/json'}

        data = {'id': 0, 'method': pdict['method'], 'params':
                [pdict['item'], pdict['params']]}

        self.log.debug('Making {0} request to {1}'.format(pdict['method'],
                        session_url))

        request = self.session.post(
                session_url, headers=header,
                data=json.dumps(data),
                verify=self.sslverify
        )
        results = request.json()

        return results

    def config_show(self):
        m = {'method': 'config_show', 'item': [None], 'params': {'all': True}}
        results = self.makeReq(m)

        return results

    def group_add(self, group, description=None):
        m = {'method': 'group_add',
             'item': [group],
             'params': {
                 'all': True,
                 'description': description
             }
        }
        results = self.makeReq(m)

        return results

    def group_add_member(self, group, item, membertype):
        if membertype not in ['user', 'group']:
            raise ValueError('Type {0} is not a valid member type,\
             specify user or group'.format(membertype))
        m = {
                'item': [group],
                'method': 'group_add_member',
                'params': {
                    'all': True,
                    'raw': True,
                    membertype: item
                }
        }
        results = self.makeReq(m)

        return results

    def group_find(self, group=None, sizelimit=40000):
        m = {'method': 'group_find', 'item': [group], 'params': {'all': True,
             'sizelimit': sizelimit}}
        results = self.makeReq(m)

        return results

    def group_show(self, group):
        m = {'item': [group], 'method': 'group_show', 'params':
             {'all': True, 'raw': False}}
        results = self.makeReq(m)

        return results

    def host_add(self, hostname, opasswd, force=True):
        m = {'item': [hostname], 'method': 'host_add', 'params': {'all': True,
             'force': force, 'userpassword': opasswd}}
        results = self.makeReq(m)

        return results

    def host_del(self, hostname):
        m = {'item': [hostname], 'method': 'host_del', 'params': {'all': True}}
        results = self.makeReq(m)

        return results

    def host_find(self, hostname=None, in_hg=None, sizelimit=40000):
        m = {'method': 'host_find', 'item': [hostname], 'params':
             {'all': True, 'in_hostgroup': in_hg, 'sizelimit': sizelimit}}
        results = self.makeReq(m)

        return results

    def host_mod(self, hostname, description=None, locality=None,
                 location=None, platform=None, osver=None):
        m = {'item': [hostname], 'method': 'host_mod', 'params':
             {'all': True, 'description': description, 'locality': locality,
              'nshostlocation': location, 'nshardwareplatform': platform,
              'nsosversion': osver}}
        results = self.makeReq(m)

        return results

    def host_show(self, hostname):
        m = {'item': [hostname], 'method': 'host_show', 'params':
             {'all': True}}
        results = self.makeReq(m)

        return results

    def hostgroup_add(self, hostgroup, description=None):
        m = {
                'method': 'hostgroup_add',
                'item': [hostgroup],
                'params': {
                    'all': True,
                    'description': description
                }
        }
        results = self.makeReq(m)

        return results

    def hostgroup_add_member(self, hostgroup, hostname):
        if type(hostname) != list:
            hostname = [hostname]
        m = {
                'method': 'hostgroup_add_member',
                'item': [hostgroup],
                'params': {'host': hostname, 'all': True}
        }
        results = self.makeReq(m)

        return results

    def hostgroup_show(self, hostgroup):
        m = {'item': [hostgroup], 'method': 'hostgroup_show', 'params':
             {'all': True}}
        results = self.makeReq(m)

        return results

    def passwd(self, principal, passwd):
        item = [principal, passwd]
        if not principal.split('@')[0] == self.login_user:
            item.append('CHANGING_PASSWORD_FOR_ANOTHER_USER')
        m = {'method': 'passwd', 'params': {'version': '2.112'}, 'item': item}
        results = self.makeReq(m)

        return results

    def user_add(self, user, opts):
        opts['all'] = True
        m = {'method': 'user_add', 'item': [user], 'params': opts}
        results = self.makeReq(m)

        return results

    def user_find(self, user=None, attrs={}, sizelimit=40000):
        params = {'all': True,
                  'no_members': False,
                  'sizelimit': sizelimit,
                  'whoami': False}
        params.update(attrs)
        m = {'item': [user], 'method': 'user_find', 'params': params}
        results = self.makeReq(m)

        return results

    def user_show(self, user):
        m = {'item': [user], 'method': 'user_show', 'params':
             {'all': True, 'raw': False}}
        results = self.makeReq(m)

        return results

    def user_status(self, user):
        m = {'item': [user], 'method': 'user_status', 'params':
             {'all': True, 'raw': False}}
        results = self.makeReq(m)

        return results

    def user_unlock(self, user):
        m = {'item': [user], 'method': 'user_unlock', 'params':
             {'version': '2.112'}}
        results = self.makeReq(m)

        return results

    def user_mod(self, user, addattrs=[], setattrs=[], delattrs=[]):
        m = {
            'id': 0,
            'method': 'user_mod',
            'item': [user],
            'params': {
                    'all': False,
                    'no_members': False,
                    'raw': False,
                    'rights': False,
                    'version': '2.164'
            }
        }
        if len(addattrs):
            m['params']['addattr'] = addattrs
        if len(setattrs):
            m['params']['setattr'] = setattrs
        if len(delattrs):
            m['params']['delattr'] = delattrs

        return self.makeReq(m)

    def stageuser_find(self, user=None, attrs={}, sizelimit=40000):
        params = {'all': True,
                  'no_members': False,
                  'sizelimit': sizelimit,
        }
        params.update(attrs)
        m = {'item': [user], 'method': 'stageuser_find', 'params': params}
        results = self.makeReq(m)

        return results

    def stageuser_add(self, user, opts, addattrs=None, setattrs=None):
        opts['all'] = False
        if addattrs is not None:
            opts['addattr'] = addattrs
        if setattrs is not None:
            opts['setattr'] = setattrs
        m = {
            'method': 'stageuser_add',
            'item': [user],
            'params': opts
        }
        results = self.makeReq(m)

        return results

    def stageuser_del(self, user):
        m = {
            'method': 'stageuser_del',
            'item': [user],
            'params': {
                'version': '2.164'
            }
        }
        results = self.makeReq(m)

        return results

    def selfservice_add(self, aciname, attrs, permissions=None):
        m = {
            'method': 'selfservice_add',
            'item': [None],
            'params': {
                'aciname': aciname,
                'attrs': attrs,
                'version': '2.164'
            }
        }
        if permissions is not None:
            m['params']['permissions'] = permissions
        results = self.makeReq(m)

        return results

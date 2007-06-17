#####################################################################
# Copyright (C) 2007 Alex Clemesha <clemesha@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#####################################################################

import twist

def user_type(avatarId):
    if twist.notebook.user_is_admin(avatarId):
        return 'admin'
    return 'user'

import os

from twisted.cred import portal, checkers, credentials, error as credError
from twisted.internet import protocol, defer
from zope.interface import Interface, implements
from twisted.web2 import iweb
from twisted.python import log

class PasswordDataBaseChecker(object):
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.IUsernamePassword,)

    def __init__(self, dbConnection):
        self.dbConnection = dbConnection

    def queryDatabase(self, result):
        if result:
            avatarId = str(result[0][0])
            return avatarId #defer.succeed(avatarId)
        else:
            return checkers.ANONYMOUS #defer.succeed(checkers.ANONYMOUS)

    def requestAvatarId(self, credentials):
        log.msg("=== requestAvatarId ===")
        username = credentials.username
        password = credentials.password
        query = "SELECT avatarId FROM users WHERE avatarId = ? AND password = ?"
        d = self.dbConnection.runQuery(query, (username, password))
        d.addCallback(self.queryDatabase)
        #d.addErrback(self._failed)
        return d

class PasswordDictChecker(object):
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.IUsernamePassword,)

    def __init__(self, passwords):
        "passwords: a dict-like object mapping usernames to passwords"
        self.passwords = passwords

    def requestAvatarId(self, credentials):
        log.msg("=== requestAvatarId ===")
        username = credentials.username
        #log.msg("un: %s, pw: %s"%(credentials.username, credentials.password))
        if self.passwords.has_key(username):
            log.msg("password.has_key(%s)"%username)
            password = self.passwords[username]
            if credentials.password == password:
                return defer.succeed(username)
            else:
                log.msg("=== %s entered the wrong password" % username)
                log.msg("=== Returning anonymous credentials.")
                return defer.succeed(checkers.ANONYMOUS)
        else:
            log.msg("=== Returning anonymous credentials.")
            return defer.succeed(checkers.ANONYMOUS)
            #return defer.fail(credError.UnauthorizedLogin("No such user"))

class PasswordFileChecker(PasswordDictChecker):
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.IUsernamePassword,)

    def __init__(self, password_file):
        """
        INPUT:
        password_file - file that contains passwords

        """
        if not os.path.exists(password_file):
            open(password_file,'w').close()
        f = open(password_file).readlines()
        passwords = {'a':'a', 'was':'a', 'admin':'a'}
        for line in f:
            username, password = line.split(':')
            password = password.strip()
            passwords[username] = password

        self.passwords = passwords

class LoginSystem(object):
    implements(portal.IRealm)

    def __init__(self, users):
        self.users = users #empty, stored in database right now
        # self.dbConnection = dbConnection
        self.usersResources = {} #store created resource objects
        self.kernels = {} #logged in users kernel connections.
        self.logout = lambda: None #find a good use for logout

    def requestAvatar(self, avatarId, mind, *interfaces):
        """Return a given Avatar depending on the avatarID.

        This approximatly boils down to, for a protected web site,
        that given a username (avatarId, which could just be '()' for
        an anonymous user) returned from a login page,
        (which first went through a password check in requestAvatarId)
        We serve up a given "web site" -> twisted resources, that depends
        on the avatarId, (i.e. different permissions / view depending on
        if the user is anonymous, regular, or an admin)
        """
        from sage.server.notebook.twist import AnonymousToplevel, UserToplevel, AdminToplevel
        log.msg("=== requestAvatar ===")
        self.cookie = mind[0]
        if iweb.IResource in interfaces:
            if avatarId is checkers.ANONYMOUS: #anonymous user

                log.msg("returning AnonymousResources")
                rsrc = AnonymousToplevel(self.cookie, avatarId)
                return (iweb.IResource, rsrc, self.logout)

            elif user_type(avatarId) == 'user':

                log.msg("returning User resources for %s" % avatarId)
                self._mind = mind #mind = [cookie, request.args, segments]
                self._avatarId = avatarId
                rsrc = UserToplevel(self.cookie, avatarId)
                return (iweb.IResource, rsrc, self.logout)

            elif user_type(avatarId) == 'admin':

                self._mind = mind #mind = [cookie, request.args, segments]
                self._avatarId = avatarId
                rsrc = AdminToplevel(self.cookie, avatarId)
                return (iweb.IResource, rsrc, self.logout)

        else:
            raise KeyError("None of the requested interfaces is supported")

    def getUserResource(self, result):
        ktype = str(result[0][0])
        kernelConnection = self.kernels[self.nbid] = kernel.KernelManager(ktype)
        rsrc = resources.Root(self._avatarId, self.cookie, kernelConnection, self.dbConnection)
        return (iweb.IResource, rsrc, self.logout)

from Products.PlonePAS.tools.membersip import MembershipTool


def testCurrentPassword(self, password):
    """ test to see if password is current """
    request = getattr(self, 'REQUEST', {})
    userid = self.getAuthenticatedMember().getUserId()
    acl_users = self._findUsersAclHome(userid)
    if not acl_users:
        return 0
    user = acl_users.getUserById(userid)
    if not user:
        return 0
    username = user.getUserName()
    return acl_users.authenticate(username, password, request)


MembershipTool.testCurrentPassword = testCurrentPassword

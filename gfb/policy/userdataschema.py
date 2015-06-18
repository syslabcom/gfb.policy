# -*- coding: utf-8 -*-
from plone.app.users.userdataschema import (
    IUserDataSchemaProvider as IBaseUserDataSchemaProvider)
from plone.app.users.userdataschema import (
    IUserDataSchema as IBaseUserDataSchema)
from plone.app.users.browser.personalpreferences import(
    UserDataPanelAdapter as BaseUserDataPanelAdapter)
from zope import schema
from zope.interface import implements


class IUserDataSchemaProvider(IBaseUserDataSchemaProvider):
    """
    """

    def getSchema():
        """
        """


class UserDataSchemaProvider(object):
    implements(IUserDataSchemaProvider)

    def getSchema(self):
        """
        """
        return IUserDataSchema


class IUserDataSchema(IBaseUserDataSchema):

    is_expert_author = schema.Bool(
        title=u"Ist der Nutzer ein Autor für den Bereich Expertenwissen?",
        required=False,
        default=False,
    )


class UserDataPanelAdapter(BaseUserDataPanelAdapter):

    def get_is_expert_author(self):
        return self._getProperty('is_expert_author')

    def set_is_expert_author(self, value):
        return self.context.setMemberProperties({'is_expert_author': value})

    is_expert_author = property(get_is_expert_author, set_is_expert_author)

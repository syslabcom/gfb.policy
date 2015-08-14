# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode


def logit(*kwargs):
    " log something from the web "
    try:
        mesg = ''
        for kwarg in kwargs:
            mesg += str(kwarg) + ' '
        print mesg
    except:
        print [kwargs]


def handle_checkin(obj, event):
    host = getToolByName(obj, 'MailHost')

    portal = getToolByName(obj, 'portal_url').getPortalObject()

    send_from_address = portal.getProperty('email_from_address')
    send_to_address = portal.portal_properties.site_properties.getProperty(
        'external_editor_address', send_from_address)

    obj_url = event.baseline.absolute_url()
    subject = "GFB: Artikel mit Änderungen wurde veröffentlicht"
    message = (
        u'Der Artikel "%(title)s" wurde neu veröffentlicht, mit folgendem '
        u'Kommentar:\n%(comment)s\n\nDie Adresse lautet:\n%(url)s.\nHier '
        u'können Sie sich die Änderungen anzeigen lassen:\n%(history)s' % dict(
            title=safe_unicode(obj.Title()),
            history=u"{0}/@@historyview".format(safe_unicode(obj_url)),
            comment=safe_unicode(event.message),
            url=safe_unicode(obj_url)))

    encoding = portal.getProperty('email_charset')
    msg_type = 'text/plain'

    envelope_from = send_from_address

    host.send(
        message, mto=send_to_address, mfrom=envelope_from,
        subject=subject, msg_type=msg_type, charset=encoding
    )

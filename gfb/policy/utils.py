# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from plone.protect.utils import addTokenToUrl
from zope.component import getMultiAdapter


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

    rt = getToolByName(obj, "portal_repository", None)
    history = rt.getHistoryMetadata(event.baseline)
    num = int(history.getLength(countPurged=False))
    if num > 0:
        num = num - 1

    pm = getToolByName(portal, 'portal_membership')
    user = pm.getAuthenticatedMember()
    cnt = num
    username = usermail = None
    while cnt >= 0:
        try:
            data = history.retrieve(cnt)
            principal = data['metadata']['sys_metadata']['principal']
            if principal != user.id :
                actor = pm.getMemberById(principal)
                username = safe_unicode(actor.getProperty('fullname'))
                usermail = safe_unicode(actor.getProperty('email'))
                break
        except:
            pass
        cnt = cnt - 1

    obj_url = event.baseline.absolute_url()
    title = safe_unicode(event.baseline.Title())
    folder_title = safe_unicode(aq_parent(event.baseline).Title())
    subject = u'GFB: Artikel "{0}" aus Rubrik "{1}" wurde veröffentlicht'.format(
        title, folder_title)
    history_url = u"{0}/@@history?one=current&two={1}".format(
        safe_unicode(obj_url), num)
    history_url = addTokenToUrl(history_url)

    note = u""
    if username:
        note = u'\nDie letzte Änderung wurde von "%(name)s" durchgeführt.\n\n' % dict(
            name=username)
    message = (
        u'Der Artikel "%(title)s" aus Rubrik "%(rubrik)s" wurde neu '
        u'veröffentlicht, mit folgendem Kommentar:\n%(comment)s\n%(note)s'
        u'\nDie Adresse lautet:\n%(url)s.\nHier '
        u'können Sie sich die Änderungen anzeigen lassen:\n%(history)s' % dict(
            title=safe_unicode(obj.Title()),
            rubrik=folder_title,
            note=note,
            history=history_url,
            comment=safe_unicode(event.message),
            url=safe_unicode(obj_url)))

    encoding = portal.getProperty('email_charset')
    msg_type = 'text/plain'

    envelope_from = send_from_address

    host.send(
        message, mto=send_to_address, mfrom=envelope_from,
        subject=subject, msg_type=msg_type, charset=encoding
    )
    if usermail:
        host.send(
            message, mto=usermail, mfrom=envelope_from,
            subject=subject, msg_type=msg_type, charset=encoding
        )

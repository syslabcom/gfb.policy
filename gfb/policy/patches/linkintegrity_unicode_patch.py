from plone.app.linkintegrity import parser
from plone.app.linkintegrity.parser import LinkParser
from HTMLParser import HTMLParseError
from Products.CMFPlone.utils import safe_unicode


def extractLinks(data):
    """ parse the given html and return all links """
    if not data:
        return []
    parser = LinkParser()
    data = safe_unicode(data)
    try:
        parser.feed(data)
        parser.close()
    except (HTMLParseError, TypeError):
        pass
    return parser.getLinks()


parser.extractLinks = extractLinks

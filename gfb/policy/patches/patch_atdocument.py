from Products.ATContentTypes.content.document import ATDocument
from Products.CMFPlone.utils import safe_unicode
from gfb.policy.BeautifulSoup import BeautifulSoup

orig_processForm = ATDocument.processForm


def processForm(self, data=1, metadata=0, REQUEST=None, values=None):
    REQUEST = REQUEST or self.REQUEST
    bs = BeautifulSoup(
        safe_unicode(REQUEST.get('text', '')), convertEntities='html')
    REQUEST.form['text'] = bs.renderContents('utf-8').replace('\xc2\xa0', '&nbsp;')
    orig_processForm(self, data, metadata, REQUEST, values)

ATDocument.processForm = processForm

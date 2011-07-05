from zope.interface import implements
from gfb.policy.interfaces import IVocabularyUtility
from Products.CMFCore.utils import getToolByName
from zope.site.hooks import getSite

class ProviderVocabularyUtility(object):
    implements(IVocabularyUtility)

    def _validProviders(self):
        # switch: if the current user has Manager rights, show ALL Provider objects,
        # else filter to those that are assigned to at least one data object (RiskAssessmentLink)
        context = getSite()
        pc = getToolByName(context, 'portal_catalog')
        if context.portal_membership.getAuthenticatedMember().allowed(context, ['Manager']):
            provRes = pc(portal_type='Provider')
        else:
            rc = getToolByName(context, 'reference_catalog')
            res = rc(relationship='provider_of')
            uids = set()
            for r in res:
                uids.add(r.targetUID)
            
            provRes = pc(UID = list(uids))
        return provRes

    def getVocabularyDict(self):
        """Build vocabulary dict
        """
        context = getSite()
        provRes = self._validProviders()
        plt = getToolByName(context, 'portal_languages')
        lang = plt.getPreferredLanguage()
        pvt = getToolByName(context, 'portal_vocabularies')
        VOCAB = pvt.get('provider_category')
        results = dict()
        if VOCAB:
            DL =VOCAB.getDisplayList(context)
            cats = DL.keys()
            for catId, catName in DL.items():
                results[catId] = (catName, dict())
            for res in provRes:
                if res.Language != lang:
                    try:
                        ob = res.getObject()
                    except:
                        # stale catalog entry
                        continue
                    ob = ob.getTranslation(lang) or ob
                    title = ob.Title()
                else:
                    title = res.Title
                if res.getProvider_category in cats:
                    results[res.getProvider_category][1][res.UID] = (title, None)
        else:
            for res in provRes:
                results[res.UID] = (res.Title, None)
        return results

        

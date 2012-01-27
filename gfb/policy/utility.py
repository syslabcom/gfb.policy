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
        plt = getToolByName(context, 'portal_languages')
        lang = plt.getPreferredLanguage()
        deflang = plt.getDefaultLanguage()
        if context.portal_membership.getAuthenticatedMember().allowed(context, ['Manager']):
            provRes = pc(portal_type='Provider', Language=lang)
        else:
            rc = getToolByName(context, 'reference_catalog')
            res = rc(relationship='provider_of')
            uids = set()
            for r in res:
                uids.add(r.targetUID)
            provRes = pc(UID = list(uids), Language=deflang)
            # if we are not dealing with the canonical language, we need to
            # find all available translations, and keep the canonicals if no
            # translation is present. Then do a second catalog query
            if lang!=deflang:
                uids = set()
                for prov in provRes:
                    obj = prov.getObject()
                    obj = obj.getTranslation(lang) or obj
                    uids.add(obj.UID())
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



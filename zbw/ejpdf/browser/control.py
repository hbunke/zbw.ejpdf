# -*- coding: UTF-8 -*-

# Hendrik Bunke <h.bunke@zbw.eu>
# German National Library of Economics (ZBW)
# http://zbw.eu/

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations
from toolz.itertoolz import first, get
from operator import truth


class View(BrowserView):
    """
    control panel for cover generation
    """

    template = ViewPageTemplateFile("control.pt")

    def __call__(self):
        return self.template()
    
    def annotations(self):
        """
        get zbw.coverdata annotations
        """
        ann = IAnnotations(self.context)
        data = ann.get('zbw.coverdata', {})
        
        # make sure that all necessary keys are in annotations; some
        # annotations are from an earlier dev stage
        keys = ['keywords',
                'additional',
                'authors',
                "date_submission",
                "date_accepted_as_dp",
                "date_published_as_dp",
                "date_revised",
                "date_accepted_as_ja",
                "date_published_as_ja",
                ]
        
        dic = {k: data.get(k) for k in keys if k in data}
        return dic or dict(authors=[])

    def authors(self):
        """
        return list of dicts with fullname, affiliation, email; mark
        corresponding author
        """
        anna = self.annotations()['authors']
       
        def author_dict(i):
            catalog = getToolByName(self.context, "portal_catalog")
            obj = first(catalog(id=i)).getObject()
            name = "{} {}".format(obj.getFirstname(), obj.getSurname())
               
            def aff(d):
                return i == d.get('author_id', None) and d.get('affil', None)

            def corresponding_author():
                ca = lambda a: a['corresponding'] is True
                return first(filter(ca, anna))['author_id'] == i
                
            corresponding = anna and corresponding_author()
            affil = get(0, filter(truth, map(aff, anna)), None) or obj.getOrganisation()

            return {'author_id': obj.getId(), 'name': name, 'affil': affil,
                    'email': obj.getEmail(), 'corresponding': corresponding}
        
        authors = map(author_dict, self.context.getAuthors())
        
        if not any(a['corresponding'] for a in authors):
            first(authors).update({'corresponding': True})
        
        return authors


    

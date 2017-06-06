# -*- coding: UTF-8 -*-

# Hendrik Bunke <h.bunke@zbw.eu>
# German National Library of Economics (ZBW)
# http://zbw.eu/

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations
from toolz.itertoolz import first
from toolz.dicttoolz import valfilter


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
        key = 'zbw.coverdata'
        if key in ann:
            data = ann[key]
            d = {}
            
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

            for k in keys:
                if k in data:
                    d[k] = data[k]
                else:
                    d[k] = False
            return d
        
        # all other missing annotations are catched by the template
        return dict(authors=False)

    def authors(self):
        """
        returns dicts with fullname, affiliation, email, and marks
        corresponding author
        """
        ann = IAnnotations(self.context)
        key = 'zbw.coverdata'
        anna = self.annotations()['authors']
       
        def author_dict(i):
            catalog = getToolByName(self.context, "portal_catalog")
            obj = first(catalog(id=i)).getObject()
            name = "{} {}".format(obj.getFirstname(), obj.getSurname())
               
            # XXX workaround for a strange bug
            # try:
                # dic = ann[key]['authors']
                # for d in dic:
                    # if i == d['author_id']:
                        # affil = d['affil']
            # except:
                # pass
            
            def aff(d):
                affil = obj.getOrganisation()
                fd = valfilter(dic, lambda v: i == v) 
                

                if i == d.get('author_id', None):
                    affil = d.get('affil', None)
                return affil

            
            dic = ann[key]['authors'] or {}
            affil = first(map(aff, dic))

            author_id = obj.getId()
            email = obj.getEmail()
            corresponding = anna and corresponding_author(i) or False

            return {'author_id': author_id, 'name': name, 'affil': affil,
                    'email': email, 'corresponding': corresponding}
        
        
        def corresponding_author(i):
            ca = lambda a: a['corresponding'] is True
            return first(filter(ca, anna))['author_id'] == i
            
        authors = map(author_dict, self.context.getAuthors())
        
        if not any(a['corresponding'] for a in authors):
            first(authors)['corresponding'] = True

        return authors


    


    

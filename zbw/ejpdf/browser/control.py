# -*- coding: UTF-8 -*-

# Dr. Hendrik Bunke <h.bunke@zbw.eu>
# German National Library of Economics (ZBW)
# http://zbw.eu/

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations


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
            
            #make sure that all necessary keys are in annotations; some
            #annotations are from an earlier dev stage
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
        
        #all other missing annotations are catched by the template
        return dict(
                authors = False)


    def authors(self):
        """
        returns dicts with fullname, affiliation, email and marks
        corresponding author
        """
        ann = IAnnotations(self.context)
        key = 'zbw.coverdata'
        
        author_id_list = self.context.getAuthors()
        authors = []
        catalog = getToolByName(self.context, "portal_catalog")
        for i in author_id_list:
            brains = catalog(id=i)
            for brain in brains:
                obj = brain.getObject()
                surname = brain.getSurname
                firstname = obj.getFirstname()
                name = "%s %s" %(firstname, surname)
               
                try:
                    dic = ann[key]['authors']
                    for d in dic:
                        if i == d['author_id']:
                            affil = d['affil']
                except:
                    affil = obj.getOrganisation()
                
                author_id = obj.getId()
                email = obj.getEmail()
                author = {'author_id' : author_id, 'name' : name, 'affil' : affil,
                        'email' : email, 'corresponding' : False}
                authors.append(author)
        
        #set to the corresponding author
        corr = self.__corresponding_author()
        if corr is not False:
            for author in authors:
                if author['name'] == corr:
                    author['corresponding'] = True
        else:
            authors[0]['corresponding'] = True

        return authors


    def __corresponding_author(self):
        """
        helper method. checks for corresponding author in annotation and
        returns either name or False
        """
        ann = self.annotations()
        if ann['authors'] is False:
            return False
        for author in ann['authors']:
            if author['corresponding'] is True:
                return author['name']
            
    


    

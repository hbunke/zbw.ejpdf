# -*- coding: UTF-8 -*-

# Dr. Hendrik Bunke <h.bunke@zbw.eu>
# German National Library of Economics (ZBW)
# http://zbw.eu/

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.utils import DT2dt
#from datetime import date
from zbw.ejpdf.interfaces import ICover
from zope.interface import Interface
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
            keywords = data['keywords']
            correspondence = data['correspondence']
            #email = data['correspondence_email']
            additional = data['additional']
            return dict(
                    keywords = keywords,
                    correspondence = correspondence,
                    additional = additional)
        return dict(
                keywords = u"",
                correspondence = u"",
                additional = u"")


    def authors(self):
        """
        returns dicts with fullname and affiliation
        """
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
                affil = obj.getOrganisation()
                author_id = obj.getId()
                author = {'id' : author_id, 'name' : name, 'affil' : affil}
                authors.append(author)
        return authors

   

    

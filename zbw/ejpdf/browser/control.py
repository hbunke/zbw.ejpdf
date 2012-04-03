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
            email = data['correspondence_email']
            additional = data['additional']
            return dict(
                    keywords = keywords,
                    correspondence = correspondence,
                    email = email,
                    additional = additional)
        return dict(
                keywords = "",
                correspondence = "",
                email = "",
                additional = "")
        




    

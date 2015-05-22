# -*- coding: UTF-8 -*-

# Dr. Hendrik Bunke <h.bunke@zbw.eu>
# German National Library of Economics (ZBW)
# http://zbw.eu/

from Products.Five.browser import BrowserView
from zbw.ejpdf.interfaces import ICover, ICoverAnnotation
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from zbw.ejpdf.interfaces import ICoverSettings


class View(BrowserView):
    """
    generates and shows cover PDF
    """

    def __call__(self):
        """
        """
        
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)
        #first store additional data from request
        store = ICoverAnnotation(self.context)
        pdf = ICover(self.context)
        pdfname = "cover.{}.{}.pdf".format(self.context.portal_type,
                self.context.getId())
        self.context.REQUEST.RESPONSE.setHeader('Content-Type', 'application/pdf')
        pdf = "{}/{}".format(settings.pdf_url, pdfname)
        #import pdb; pdb.set_trace()
        self.context.REQUEST.RESPONSE.redirect(pdf)
           

    

    

# -*- coding: UTF-8 -*-

# Dr. Hendrik Bunke <h.bunke@zbw.eu>
# German National Library of Economics (ZBW)
# http://zbw.eu/

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.utils import DT2dt
#from datetime import date
from BeautifulSoup import BeautifulSoup
from zbw.ejpdf.interfaces import ICover
from zope.interface import Interface



class IView(Interface):
    
    def publish_date():
        """
        """
    
    def clean_abstract():
        """
        """

    def portal_type():
        """
        """

    def authors():
        """
        """

    

class View(BrowserView):
    """
    view for xml generation for coverpage with rel. data
    """

    template = ViewPageTemplateFile("cover.pt")

    def __call__(self):
        self.request.RESPONSE.setHeader('Content-Type', 'text/xml')
        return self.template()


    def publish_date(self):
        """
        returns date in format Month dayNumber, Year
        """
        obj = self.context
        #import pdb; pdb.set_trace()
        obj_date = DT2dt(self.context.created())
        obj_date = obj_date.strftime("%B %d, %Y")
        return obj_date

    
    def clean_abstract(self):
        """
        """
        html = self.context.getAbstract()
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)

        return unicode(soup)

    def portal_type(self):
        """
        returns proper portal type
        """
        pt = self.context.portal_type
        if pt == "DiscussionPaper":
            pt = "Discussion Paper"
        if pt == "JournalPaper":
            pt = "Journal Article"

        return pt

    
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
                author = {'name' : name, 'affil' : affil}
                authors.append(author)

        return authors



class PdfView(BrowserView):
    """
    generates and shows pdf
    """

    def __call__(self):
        pdf = ICover(self.context)
        pdf = pdf.generate()
        pdfname = "cover.%s.%s.pdf" %(self.context.portal_type,
                self.context.getId())
        if pdf:
            self.context.REQUEST.RESPONSE.setHeader('Content-Type', 'application/pdf')
            
            #XXX change URL 
            pdf = "http://localhost:12000/%s" %pdfname
            #import pdb; pdb.set_trace()
            self.context.REQUEST.RESPONSE.redirect(pdf)
        else:
            return "oops, something went wrong"
           



    


    

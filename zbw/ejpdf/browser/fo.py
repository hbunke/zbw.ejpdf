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
from zbw.ejpdf.interfaces import ICover, ICoverAnnotation
from zope.interface import Interface
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter, getUtility
from plone.registry.interfaces import IRegistry
from zbw.ejpdf.interfaces import ICoverSettings


class IView(Interface):

    def publish_date():
        """
        """

    def get_publish_year():
        """
        """


class View(BrowserView):

    template = ViewPageTemplateFile("fo.pt")

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


    def get_publish_year(self):
        """
        returns year of creation date
        """
        obj = self.context
        #import pdb; pdb.set_trace()
        obj_date = DT2dt(self.context.created())
        obj_date = obj_date.strftime("%Y")
        return obj_date


    def uri(self):
        """
        """
        pt = self.context.portal_type
        if pt == "DiscussionPaper":
            uri = self.context.absolute_url()
        if pt == "JournalPaper":
            uri = "http://dx.doi.org/10.5018/economics-ejournal.ja.%s" %self.context.getId()
        return uri


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


    def clean_abstract(self):
        """
        """
        html = self.context.getAbstract()
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        soup = soup.findAll('p')
        #return unicode(soup)
        return soup


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
            additional = data['additional']
            authors = data['authors']
            return dict(
                    keywords = keywords,
                    correspondence = correspondence,
                    additional = additional,
                    authors = authors)
        return dict(
                keywords = "",
                correspondence = "",
                additional = "",
                authors = authors)


    def citation_string(self):
        """
        generates citation string
        """
        paper_view = getMultiAdapter((self.context, self.request),
                name="paperView")
        
        text = u""
        
        text += unicode(paper_view.authors_as_string(), 'utf-8')
        pt = self.context.portal_type
        if pt == "JournalPaper":
            type_view = getMultiAdapter((self.context, self.request), name="ja_view")
            version = type_view.last_version_info()
            doi_url = "http://dx.doi.org/%s" %type_view.get_doi()
            text += " (%s). " %type_view.pubyear()
            text += unicode(self.context.Title(), 'utf-8')
            text += ".  Economics: The Open-Access, Open-Assessment E-Journal, "
            text += "Vol. %s, %s" %(type_view.get_volume(), self.context.getId())
            if version and version['number'] > 1:
               text += "(Version %s)" %version['number']
            text += ". %s" %doi_url
        
        if pt == "DiscussionPaper":
            type_view = getMultiAdapter((self.context, self.request), name="dp_view")
            url = self.context.absolute_url()
            text += unicode(type_view.cite_as(), 'utf-8')
            text += " %s" %url

        return text

    def is_last_author(self, author):
        """
        """
        authors = self.authors()
        if not author == authors[-1]:
            return True
        return False



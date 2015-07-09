# -*- coding: UTF-8 -*-

# Dr. Hendrik Bunke <h.bunke@zbw.eu>
# German National Library of Economics (ZBW)
# http://zbw.eu/

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.utils import DT2dt
from BeautifulSoup import BeautifulSoup
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from datetime import datetime
from xml.sax.saxutils import escape
from operator import itemgetter

class View(BrowserView):

    template = ViewPageTemplateFile("fo.pt")
    


    def __call__(self):
        self.request.RESPONSE.setHeader('Content-Type', 'text/xml')
        return self.template()

    def __get_obj_date(self):
        """
        necessary because unpublished paper do not have created(). In that case
        modified() is returned
        """

        date = self.context.created()
        if date is None:
            date = self.context.modified()
        return date


    def publish_date(self):
        """
        returns date in format Month dayNumber, Year
        """
        #import pdb; pdb.set_trace()
        obj_date = DT2dt(self.__get_obj_date())
        obj_date = obj_date.strftime("%B %d, %Y")
        return obj_date


    def get_publish_year(self):
        """
        returns year of creation date
        """
        obj = self.context
        obj_date = DT2dt(self.__get_obj_date())
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
    
    

    def clean_abstract(self):
        """
        """
        html = self.context.getAbstract()
        
        #tags we don't need BeautifulSoup for. KISS!
        abstract = html.replace('<br />', '')
        
        soup = BeautifulSoup(abstract, convertEntities=BeautifulSoup.HTML_ENTITIES)
        
        #replacing html <p> with fo <fo:block>
        while True:
            p = soup.find('p')
            if not p:
                break
            p.name = 'fo:block'
            del p['style']
            del p['align']
            del p['class']
            
            p['text-align'] = 'justify'
            p['space-after'] = '6px'
            p['language'] = 'en'
            p['hyphenate'] = 'false'
        
        #replacing sub 
        while True:
            sub = soup.find('sub')
            if not sub:
                break
            sub.name = 'fo:inline'
            sub['baseline-shift'] = 'sub'
            sub['font-size'] = '80%'

        #replacing sup
        while True:
            sup = soup.find('sup')
            if not sup:
                break
            sup.name = 'fo:inline'
            sup['baseline-shift'] = 'sup'
            sup['font-size'] = '80%'
        
        while True:
            em = soup.find('em')
            if not em:
                break
            em.name = 'fo:inline'
            em['font-style'] = 'italic'

        while True:
            span = soup.find('span')
            if not span:
                break
            span.name = 'fo:inline'


        # removing <a> tags without tag content
        links = soup.findAll('a')
        for l in links:
            l.replaceWithChildren()
        
        return unicode(soup)


    def annotations(self):
        """
        get zbw.coverdata annotations
        """

        ann = IAnnotations(self.context)
        coverdata = ann['zbw.coverdata']
        return coverdata


    def citation_string(self):
        """
        generates citation string
        """
        paper_view = getMultiAdapter((self.context, self.request),
                name="paperView")
        
        date = datetime.now()

        text = u""
        

        text += unicode(paper_view.authors_as_string(), 'utf-8')
        pt = self.context.portal_type
        if pt == "JournalPaper":
            type_view = getMultiAdapter((self.context, self.request), name="ja_view")
            version = type_view.last_version_info()
            doi_url = "http://dx.doi.org/%s" %type_view.get_doi()
            
            #we must use the actual year here, since private papers don't have
            #a publish date
            #text += " (%s). " %type_view.pubyear()
            text += " (%s). " %date.year

            title = self.escape_title()
            text += unicode(title, 'utf-8')
            
            signs = ('?', '!', '.')
            if not text.endswith(signs):
                text += "."
            text += " <fo:inline font-style='italic'>Economics: The Open-Access, Open-Assessment E-Journal</fo:inline>, "
            text += "%s (%s)" %(type_view.get_volume(), self.context.getId())
            
            if self.context.getPages():
                pages = self.context.getPages()
                text += u": 1—%s" %pages

            if version and version['number'] > 1:
               text += "(Version %s)" %version['number']
            text += ". %s" %doi_url
        
        if pt == "DiscussionPaper":
            type_view = getMultiAdapter((self.context, self.request), name="dp_view")
            url = self.context.absolute_url()
            
            citation = escape(type_view.cite_as())

            text += unicode(citation, 'utf-8')
            text = text.replace(u"Not published yet", unicode(date.year))
            text += " %s" %url
        return text


    def authors(self):
        """
        returns dicts with fullname and affiliation
        """
        catalog = getToolByName(self.context, "portal_catalog")
        
        brains = map(lambda author_id: itemgetter(0)(catalog(id=author_id)),
                self.context.getAuthors())
        
        authors = map(lambda brain: dict(
            author_id = brain.getObject().getId(),
            name = '{} {}'.format(brain.getObject().getFirstname(), brain.getSurname),
            affil = brain.getObject().getOrganisation()
            ), brains)
        
        return authors


    def authors_as_string(self):
        """
        """
        
        return map(lambda author: self._authors_concat_string(author,
                    self.authors()), self.authors())

    

    def _authors_concat_string(self, author, authors):
        """
        """
        nr = len(authors)
        if nr <= 1:
            return author['name']

        if nr == 2:
            if authors[-1] == author:
                return author['name']
            #this is actually quite ugly. It relies on XSL-FO to produce the 
            #necessary whitespace after 'and'. We had double-whitespace when 
            #returning "and "    
            return "%s and" %author['name'] 

        if nr > 2:
            if authors[-1] == author:
                return "and %s" %author['name']
            return "%s,"%author['name']
        return None




    def get_volume(self):
        """
        returns Volume number of Journalarticle according to creation date
        """
        cyear = int(self.__get_obj_date().strftime('%Y'))
        startyear = 2007
        vol = cyear - startyear +1
        return vol

     
    def special_issue(self):
        """
        checks if paper has been published in Special Issue
        """
        obj = self.context
        paper_view = getMultiAdapter((self.context, self.request),
                name="paperView")
        si = paper_view.getSpecialIssues()
        if si:
            obj = si[0].getObject()
            title = escape(obj.Title())
            url = obj.absolute_url()
            return {'title' : title, 'url' : url}
        return False
    

    def escape_title(self):
        """
        """
        title = self.context.Title()
        title = escape(title)
        return title
        

    def escape_additional(self):
        ann = self.annotations()
        additional = escape(ann['additional'])
        return unicode(additional, 'utf-8')

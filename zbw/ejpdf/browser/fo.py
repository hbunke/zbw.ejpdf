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
from toolz.itertoolz import first, count


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
        return self.context.created() or self.context.modified()

    def publish_date(self):
        """
        returns date in format Month dayNumber, Year
        """
        obj_date = DT2dt(self.__get_obj_date())
        return obj_date.strftime("%B %d, %Y")

    def last_version_date(self):
        """
        """
        if self.context.portal_type == "JournalPaper":
            ja_view = getMultiAdapter((self.context, self.request),
                                      name="ja_view")
            last_version = ja_view.last_version_info()
            if last_version and last_version['number'] > 1:
                return last_version['date']
            return None

    def get_publish_year(self):
        """
        returns year of creation date
        """
        obj_date = DT2dt(self.__get_obj_date())
        return obj_date.strftime("%Y")

    def uri(self):
        """
        """
        pt = self.context.portal_type
        if pt == "DiscussionPaper":
            uri = self.context.absolute_url()
        if pt == "JournalPaper":
            uri = "http://dx.doi.org/10.5018/economics-ejournal.ja.{}".format(self.context.getId())
        return uri

    def clean_abstract(self):
        """
        """
        html = self.context.getAbstract()

        # tags we don't need BeautifulSoup for. KISS!
        abstract = html.replace('<br />', '')

        soup = BeautifulSoup(abstract, convertEntities=BeautifulSoup.HTML_ENTITIES)

        # replacing html <p> with fo <fo:block>
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

        # replacing sub
        while True:
            sub = soup.find('sub')
            if not sub:
                break
            sub.name = 'fo:inline'
            sub['baseline-shift'] = 'sub'
            sub['font-size'] = '80%'

        # replacing sup
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
        return ann['zbw.coverdata']

    def citation_string(self):
        """
        generates citation string
        """
        # TODO: refactor!

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

            if version:
                text += " ({}). ".format(version['year'])
            else:
                text += " ({}). ".format(self.context.created().strftime("%Y"))

            title = self.escape_title()
            text += unicode(title, 'utf-8')

            signs = ('?', '!', '.')
            if not text.endswith(signs):
                text += "."
            text += " <fo:inline font-style='italic'>Economics: The Open-Access, Open-Assessment E-Journal</fo:inline>, "
            text += "%s (%s)" %(type_view.get_volume(), self.context.getId())

            if self.context.getPages():
                pages = self.context.getPages()
                text += u": 1&#x2013;%s" % pages

            if version and version['number'] > 1:
               text += " (Version %s)" %version['number']
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
            author_id=brain.getObject().getId(),
            name='{} {}'.format(brain.getObject().getFirstname(), brain.getSurname),
            affil=brain.getObject().getOrganisation()
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
        name = author['name']
        if nr <= 1:
            return name

        if nr == 2:
            if authors[-1] == author:
                return name
            # this is actually quite ugly. It relies on XSL-FO to produce the
            # necessary whitespace after 'and'. We had double-whitespace when
            # returning "and "
            return "{} and".format(name)

        if nr > 2:
            if authors[-1] == author:
                return "and {}".format(name)
            return "{},".format(name)
        return None

    def get_volume(self):
        """
        returns Volume number of Journalarticle according to creation date
        """
        cyear = int(self.__get_obj_date().strftime('%Y'))
        startyear = 2007
        vol = cyear - startyear + 1
        return vol

    def special_issue(self):
        """
        checks if paper has been published in Special Issue
        """
        paper_view = getMultiAdapter((self.context, self.request),
                                     name="paperView")
        si = paper_view.getSpecialIssues()
        if count(si) > 0:
            brain = first(paper_view.getSpecialIssues())
            return {'title': brain.Title, 'url': brain.getURL}
        return False

    def escape_title(self):
        """
        """
        title = self.context.Title()
        return escape(title)

    def escape_additional(self):
        ann = self.annotations()
        additional = escape(ann['additional'])
        return unicode(additional, 'utf-8')

# -*- coding: UTF-8 -*-

# Hendrik Bunke <h.bunke@zbw.eu>
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
from toolz.itertoolz import first, last, count


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
        return DT2dt(self.__get_obj_date()).strftime("%B %d, %Y")

    def last_version_date(self):
        def ja():
            ja_view = getMultiAdapter((self.context, self.request),
                                      name="ja_view")
            last_version = ja_view.last_version_info()
            return last_version and last_version['number'] > 1 and last_version['date'] or None
        
        return self.context.portal_type == "JournalPaper" and ja() or None


    def get_publish_year(self):
        """
        returns year of creation date
        """
        return DT2dt(self.__get_obj_date()).strftime("%Y")

    def uri(self):
        """
        """
        doi_base = "http://dx.doi.org/10.5018/economics-ejournal.ja"
        obj = self.context
        pt = obj.portal_type
        return pt == 'Discussionpaper' and obj.absolute_url()\
            or pt == 'JournalPaper' and '{}.{}'.format(doi_base, obj.getId())

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

    def citation_string_ja(self):
        """ Citation string for Journal Articles """

        paper_view = getMultiAdapter((self.context, self.request),
                                     name="paperView")
        authors = unicode(paper_view.authors_as_string(), 'utf-8')
        type_view = getMultiAdapter((self.context, self.request), name="ja_view")
        version = type_view.last_version_info()
        title = unicode(self.escape_title(), 'utf-8')
        
        # kill all if! ;-)
        version_string = version and version['number'] > 1 and "(Version {})".format(version['number']) or ""
        title_end = title.endswith(('?', '!', '.')) and ' ' or "."
        pages = self.context.getPages() and u": 1&#x2013;{}".format(self.context.getPages()) or ""

        d = dict(
            authors=authors,
            version_string=version_string,
            doi_url="http://dx.doi.org/{}".format(type_view.get_doi()),
            pubdate=version.get('year',
                self.context.created().strftime("%Y")),
            title=title,
            pages=pages,
            title_end=title_end,
            volume=type_view.get_volume(),
            number=self.context.getId(),
            ej_string="<fo:inline font-style='italic'>Economics: The Open-Access, Open-Assessment E-Journal</fo:inline>"
        )

        return u"{authors} ({pubdate}). {title}{title_end} {ej_string}, {volume} \
                ({number}){pages} {version_string}. {doi_url}".format(**d)
        
    def citation_string_dp(self):
        """ Citation string for Discussion Papers """

        paper_view = getMultiAdapter((self.context, self.request),
                                     name="paperView")
        authors = unicode(paper_view.authors_as_string(), 'utf-8')
        date = datetime.now()
        type_view = getMultiAdapter((self.context, self.request), name="dp_view")
        
        d = dict(
            authors=authors,
            citation=escape(type_view.cite_as()),
            url=self.context.absolute_url()
        )

        string = u"{authors} {citation} {url}".format(**d)
        return string.replace(u"Not published yet", unicode(date.year))

    def authors(self):
        """
        returns dicts with fullname and affiliation
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = map(lambda author_id: itemgetter(0)(catalog(id=author_id)),
                     self.context.getAuthors())

        authors = map(lambda obj: dict(
            author_id=obj.getId(),
            name='{} {}'.format(obj.getFirstname(), obj.getSurname()),
            affil=obj.getOrganisation()),
            [brain.getObject() for brain in brains])

        return authors

    def authors_as_string(self):
        return map(lambda author: authors_concat_string(author,
                   self.authors()), self.authors())
    
    def get_volume(self):
        """
        returns Volume number of Journalarticle according to creation date
        """
        cyear = int(self.__get_obj_date().strftime('%Y'))
        startyear = 2007
        return cyear - startyear + 1

    def special_issue(self):
        """
        checks if paper has been published in Special Issue
        """
        def si_dict():
            brain = first(paper_view.getSpecialIssues())
            return {'title': brain.Title, 'url': brain.getURL}
        
        paper_view = getMultiAdapter((self.context, self.request),
                                     name="paperView")
        return count(paper_view.getSpecialIssues()) > 0 and si_dict() or False
        
    def escape_title(self):
        return escape(self.context.Title())

    def escape_additional(self):
        ann = self.annotations()
        additional = escape(ann['additional'])
        return unicode(additional, 'utf-8')


def authors_concat_string(author, authors):
    """
    return proper authors string, dependent on number of authors (1, 2, or
    many)
    """
    nr = len(authors)
    name = author['name']
    is_last = lambda d: (last(authors) == author and "and {}".format(name)) or d
    return (nr == 1 and name)\
        or (nr == 2 and is_last(name)) \
        or is_last("{},".format(name))



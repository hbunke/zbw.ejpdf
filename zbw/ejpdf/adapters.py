# -*- coding: utf-8 -*-
# Dr. Hendrik Bunke, h.bunke@zbw.eu
# 2012-04

import os
import tempfile
from subprocess import Popen, PIPE
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from plone.registry.interfaces import IRegistry
from zbw.ejpdf.interfaces import ICoverSettings



class Cover(object):
    """
    """
    
    def __init__(self, context):
        self.context = context

    def generate(self):
        """
        """

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)

        if settings.fop_cmd:
            fop = settings.fop
        else:
            fop  = 'fop'
        fop_conf = settings.fop_conf
        
        xml_view = getMultiAdapter((self.context, self.context.REQUEST),
                name="cover_xml")
        xsl_view = getMultiAdapter((self.context, self.context.REQUEST),
                name="cover_xsl")
        xml = xml_view()
        xsl = xsl_view()
        xmltemp = tempfile.mktemp(suffix='.xml')
        xsltemp = tempfile.mktemp(suffix='.xsl')
        
        self.__tmpwrite(xmltemp, xml)
        self.__tmpwrite(xsltemp, xsl)
        
        pdfname = "cover.%s.%s.pdf" %(self.context.portal_type,
                self.context.getId())

        fop_cmd = "%s -c '%s' -xml '%s' -xsl '%s' '%s/%s'" %(fop, fop_conf,
                    xmltemp, xsltemp, settings.pdf_dir, pdfname)
        
        stdin = open('/dev/null')
        stdout = stderr = PIPE

        p_fop = Popen(fop_cmd, stderr=stderr, stdout=stdout, stdin=stdin,
            shell=True)
        status_fop = p_fop.wait()
        
        if status_fop != 0:
            #we are splitting the fop error message. can't find an option in
            #fop cli to suppress the USAGE information in case of errors
            #fop_msg = p_fop.stderr.read().rsplit('fop foo.fo -awt')[1]
            fop_msg = p_fop.stderr.read()
            raise FOPError(fop_msg)

        request = self.context.REQUEST
        os.unlink(xmltemp)
        os.unlink(xsltemp)


    def __tmpwrite(self, dat, content):
        """
        writes content to file
        """
        f = open(dat, 'w')
        c = content.encode('utf-8')
        f.write(c)
        f.close()


class CoverAnnotation(object):
    """
    store form values as annotation on object
    """

    def __init__(self, context):

        self.context = context
        self.request = self.context.REQUEST
        ann = IAnnotations(self.context)
        KEY="zbw.coverdata"
       
        if not ann.has_key(KEY):
            ann[KEY] = PersistentDict()
        self.ann = ann[KEY]

        keys = ["keywords", "correspondence", "correspondence_email",
                "additional"]
        for key in keys:
            if key in self.request:
                self.ann[key] = self.request[key]
            else:
                self.ann[key] = ""


class FOPError(Exception):
    pass

   









        

        


    



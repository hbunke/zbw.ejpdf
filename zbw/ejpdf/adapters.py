# -*- coding: utf-8 -*-
# Dr. Hendrik Bunke, h.bunke@zbw.eu
# 2012-04

import os
import tempfile
from subprocess import Popen, PIPE
from zope.component import getMultiAdapter
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict



class Cover(object):
    """
    """
    
    def __init__(self, context):
        self.context = context


    def generate(self):
        """
        """
        
        #TODO put this in config (file or registry)
        
        fop = "fop"
        fopconf="/home/ejournal/etc/fopconf.xml"
        
        #TODO change this
        pdfdir = "/home/bunke/test/ejpdftest"

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

        fofile = tempfile.mktemp(suffix='.fo')
        
        #TODO bei neuem FOP ist der xsltproc nicht nötig, sondern mit fop in
        #einem Schritt zu erledigen
        xslt_cmd = "xsltproc -o %s -xinclude %s %s" %(fofile, xsltemp, xmltemp)
        
        fop_cmd = "%s -c '%s' '%s' '%s/%s'" %(fop, fopconf, fofile, pdfdir, pdfname)
        
        stdin = open('/dev/null')
        stdout = stderr = PIPE

        p_xslt = Popen(xslt_cmd, stderr=stderr, stdin=stdin, stdout=stdout,
                shell=True)
        status = p_xslt.wait()
        if status == 0:
            p_fop = Popen(fop_cmd, stderr=stderr, stdout=stdout, stdin=stdin,
                shell=True)
            status = p_fop.wait()
            if status == 0:
                return True
            else:
                print p_fop.stderr.read()
                
        else:
            print p_xslt.stderr.read()
        
        return False

        request = self.context.REQUEST
        os.unlink(xmltemp)
        os.unlink(xsltemp)
        os.unlink(fofile)


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


       









        

        


    



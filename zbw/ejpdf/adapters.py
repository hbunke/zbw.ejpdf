# -*- coding: utf-8 -*-
# Dr. Hendrik Bunke, h.bunke@zbw.eu
# 2012-04

import os
import tempfile
from subprocess import Popen, PIPE
from zope.component import getMultiAdapter



class Cover(object):
    """
    """
    
    def __init__(self, context):
        self.context = context


    def generate(self):
        """
        """
        fop = "/home/bunke/bin/fop"
        fopconf="/home/bunke/.fop/fop.xconf"
        pdfdir = "/home/bunke/test/ejpdftest"
        xml_view = getMultiAdapter((self.context, self.context.REQUEST),
                name="cover_xml")
        xml = xml_view()
        xmltemp = tempfile.mktemp(suffix='.xml')
        f = open(xmltemp, 'w')
        
        #xml = unicode(xml, 'utf-8', errors="ignore")
        xml = xml.encode('utf-8')
        
        f.write(xml)
        f.close()
        
        xsl = "/home/bunke/ejdev/zbw.ejpdf/zbw/ejpdf/browser/cover.xsl"
        
        pdfname = "cover.%s.%s.pdf" %(self.context.portal_type,
                self.context.getId())

        fofile = tempfile.mktemp(suffix='.fo')
        xslt_cmd = "xsltproc -o %s -xinclude %s %s" %(fofile, xsl, xmltemp)
        fop_cmd = "%s -c '%s'  '%s' '%s/%s'" %(fop, fopconf, fofile, pdfdir, pdfname)
        
        stdin = open('/dev/null')
        stdout = stderr = PIPE

        #import pdb; pdb.set_trace()
        p_xslt = Popen(xslt_cmd, stderr=stderr, stdin=stdin, stdout=stdout,
                shell=True)
        status = p_xslt.wait()
        if status == 0:
            #import pdb; pdb.set_trace()
            p_fop = Popen(fop_cmd, stderr=stderr, stdout=stdout, stdin=stdin,
                shell=True)
            status = p_fop.wait()
            if status == 0:
                os.unlink(xmltemp)
                os.unlink(fofile)
                return True
            else:
                os.unlink(xmltemp)
                os.unlink(fofile)
        return False









        

        


    



# -*- coding: utf-8 -*-
# Dr. Hendrik Bunke, h.bunke@zbw.eu
# 2012-04

import os
import tempfile
from subprocess import Popen, PIPE
from zope.component import getMultiAdapter, getUtility
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from plone.registry.interfaces import IRegistry
from zbw.ejpdf.interfaces import ICoverSettings
from operator import itemgetter

class Cover(object):
    """
    """
    
    def __init__(self, context):
        
        self.context = context
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)

        if settings.fop_cmd:
            fop = settings.fop_cmd
        else:
            fop  = 'fop'
        fop_conf = settings.fop_conf
        
        fo_view = getMultiAdapter((self.context, self.context.REQUEST),
                name="cover_fo")
        fo = fo_view()
        
        
        fotemp = tempfile.mktemp(suffix='.fo')
        f = open(fotemp, 'w')
        c = fo.encode('utf-8')
        f.write(c)
        f.close()

        pdfname = "cover.%s.%s.pdf" %(self.context.portal_type,
                self.context.getId())
        pdf = settings.pdf_dir + '/' + pdfname
        
        #fop_cmd = "%s '-c' '%s' '%s' '%s/%s'" %(fop, fop_conf, fotemp,
        #            settings.pdf_dir, pdfname)

        fop_list = [fop, '-c', fop_conf, fotemp, pdf] 

        stdin = open('/dev/null')
        stdout = stderr = PIPE
        env = {'PATH':'/bin:/usr/bin:/usr/local/bin'}
        p_fop = Popen(fop_list, 
                stderr=stderr, 
                stdout=stdout, 
                stdin=stdin,
                env=env)

        #XXX wait() might causes deadlocks in case of large outputs
        #status_fop = p_fop.wait().
        #better use communicate(). See
        #http://docs.python.org/library/subprocess.html#subprocess.Popen.wait
        
        p_fop_out = p_fop.communicate()
        p_fop_status = p_fop.returncode

        if p_fop_status !=0:
            fop_msg = p_fop_out[1]
            raise FOPError(fop_msg, p_fop_status)

        #if status_fop != 0:
        #    fop_msg = p_fop.stderr.read()
        #    raise FOPError(fop_msg, status_fop)

        request = self.context.REQUEST
        os.unlink(fotemp)


class CoverAnnotation(object):
    """
    store form values as annotation on object. Called before PDF generation
    (browser/pdf.py)
    """

    def __init__(self, context):

        self.context = context
        self.request = self.context.REQUEST
        ann = IAnnotations(self.context)
        KEY="zbw.coverdata"
        
        # for debugging and testing: first delete previously stored annotations
        #del ann[KEY]

        if KEY not in ann:
            ann[KEY] = PersistentDict()
        self.ann = ann[KEY]

        request_author_keys = ['author_name', 'affil', 'author_email',
                                'author_id']
        
        for key in request_author_keys:
            if isinstance(self.request[key], basestring):
                self.request[key] = [self.request[key]]
            
        authors = zip(self.request['author_name'], self.request['affil'],
                self.request['author_email'], self.request['author_id'])
 
        self.ann['authors'] = map(lambda author: dict(
                name = author[0],
                affil = author[1],
                email = author[2],
                author_id = author[3],
                #generator expression; boolean
                corresponding = (author[3] == self.request['corresponding_author']) 
                ), 
                authors)
        
        keys = ["keywords", 
                "additional",
                "date_submission",
                "date_accepted_as_dp",
                "date_published_as_dp",
                "date_revised", 
                "date_accepted_as_ja",
                "date_published_as_ja",
                ]

        for key in keys:
            self.ann[key] = u""
            if key in self.request:
                self.ann[key] = self.request[key]

        


class FOPError(Exception):
    
    def __init__(self, reason, errorcode):
        self.reason = str(reason)
        self.errorcode = errorcode
    
    def __str__(self):
        s = "(%s)  " %self.errorcode
        s += self.reason
        return s
   



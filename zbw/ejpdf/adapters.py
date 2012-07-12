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

        fop_cmd = "%s -c '%s' %s '%s/%s'" %(fop, fop_conf, fotemp,
                    settings.pdf_dir, pdfname)
        
        stdin = open('/dev/null')
        stdout = stderr = PIPE
        
        p_fop = Popen(fop_cmd, stderr=stderr, stdout=stdout, stdin=stdin,
            shell=True)

        
        #XXX wait() might causes deadlocks in case of large outputs
        #status_fop = p_fop.wait(). This might have been the cause for the
        #errors on freebsd
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
    store form values as annotation on object
    """

    def __init__(self, context):

        self.context = context
        self.request = self.context.REQUEST
        ann = IAnnotations(self.context)
        KEY="zbw.coverdata"
        
        # for debugging and testing: first delete previously stored annotations
        #del ann[KEY]

        if not ann.has_key(KEY):
            ann[KEY] = PersistentDict()
        self.ann = ann[KEY]

        # a little complicated here, but we need to combine several field
        # values from the control form, in order to get all necessary author
        # information
        #XXX could be done better, most probably ;-)

        request_author_keys = ['author_name', 'affil', 'author_email']
        for key in request_author_keys:
            if type(self.request[key]) is not list:
                    self.request[key] = [self.request[key]]
            
        authors = zip(self.request['author_name'], self.request['affil'],
                self.request['author_email'])
        authors_new = []
        for author in authors:
            author_new = dict(
                            name = author[0],
                            affil = author[1],
                            email = author[2],
                            corresponding = False
                            )

            # erstes if kann spaeter weg, wenn corresponding standardmaessig übermittelt
            # wird
            if 'corresponding_author' in self.request:
                if author[0] == self.request['corresponding_author']:
                    author_new['corresponding'] = True
            
            authors_new.append(author_new)
       
        self.ann['authors'] = authors_new
        keys = ["keywords", 
                "correspondence",
                "additional",
                ]

        for key in keys:
            if key in self.request:
                self.ann[key] = self.request[key]
            else:
                self.ann[key] = u""



class FOPError(Exception):
    pass
   



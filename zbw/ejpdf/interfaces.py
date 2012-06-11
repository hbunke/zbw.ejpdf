# -*- coding: utf-8 -*-
# Dr. Hendrik Bunke, h.bunke@zbw.eu

from zope.interface import Interface
from zope import schema

class ICover(Interface):
    """
    Interface for generating Economics PDF-Cover
    """

    def generate():
        """
        """

class ICoverAnnotation(Interface):
    """
    Interface for storing form data from cover_control as Annotation on object
    """

class ICoverSettings(Interface):
    """
    Configuration panel
    """

    pdf_dir = schema.TextLine(
            title=u"PDF Directory",
            description=u"Please give the *complete* path where the cover PDFs\
                            shall be stored",
            required=True,
            )

    pdf_url = schema.TextLine(
            title=u"PDF URL",
            description=u"URL the PDF view is redirected to. This must be\
                    in your webserver with the PDF dir",
            required = True,
            )

    fop_conf = schema.TextLine(
            title=u"FOP Configuration",
            description=u"Path to your FOP Config",
            required = True,
            )

    fop_cmd = schema.TextLine(
            title=u"FOP cmd",
            description=u"Path to your local fop command. Default is 'fop'",
            required = False,
            )


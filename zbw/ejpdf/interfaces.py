# -*- coding: utf-8 -*-
# Dr. Hendrik Bunke, h.bunke@zbw.eu

from zope.interface import Interface
#from zope import schema

class ICover(Interface):
    """
    Interface for generating Economics PDF-Cover
    """

    def generate():
        """
        """


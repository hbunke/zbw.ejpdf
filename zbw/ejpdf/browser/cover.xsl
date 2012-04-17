<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
								version="1.0">
<xsl:decimal-format name="de" decimal-separator="," grouping-separator="."/>
								
<xsl:template match="/">

    <!-- TODO:
         -  journalarticle sieht anders aus: 
            -   kein portal_type
            -   kleineres logo? 
            -   vol statt no
            -   zusätzlicher Block: Citation
    -->

	<fo:root
	font-family="Times" 
	font-selection-strategy="character-by-character" 
	font-size="11pt">
	
		<fo:layout-master-set>
			
			<fo:simple-page-master master-name="A4"
				page-width="210mm" page-height="297mm"
				margin-top="1.5cm" margin-bottom="1.25cm" margin-left="3.6cm"
				margin-right="3.6cm">
				<fo:region-body margin-top="2.5cm" />
				<fo:region-before extent="2cm" />
				<fo:region-after extent="1cm" />
			</fo:simple-page-master>
		
		</fo:layout-master-set>
			
        <fo:page-sequence master-reference="A4">

            <fo:static-content flow-name="xsl-region-after"
                font-size="8pt" font-family="Helvetica">
                <fo:block>
                    © Author(s) 2012. Licensed under a Creative Commons License
                    - Attribution-NonCommercial 2.0 Germany
                </fo:block>
            </fo:static-content>
			
				<fo:flow flow-name="xsl-region-body">
					
                    <!-- Logo -->
                    <fo:block-container absolute-position="fixed" top="1.5cm" 
                        left="1cm">
						<fo:block >
                            <fo:external-graphic 
                                src="file:///home/bunke/ejdev/zbw.ejpdf/zbw/ejpdf/example_files/logo3.tif" />
                        </fo:block>
                    </fo:block-container>

                    <!-- infozeile -->
                    <fo:block-container space-before="6px"
                        font-family="Helvetica"
                        font-size="8pt">
                    	<fo:block font-weight="bold">
                            <xsl:value-of select="/cover/portal_type" />
                        </fo:block>
                        <fo:block>
                            No.  <fo:inline><xsl:value-of select="/cover/id" /></fo:inline> |
                            <fo:inline><xsl:value-of select="/cover/date" /></fo:inline> |
                            <fo:inline><xsl:value-of select="/cover/url" /></fo:inline>
                        </fo:block>
                    </fo:block-container>


                    
                    
                    <fo:block
                        
                        font-size="17pt"
                        font-weight="bold"
                        text-align="center"
                        space-before="2cm">

                        <xsl:value-of select="/cover/title" />
                    
                    </fo:block>
                    
                    
                    <fo:block-container
                        font-style="italic"
                        space-before="0.5cm"
                        text-align="center">
                    
                        <xsl:apply-templates match="//author" />
                    
                    </fo:block-container>

                    
                    <!-- abstract -->
                    <fo:block text-align="justify" space-before="18px" language="en" hyphenate="true">
                        <fo:inline font-weight="bold" padding-right="9px">Abstract </fo:inline>
                        <xsl:value-of select="/cover/abstract/p" />
                    </fo:block>
    
                    <fo:block text-align="justify" space-after="18px" space-before="12px">
                        <xsl:value-of select="/cover/abstract/p[2]" />
                    
                    </fo:block>

                    <fo:block>
                        <fo:inline font-weight="bold" padding-right="9px">JEL </fo:inline>
                        <xsl:for-each select="/cover/jels/jel">
                            <fo:inline padding-right="6px"><xsl:value-of select="." />
                            </fo:inline>
                        </xsl:for-each>
                    </fo:block>

                    <fo:block space-before="6px">
                        <fo:inline font-weight="bold" padding-right="9px">Keywords</fo:inline> 
                        <xsl:value-of select="/cover/keywords" />
                    </fo:block>
                    
                    <fo:block space-before="6px">
                        <fo:inline font-weight="bold" padding-right="9px">Correspondence</fo:inline> 
                        <xsl:value-of select="/cover/correspondence" /> 
                        E-mail:
                        <fo:inline><xsl:value-of select="/cover/email" /></fo:inline>
                    </fo:block>

                    <fo:block font-size='10px' space-before="6px" font-style="italic">
                        <xsl:value-of select="/cover/additional" /> 
                    </fo:block>


                    



                </fo:flow>

                <!-- footer 

                <fo:flow flow-name="xls-region-after">
                
                                   
                </fo:flow>
                -->


			</fo:page-sequence>

	</fo:root>
	
</xsl:template>

<xsl:template match="//author">

    <fo:block font-size="14pt" >
        <xsl:value-of select="name" />
    </fo:block>

    <fo:block font-size="11pt" space-after="6px">
        <xsl:value-of select="affil" />
    </fo:block>

</xsl:template>



</xsl:stylesheet>
	
	

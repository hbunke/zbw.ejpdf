<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
								version="1.0">
<xsl:decimal-format name="de" decimal-separator="," grouping-separator="."/>
								
<xsl:template match="/">

	<fo:root
	font-family="Helvetica" 
	font-selection-strategy="character-by-character" 
	font-size="11pt">
	
		<fo:layout-master-set>
			
			<fo:simple-page-master master-name="A4"
				page-width="210mm" page-height="297mm"
				margin-top="1.5cm" margin-bottom="1.25cm" margin-left="3cm"
				margin-right="3cm">
				<fo:region-body margin-top="2.5cm" />
				<fo:region-before extent="2cm" />
				<fo:region-after extent="2cm" />
			</fo:simple-page-master>
		
		</fo:layout-master-set>
			
			<fo:page-sequence master-reference="A4">
			
				<fo:flow flow-name="xsl-region-body">
					
					
					<!-- Logo -->
					<fo:block-container absolute-position="fixed" top="1.1cm" left="3cm">
						<fo:block>
                            <!--TODO -->	
                            <fo:external-graphic src="file:///" content-height="1.58cm"/>
						</fo:block>
					</fo:block-container>
					
					
                    <!-- Absender Adressfeld BEISPIEL! -->
					<fo:block-container
						absolute-position="fixed"
						left="3cm"
						right="0cm"
						bottom="0cm"
						top="3.5cm"
						font-size="7pt"
						font-family="Helvetica">
						<fo:block>Dr. Hendrik Bunke | Friesenstr. 93 | 28203 Bremen</fo:block>
					</fo:block-container>
					
					<fo:block-container
						absolute-position="fixed"
						left="3cm"
						right="0cm"
						top="4.45cm"
						bottom="0cm">
						<fo:block>
							<xsl:value-of select="/brief/adresse/name" />
						</fo:block>
						<xsl:for-each select="//zeile">
							<fo:block><xsl:value-of select="." /></fo:block>
						</xsl:for-each>
						<fo:block>
							<xsl:value-of select="/brief/adresse/strasse" />
						</fo:block>
						<fo:block space-before="6pt">
							<xsl:value-of select="/brief/adresse/plz" /><xsl:text> </xsl:text><xsl:value-of select="/brief/adresse/ort" />
						</fo:block>
					</fo:block-container>
					
					
					<xsl:apply-templates />

                </fo:flow>
			</fo:page-sequence>

	</fo:root>
	
</xsl:template>

<xsl:template match="para">
	<fo:block space-before="6pt" language="de" hyphenate="true">
		<xsl:apply-templates />
	</fo:block>
</xsl:template>

<xsl:template match="betreff">
	<fo:block space-before="4.2cm" space-after="0.5cm"
	 font-weight="600" >
		<xsl:value-of select="." />
    
	</fo:block>
</xsl:template>

<xsl:template match="anrede">
	<fo:block space-after="12pt">
		<xsl:value-of select="." /><xsl:text>,</xsl:text>
	</fo:block>
</xsl:template>

<xsl:template match="gruss">
	<fo:block space-before="24pt" space-after="0.5cm">
		<xsl:value-of select="." />
	</fo:block>
	
	<xsl:choose>
		<xsl:when test="@signatur='yes'">
			<fo:block>
				<fo:external-graphic src="file:///home/bunke/hbxt/img/unterschrift.jpg" content-height="1.5cm" />
			</fo:block>
		</xsl:when>
		<xsl:otherwise>
			<fo:block space-after="1cm" />
		</xsl:otherwise>
	</xsl:choose>
	
	<fo:block>(Dr. Hendrik Bunke)</fo:block>
</xsl:template>
		
<xsl:template match="datum">
	<fo:block-container absolute-position="fixed" top="6.18cm" right="3cm"
		bottom="0cm" left="17.5cm">
		<fo:block text-align="right"><xsl:value-of select="." /></fo:block>
	</fo:block-container>
</xsl:template>

<xsl:template match="strong">	
	<fo:inline font-weight="bold"><xsl:value-of select="." /></fo:inline>
</xsl:template>

<xsl:template match="emphasis">
	<fo:inline font-style="italic"><xsl:value-of select="." /></fo:inline>
</xsl:template>

<xsl:template match="rechnung">
	
	<fo:block-container space-before="18pt" space-after="24pt">
		<fo:table>
			<fo:table-column width="75%" />
			<fo:table-column width="25%" />
			<fo:table-body>
			<xsl:for-each select="posten">
				<fo:table-row>
					<fo:table-cell padding-bottom="6pt">
						<fo:block><xsl:value-of select="title" /></fo:block>
					</fo:table-cell>
					<fo:table-cell>
						<fo:block text-align="right" padding-bottom="6pt">
							<xsl:value-of select="format-number(preis,'#.##0,00','de')" />
							<!-- hier noch Eurozeichen einfügen? --> EUR</fo:block>
					</fo:table-cell>
				</fo:table-row>
			</xsl:for-each>
			<fo:table-row background-color="rgb(240,240,240)">
				<fo:table-cell padding-top="6pt" padding-bottom="6pt">
					<fo:block font-weight="bold">Gesamt</fo:block></fo:table-cell>
				<fo:table-cell padding-top="6pt" padding-bottom="6pt">
					<fo:block font-weight="bold" text-align="right">
							<xsl:variable name="gesamt" select="sum(posten/preis)" />
							<xsl:value-of select="format-number($gesamt,'#.##0,00','de')"
							/> EUR
					</fo:block>
				</fo:table-cell>
			</fo:table-row>
				
			</fo:table-body> </fo:table> <fo:block font-size="7pt">[Es besteht derzeit keine
			Umsatzsteuerpflicht]</fo:block> </fo:block-container> </xsl:template>

<xsl:template match="quote">
	<xsl:text>&#187;</xsl:text><xsl:value-of select="."/><xsl:text>&#171;</xsl:text>
</xsl:template>

<xsl:template match="anlagen">
	<fo:block font-size="9pt" space-before="15pt">Anlagen: <xsl:value-of select="." /></fo:block>
</xsl:template>

</xsl:stylesheet>
	
	

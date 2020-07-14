# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import mmap
import re
import sys
from lxml import etree as ET

filename = sys.argv[1]

with open(filename, 'rb+', 0) as file, \
	mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
	
	#create_date_re = re.search(b'<xmp:CreateDate>(.*)</xmp:CreateDate>', s)
	#if create_date_re:
	
	#PDF/A-1a (default)
	xmp_metadata_re = re.search(b'<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 4.2.1\\-c043 52.372728, 2009/01/18\\-15:08:04 ">(\\S|\\s)+</rdf:RDF>[\\s]*</x:xmpmeta>[\\s]*<\\?xpacket end="w"\\?>', s)
	#if not PDF/A-1a, check PDF/A-1b
	#if not PDF/A-1b, check PDF/A-2a
	#if not PDF/A-2a, check PDF/A-2b
	#if not PDF/A-2b, check PDF/A-2u
	
	if not xmp_metadata_re:#if not PDF/A-2u, check PDF/A-3a
		xmp_metadata_re = re.search(b'<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 5.6\\-c015 84.159810, 2016/09/10\\-02:41:30 ">(\\S|\\s)+</rdf:RDF>[\\s]*</x:xmpmeta>[\\s]*<\\?xpacket end="w"\\?>', s)
	#if not PDF/A-3a, check PDF/A-3b
	#if not PDF/A-3b, check PDF/A-1u
	#if not PDF/A-3u, check PDF/X-1
	#if not PDF/X-1, check PDF/X-2
	#if not PDF/X-2, check PDF/X-3
	#if not PDF/X-3, check PDF/X-4
	if not xmp_metadata_re:
		xmp_metadata_re = re.search(b'<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 5.6\\-c015 84.159810, 2016/09/10\\-02:41:30 ">(\\S|\\s)+</rdf:RDF>[\\s]*</x:xmpmeta>[\\s]*<\\?xpacket end="w"\\?>', s)
		
		
	#PDFA-1a
	#<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 4.2.1-c043 52.372728, 2009/01/18-15:08:04        ">^^J%
	#PDFX-4
	#<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 5.6-c015 84.159810, 2016/09/10-02:41:30        ">^^J%
	
	# If PDF standard was verified, copy CreateDate from file and insert into PDF
	if xmp_metadata_re:
		print('XMP data found')
		#<xmp:CreateDate>2018-07-28T08:54:48-05:00</xmp:CreateDate>
		#/CreationDate(D:20180723210935-05'00')
		#str.replace(old, new[, max])
		data = xmp_metadata_re.group()

		tree = ET.fromstring(data)
		'''<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 5.6-c015 84.159810, 2016/09/10-02:41:30 ">
		<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
		<rdf:Description rdf:about=""
		xmlns:xmp="http://ns.adobe.com/xap/1.0/"
		xmlns:dc="http://purl.org/dc/elements/1.1/"
		xmlns:xmpMM="http://ns.adobe.com/xap/1.0/mm/"
		xmlns:pdf="http://ns.adobe.com/pdf/1.3/"
		xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/"
		xmlns:xmpRights="http://ns.adobe.com/xap/1.0/rights/"
		xmlns:pdfxid="http://www.npes.org/pdfx/ns/id/"
		xmlns:pdfaExtension="http://www.aiim.org/pdfa/ns/extension/"
		xmlns:pdfaSchema="http://www.aiim.org/pdfa/ns/schema#"
		xmlns:pdfaProperty="http://www.aiim.org/pdfa/ns/property#">
		<xmp:CreateDate>2018-07-30T13:28:40-05:00</xmp:CreateDate>
		<xmp:ModifyDate>2018-07-30T13:28:40-05:00</xmp:ModifyDate>
		<xmp:MetadataDate>2018-07-30T13:28:40-05:00</xmp:MetadataDate>
		<xmp:CreatorTool>miktex; xelatex; makeindex; makeglossaries; biblatex (biber)</xmp:CreatorTool>
		<dc:format>application/pdf</dc:format>
		<dc:title>
		<rdf:Alt>
		<rdf:li xml:lang="x-default">A descriptive grammar of the Sajolang (Miji) language of Upper Dzang village</rdf:li>
		</rdf:Alt>
		</dc:title>
		<dc:description>
		<rdf:Alt>
		<rdf:li xml:lang="x-default">Ph.D. dissertation</rdf:li>
		</rdf:Alt>
		</dc:description>
		<dc:creator>
		<rdf:Seq>
		<rdf:li>Christopher S. Weedall</rdf:li>
		</rdf:Seq>
		</dc:creator>
		<dc:subject>
		<rdf:Bag>
		<rdf:li>Sajolang; Miji; grammar; language; linguistics</rdf:li>
		</rdf:Bag>
		</dc:subject>
		<dc:type>
		<rdf:Bag>
		<rdf:li>Text</rdf:li>
		</rdf:Bag>
		</dc:type>
		<dc:source>thesis.tex</dc:source>
		<xmpMM:DocumentID>uuid:f7a3e4c9-bbb6-47a3-9b67-a39b1d759b62</xmpMM:DocumentID>
		<xmpMM:InstanceID>uuid:20005467-a395-4f7a-882b-b620aea8267f</xmpMM:InstanceID>
		<xmpMM:RenditionClass>default</xmpMM:RenditionClass>
		<xmpMM:VersionID>1</xmpMM:VersionID>
		<pdf:Keywords>Sajolang; Miji; grammar; language; linguistics</pdf:Keywords>
		<pdf:Producer>XeTeX 0.99999</pdf:Producer>
		<pdf:Trapped>True</pdf:Trapped>
		<pdfxid:GTS_PDFXVersion>PDF/X-4</pdfxid:GTS_PDFXVersion>
		</rdf:Description>
		</rdf:RDF>
		</x:xmpmeta>'''
		ns = {'x':'adobe:ns:meta/', 'rdf':'http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'xmp':'http://ns.adobe.com/xap/1.0/',}
		print(tree.xpath('//x:xmpmeta//rdf:RDF//rdf:Description//xmp:CreateDate', namespaces=ns)[0].text.strip())
		create_date_byte_str = bytes(tree.xpath('//x:xmpmeta//rdf:RDF//rdf:Description//xmp:CreateDate', namespaces=ns)[0].text.strip(), 'utf-8')
		fix_date = create_date_byte_str.replace(b'-',b'',2).replace(b':',b'',2).replace(b'T',b'')
		#fix_date = create_date_re.group(1).replace(b'-',b'',2).replace(b':',b'',2).replace(b'T',b'')
		fix_date = fix_date.replace(b':',b'\'') + b'\''
		fix_date_re = re.sub(b'(/CreationDate\(D:)(.*)(\))', b'\g<1>'+fix_date+b'\g<3>', s)
		print(fix_date)
		file.write(fix_date_re)
	else:
		print('Something is wrong... CreateDate does not exist in the file "'+filename+'"')
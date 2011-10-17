#!/usr/bin/env python

# bbt.py v0.7b - BlackBerry BBThumbsXXXxXXX.key file parser
# Copyright (C) 2011, Sheran A. Gunasekera <sheran@zensay.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#

import sys
import struct
import datetime
import getopt
import os
from bbtmodules.DatFile import DatFile
from bbtmodules.BBThumbs import BBThumbs

def usage():
	print("Usage: bbt.py [options]")
	print("  -h, --help: This cruft")
	print("  -k, --key <bbthumbs key file>: Process post OS5 thumbs.key file (requires thumbs.dat file in same directory)")
	print("  -b, --bbthumbs <old bbthumbs file>: Process pre OS5 BBThumbs.dat file")
	print("  -x, --extract: Extracts the thumbnails into directory specified by -o")
	print("  -o, --output <output directory>: Directory to extract thumbs to (used only with -x)")
	print("  -f, --offset: Show record ID and Offset of each thumbnail (BBThumbs.dat has no record ID)")
	
def process(kf,outdir,extract,offsets):
	thumbsperrow = 3
	if(kf.startswith('-')):
		usage()
		sys.exit(2)
	if extract:
		if not os.path.exists(outdir):
			os.makedirs(outdir)
		else:
			print "Directory already exists"
			sys.exit(2)
	print "*** Processing "+os.path.split(kf)[1]+" on "+str(datetime.datetime.now())
	bbt_file = open(kf,'rb')
	magic = (struct.unpack(">4s",bbt_file.read(4)))[0].encode("hex").upper()
	if magic != "08062009":
		print kf+" is not a BlackBerry thumbs file!";
		sys.exit(2)
	bbt_file.seek(9,1)
	thumbs = []

	try:
		while(True):
			tkey = (struct.unpack(">4s",bbt_file.read(4)))[0].encode("hex").upper()
			bbt_file.seek(4,1)
			tval = (struct.unpack(">I",bbt_file.read(4))[0])
			if tval != 0:
				thumbs.append([tkey, tval]) 
	except:
		bbt_file.close()
		dfile = DatFile(kf[:-3]+"dat")
		ctr = 0;
		if dfile.is_valid:
			if extract:
				html = open(os.path.join(outdir,"bbt.html"),"w")
				html.write("<html>\n<head><style type='text/css'>\np {font-family:'Verdana';font-size: 10px;}\n</style>\n<title>BBT Report for "+kf+"</title></head>\n<body>")
				html.write("<p>bbt.py - BlackBerry Thumbnails file parser</br>")
				html.write("Sheran A. Gunasekera</p>")
				html.write("<p>Report generated on: "+datetime.datetime.now().strftime("%d-%m-%Y %H:%M")+"</p>\n")
				html.write("<table border=1>\n")
			for key in thumbs:
				rec = dfile.record(key[1], key[0])
				if rec != None:
					if extract:
						rec.save_to_disk(outdir)
					timestamp = rec.gmt_timestamp()
					if extract:
						if ctr == 0 or not ctr%thumbsperrow:
							skip = 0
							html.write("<tr><td valign=bottom>")
						else:
							html.write("<td valign=bottom>")
							skip += 1
						html.write("<img src='"+rec.name()+"' />"+"<p>ID: "+str(key[0])+"<br/>Offset: "+str(key[1])+"<br/>Name: "+rec.name()+"<br/>Time: "+timestamp+"<br/>Hash: "+rec.sha1hash()+"</p>")
						if skip == thumbsperrow - 1:
							skip = 0
							html.write("</td></tr>\n")
						else:
							html.write("</td>\n")
					if offsets:
						print "+ ID: "+str(key[0])+" Offset: "+str(key[1])+" // "+rec.name()+" // "+timestamp+" // "+rec.sha1hash()
					else:
						print "+ "+rec.name()+" // "+timestamp+" // "+rec.sha1hash()
					ctr += 1
		if extract:
			html.write("</table>\n</body>\n</html>")
			html.close()
		dfile.close()
		print "*** "+os.path.split(kf)[1]+" has "+str(len(thumbs))+" records"
		print "*** Processed "+str(ctr)+" records"
		
def oldthumbs(bbthumbs,outdir,extract,offsets):
	thumbsperrow = 3
	if(bbthumbs.startswith('-')):
		usage()
		sys.exit(2)
	if extract:
		if not os.path.exists(outdir):
			os.makedirs(outdir)
		else:
			print "Directory already exists"
			sys.exit(2)
	print "*** Processing "+os.path.split(bbthumbs)[1]+" on "+str(datetime.datetime.now())
	bbth = BBThumbs(bbthumbs)
	if bbth.is_valid():
		recs = bbth.process()
		if extract:
			html = open(os.path.join(outdir,"bbt.html"),"w")
			html.write("<html>\n<head><style type='text/css'>\np {font-family:'Verdana';font-size: 10px;}\n</style>\n<title>BBT Report for "+os.path.split(bbthumbs)[1]+"</title></head>\n<body>")
			html.write("<p>bbt.py - BlackBerry Thumbnails file parser</br>")
			html.write("Sheran A. Gunasekera</p>")
			html.write("<p>Report generated on: "+datetime.datetime.now().strftime("%d-%m-%Y %H:%M")+"</p>\n")
			html.write("<table border=1>\n")
		ctr = 0;
		for rec in recs:
			if extract:
				bbth.record(rec).save_to_disk(outdir)
			timestamp = bbth.record(rec).gmt_timestamp()
			if extract:
				if ctr == 0 or not ctr%thumbsperrow:
					skip = 0
					html.write("<tr><td valign=bottom>")
				else:
					html.write("<td valign=bottom>")
					skip += 1
				html.write("<img src='"+bbth.record(rec).name()+"' />"+"<p>Offset: "+str(rec)+"<br/>Name: "+bbth.record(rec).name()+"<br/>Time: "+timestamp+"<br/>Hash: "+bbth.record(rec).sha1hash()+"</p>")
				if skip == thumbsperrow - 1:
					skip = 0
					html.write("</td></tr>\n")
				else:
					html.write("</td>\n")
			if offsets:
				print "+ Offset: "+str(rec)+" // "+bbth.record(rec).name()+" // "+timestamp+" // "+bbth.record(rec).sha1hash()
			else:
				print "+ "+bbth.record(rec).name()+" // "+timestamp+" // "+bbth.record(rec).sha1hash()
			ctr +=1
	else:
		print bbthumbs+" is not a BlackBerry thumbs file!";
		sys.exit(2)
	if extract:
		html.write("</table>\n</body>\n</html>")
		html.close()
	bbth.close()
	print "*** "+os.path.split(bbthumbs)[1]+" has "+str(len(recs))+" records"

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hk:o:xb:lmf", ["help", "key=","output=","extract","bbthumbs=","local","machine","offset"])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)
	
	keyfile = None
	outdir = None
	extract = False
	bbthumbs = None
	local = False
	machine = False
	offsets = False
	
	for o,a in opts:
		if o in ("-k","--key"):
			keyfile = a
		elif o in ("-h","--help"):
			usage()
			sys.exit()
		elif o in("-o","--output"):
			outdir = a
		elif o in("-x","--extract"):
			extract = True
		elif o in("-b","--bbthumbs"):
			bbthumbs = a
		elif o in("-f","--offset"):
			offsets = True
		else:
			assert False, "unhandled option"
		
	if keyfile == None and bbthumbs == None:
		usage()
		sys.exit()
	
	if keyfile and bbthumbs:
		print "-k and -b are mutually exclusive.  Use one or the other."
		sys.exit(2)
	
	if extract:
		if outdir == None:
			print "-x requires an output directory"
			sys.exit(2)
		
	if keyfile:
		process(keyfile,outdir,extract,offsets)	
	elif bbthumbs:
		oldthumbs(bbthumbs,outdir,extract,offsets)
	else:
		sys.exit()


if __name__ == "__main__":
	main()

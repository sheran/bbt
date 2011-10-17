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

import struct
import time
import hashlib
import os

class BBThumbs:
	def __init__(self,dat_file):
		self.dat_file = open(dat_file,'rb')
	
	def is_valid(self):
		self.dat_file.seek(0,0)
		magic = (struct.unpack(">4s",self.dat_file.read(4)))[0].encode("hex").upper()
		valid = (True if magic == "24052003" else False)
		return valid
	
	def process(self):
		self.dat_file.seek(1,1)
		# Header 1
		# byte Start of Record [0]
		# byte Dunno [1]
		# byte Length of File Name [2]
		# Header 2
		# long Unix Timestamp in milliseconds [0]
		# int Dunno [1]
		# int Length of Data [2]
		record_offsets = []
		record_offsets.append(self.dat_file.tell())
		try:
			while(True):
				h1b = self.dat_file.read(3)
				if len(h1b) < 3:	
					break
				header1 = struct.unpack(">BBB",h1b)
				header_data = [] 
				header_data.append(self.dat_file.read(header1[2]))
				header2 = struct.unpack(">QII",self.dat_file.read(16))
				self.dat_file.seek(header2[2],1)
				record_offsets.append(self.dat_file.tell())
		except EOFError:
			pass
		return record_offsets[:-1]
						
	def record(self,offset):
		self.dat_file.seek(offset,0)
		# Header 1
		# byte Start of Record [0]
		# byte Dunno [1]
		# byte Length of File Name [2]
		# Header 2
		# long Unix Timestamp in milliseconds [0]
		# int Dunno [1]
		# int Length of Data [2]
		header1 = struct.unpack(">BBB",self.dat_file.read(3))
		header_data = [] 
		header_data.append(self.dat_file.read(header1[2]))
		header2 = struct.unpack(">QII",self.dat_file.read(16))
		data = self.dat_file.read(header2[2])
		return Record(header1,header2,header_data, data)
		
	def close(self):
		self.dat_file.close()

class Record:
	def __init__(self,header1,header2,header_data,data):
		self.header1 = header1
		self.header2 = header2
		self.header_data = header_data
		self.data = data
	
	def data(self):
		return self.data
	
	def thumb(self):
		if self.data[0].encode("hex") == "00":
			tmpdatalen = struct.unpack(">H",self.data[3:5])
			tmpdata = self.data[5:tmpdatalen[0]+5]
			return tmpdata
		else:
			return self.data
		
	def header1(self):
		return self.header1
	
	def header2(self):
		return self.header2
	
	def name(self):
		return self.header_data[0]
	
	def gmt_timestamp(self):
		tz = time.timezone
		time_from_file = time.gmtime((self.header2[0]/1000)) 
		return time.asctime(time_from_file) + " (Device Time)"
	
	def sha1hash(self):
		s = hashlib.sha1()
		s.update(self.data)
		return s.hexdigest()
	
	def save_to_disk(self,path):
		thumbs_file = open(os.path.join(path,self.name()),'wb')
		thumbs_file.write(self.thumb())
		thumbs_file.close();

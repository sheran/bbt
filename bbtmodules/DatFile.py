#!/usr/bin/env python

# bbt.py v0.4b - BlackBerry BBThumbsXXXxXXX.key file parser
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

import time
import struct
import hashlib
import calendar

class DatFile:
	def __init__(self,dat_file):
		self.dat_file = open(dat_file,'rb')
	
	def is_valid(self):
		self.dat_file.seek(0,0)
		magic = (struct.unpack(">4s",self.dat_file.read(4)))[0].encode("hex").upper()
		valid = (True if magic == "22062009" else False)
		return valid
	
	def record(self,offset,record_id):
		self.dat_file.seek(offset,0)
		# Header layout is:
		# byte Start of Record [0]
		# int Record ID [1]
		# int Length of Path Name [2]
		# int Length of File Name [3]
		# int Length of Data [4]
		# long Hex timestamp in milliseconds [5]
		# int Dunno [6]
		# byte 0x00 [7]
		
		header = struct.unpack(">B4sIIIQIB",self.dat_file.read(30))
		header_data = [] 
		header_data.append(self.dat_file.read(header[2]))
		header_data.append(self.dat_file.read(header[3]))
		data = self.dat_file.read(header[4])
		if record_id == header[1].encode("hex").upper():
			return Record(header, header_data, data)
		else:
			return None
		
	def close(self):
		self.dat_file.close()

class Record:
	def __init__(self,header,header_data,data):
		self.header = header
		self.header_data = header_data
		self.data = data
	
	def data(self):
		return self.data
	
	def id(self):
		return self.header[1].encode("hex").upper()
	
	def name(self):
		return self.header_data[1]
	
	def path(self):
		return self.header_data[0]
	
	def gmt(self):
		tz = time.timezone
		time_from_file = time.gmtime((self.header[5]/1000)) 
		return time_from_file
	
	def gmt_timestamp(self):
		return time.asctime(self.gmt()) + " (Device Time)"

	def data_len(self):
		return self.header[4]
	
	def sha1hash(self):
		s = hashlib.sha1()
		s.update(self.data)
		return s.hexdigest()
	
	def save_to_disk(self,path):
		thumbs_file = open(path+"/"+self.name(),'wb')
		thumbs_file.write(self.data)
		thumbs_file.close();

# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#%############################################################
#%Regular package imports here
#%############################################################
import codecs
import cchardet
import inspect
import os

######################################################################
	
def split_path_filename_extension(full_file_path):
	"""
	split a full file name into path, fileName and suffix
	@param full_file_path
	@return a list containing the path (with a trailing slash added), the 
		file name (without the suffix) and the file suffix (without the 
		preceding dot)
	"""
	tmp = full_file_path.split('/')
	return '/'.join(tmp[:-1]) + '/', '.'.join(tmp[-1].split('.')[:-1]), tmp[-1].split('.')[-1]

######################################################################

def get_filename_only(full_file_path):
	"""
	@param full_file_path
	@return the file name minus the extension
	"""
	return ''.join(full_file_path.split('/')[-1].split('.')[:-1])

######################################################################

def get_filename(full_file_path):
	"""
	@param full_file_path
	@return the file name (including extension)
	"""
	return full_file_path.split('/')[-1]

######################################################################
######################################################################
### Raise exception (forceful error) if file doesn't exist
#####
#####
### Arguments:
##### file_path		- the full path of the file
#####
### Raise Exception:
##### if the file does not exist
######################################################################
######################################################################
def verify_file_exists(file_path):
	if not os.path.isfile(file_path):
		raise Exception("[" + inspect.getouterframes(inspect.currentframe())[1].function + "]: File '"+ file_path +"' does not exist")
	
######################################################################

def verify_or_make_dirs_for(file_path):
	if not os.path.exists(os.path.dirname(file_path)):
		try:
			os.makedirs(os.path.dirname(file_path))
			return True
		except OSError as exc: # Guard against race condition
			if exc.errno != errno.EEXIST:
				raise
	return True

######################################################################

def write_to_file(file_path, data_string):
	verify_or_make_dirs_for(file_path)
	f = os.open(file_path, os.O_WRONLY|os.O_CREAT)
	os.write(f, str(data_string).encode())
	os.close(f)

######################################################################

def read_from_file(file_path):
	f = os.open(file_path, os.O_RDONLY)
	#os.stat_result.st_size
	#sum(getsize(join(root, name)
	#os.path import join, getsize
	#os.stat(name, dir_fd=rootfd).st_size
	encoded_text = os.read(f, os.stat(file_path).st_size)
	os.close(f)
	encoding = cchardet.detect(encoded_text)
	return decode_file_text(encoded_text, encoding), encoded_text, encoding

######################################################################

def append_to_file(file_path, data_string):
	verify_or_make_dirs_for(file_path)
	f = os.open(file_path, os.O_WRONLY|os.O_CREAT|os.O_APPEND)
	os.write(f, str(data_string).encode())
	os.close(f)

######################################################################

def decode_file_text(encoded_text, encoding):
	if encoding['encoding'] == 'ASCII' or encoding['encoding'] == 'UTF-8':
		return encoded_text.decode(encoding='UTF-8')
	elif encoding['encoding'] == 'UTF-16':
		bom = codecs.BOM_UTF16
		if encoded_text.startswith(bom):
			encoded_text = encoded_text[len(bom):]#strip away the BOM
		return encoded_text.decode(encoding='UTF-16')
	elif encoding['encoding'] == 'UTF-16BE':
		bom = codecs.BOM_UTF16_BE
		if encoded_text.startswith(bom):
			encoded_text = encoded_text[len(bom):]#strip away the BOM
		return encoded_text.decode(encoding='UTF-16BE')
	elif encoding['encoding'] == 'UTF-16LE':
		bom = codecs.BOM_UTF16_LE
		if encoded_text.startswith(bom):
			encoded_text = encoded_text[len(bom):]#strip away the BOM
		return encoded_text.decode(encoding='UTF-16LE')
	else:
		raise Exception("File encoding is '"+str(encoding['encoding'])+"' and cannot be processed")

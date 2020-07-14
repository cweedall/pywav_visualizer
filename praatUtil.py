# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""

@package praatUtil This module contains some utility functions to seamlessly
	incorporate Praat analysis functionality into Python

@copyright GNU Public License
@author written 2009-2014 by Christian Herbst (www.christian-herbst.org) 
@author Partially supported by the SOMACCA advanced ERC grant, University of Vienna, 
	Dept. of Cognitive Biology

@note
This program is free software; you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software 
Foundation; either version 3 of the License, or (at your option) any later 
version.
@par
This program is distributed in the hope that it will be useful, but WITHOUT 
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
@par
You should have received a copy of the GNU General Public License along with 
this program; if not, see <http://www.gnu.org/licenses/>.

"""
#%############################################################
#%Regular Python package imports here
#%############################################################
import math
import numpy
import os
import time
#%############################################################
#% Local file imports here
#%############################################################
import global_values
import global_path_helper
import generalUtility
import praatTextGrid

######################################################################

def readIntensityTier(fileName, startTime=0, endTime=-1):
	"""
	reads Praat Intensity data, saved as "short text file" within Praat
	@param fileName
	@return a tuple containing two lists: the time offset, and the 
		corresponding Intensity data
	"""
	dataX, dataY, metaData = readPraatShortTextFile(fileName, 'Intensity', startTime=startTime, endTime=endTime)
	return dataX, dataY

######################################################################

def readPitchTier(fileName, startTime=0, endTime=-1):
	"""
	reads Praat PitchTier data, saved as "short text file" within Praat
	@param fileName
	@return a tuple containing two lists: the time offset, and the 
		corresponding F0 (inaccurately called "pitch" in Praat) data
	"""
	dataX, dataY, metaData = readPraatShortTextFile(fileName, 'PitchTier', startTime=startTime, endTime=endTime)
	return dataX, dataY
	
######################################################################

def readPraatShortTextFile(fileName, obj, startTime=0.0, endTime=-1):
	""" 
	this function reads a Praat pitch tier file (saved as a 'short text file')
	@param fileName
	@param obj the file type. Currently we support these file types (as defined
		internally by Praat):
			- Harmonicity 2
			- PitchTier
			- Intensity
			- SpectrumTier
			- Spectrum 2
			- Cepstrum 1
	@return a two-dimensional array of floats, the first row 
		(index = 0) representing the time offsets of data values, and the 
		second row representing the detected fundamental frequency values 
	"""
	cnt = 0
	dataX = []
	dataY = []
	### If start time for .wav file was specified, add a junk data point
	##### This is useful to make sure the points fit properly on the x-axis and y-axis
	if startTime > 0.0:
		dataX.append(startTime-1000000)
		dataY.append(0)
	dataIdx = 0
	timeStep = 0
	timeOffset = 0
	
	arrFileTypes = ['Harmonicity 2', 'PitchTier', 'Intensity', 'SpectrumTier', 'Spectrum 2', 'Cepstrum 1']
	
	if not obj in arrFileTypes:
		raise Exception('readPraatShortTextFile - file type must be: ' + ', '.join(arrFileTypes))
	metaData = []
	
	decoded_text, _ , _ = global_path_helper.read_from_file(fileName)
	for line in decoded_text.splitlines():
		cnt += 1
		
		if cnt > 6:#Most lines are above 6, so more efficient to check this first
			if obj == 'Harmonicity 2' or obj == 'Intensity 2':
				if cnt > 13:
					val = float(line)
					if val > -100:
						dataY.append(val)
					else:
						dataY.append(None)
					dataX.append(timeOffset + float(dataIdx) * timeStep)
					dataIdx += 1
				elif cnt == 7:
					timeStep = float(line)
				elif cnt == 8:
					timeOffset = float(line)
			elif cnt % 2 == 0:
				dataY.append(float(line))
				dataIdx += 1
			else:
				dataX.append(float(line))
		elif cnt == 1 and line != "File type = \"ooTextFile\"":#First line of file - specifies ooTextFile
			raise Exception ("file " + fileName + " is not a Praat tier file")
		elif cnt == 2:#Second line of file - specifies Object class
			if obj == 'Harmonicity' and line != "Object class = \"Harmonicity\"" and line != "Object class = \"Harmonicity 2\"":
				raise Exception ("file " + fileName + " is not a Praat " + obj + " file, but claims to be (Harmonicity)")
			elif obj == 'Intensity' and line != "Object class = \"IntensityTier\"" and line != "Object class = \"Intensity 2\"":
				raise Exception ("file " + fileName + " is not a Praat " + obj + " file, but claims to be (Intensity)")
			elif line[:14] != "Object class =":
				raise Exception ("file " + fileName + " is not a Praat " + obj + " file, but claims to be")
		elif cnt == 6 and line[0:15] == 'points: size = ':
			raise Exception ("only the 'short text file' type is supported. " + " Save your Praat " + obj + " with 'Write to short text file.") 
		elif cnt > 3:
			metaData.append(line)
	### If end time for .wav file was specified, add a junk data point
	##### This is useful to make sure the points fit properly on the x-axis and y-axis
	if endTime != -1.0:
		dataX.append(endTime+1000000)
		dataY.append(0)
	return (numpy.array(dataX), numpy.array(dataY), metaData)

######################################################################

class PraatFormants:
	"""
	a class to store/process Praat formants
	"""

	DO_DEBUG = False#True
	
	# ---------------------------------------------------------------------- #

	def __init__(self):
		self.clear()
	
	# ---------------------------------------------------------------------- #
	
	def clear(self):
		"""
		resets the object's state 
		"""
		self.xmin = None
		self.xmax = None
		self.nx = None
		self.dx = None
		self.x1 = None
		self.arrX = []
		self.arrData = []
	
	# ---------------------------------------------------------------------- #
		
	def getNumFrames(self):
		"""
		@return the number of frames
		"""
		return self.nx
	
	# ---------------------------------------------------------------------- #
	
	def get(self, idx):
		"""
		@param idx 
		@return a tuple containing the time offset and the formant data at 
			that particular temporal offset. the formant data is a list of
			dictionaries (one for each formant), the latter contaning a 
			'bandwidth' and a 'frequency' parameter (both indicated in Hz)
		"""
		if idx < 0 or idx > self.nx or idx == self.nx:
			raise Exception("index out of range")
		return self.arrX[idx], self.arrData[idx]
	
	# ---------------------------------------------------------------------- #
	
	def getAllFormants(self):
		"""
		@return a list of dictionaries - the formant data
			(one for each formant), containing a 
			'bandwidth' and a 'frequency' parameter (both indicated in Hz)
		"""
		return self.arrData
	
	# ---------------------------------------------------------------------- #
	
	def decodeParam(self, txt, param, line = -1, fileName = ''):
		"""
		internally used ("pseudo-private") function used for reading Praat
		Formant files 
		@param txt the text (i.e., line from a file) that is being parsed.
			must have the structure 'paramName = paramValue'
		@param line only used for reporting errors (in case an error 
			actually arises during parsing txt)
		@param fileName only used for reporting errors (in case an error 
			actually arises during parsing txt)
		@return a floating point value
		"""
		data = txt.split('=')
		errMsg = ''
		if fileName != '':
			errMsg = ' of file "' + fileName + '"'
		if line > 0:
			errMsg = ' in line ' + str(line) + errMsg
		if len(data) != 2:
			raise Exception('cannot decode text "' + txt + '" - invalid structure' + errMsg)
		if data[0].strip() != param:
			raise Exception('expected parameter "' + param + '" but found "' + data[0].strip() + '"' + errMsg)
		return float(data[1])
	
	# ---------------------------------------------------------------------- #
	
	def read_short_formant_file_data(self, data, file_name):
		insideDataStructure = False
		dataCnt = 0
		intensity = None
		nFormants = None
		frequency = None
		bandwidth = None
		frameIdx = 0
		arrFormants = []
		#Pref is the reference value of sound pressure. Typically, it is assumed to be equal to 0.00002 Pa.
		reference_sound_pressure = 0.00002#Pascal (Pa)
		# -------------------------------------------------- #
		# short text file
		# -------------------------------------------------- #
		for line in data:
			if insideDataStructure:
				dataCnt += 1
				if dataCnt == 1:
					nFormants = float(line)
					if self.DO_DEBUG:
						print("\t\tnFormants: \n"+str(nFormants))
				else:
					tmpCnt = dataCnt - 2
					formantCount = int(tmpCnt / 2) + 1
					if tmpCnt % 2 == 0:
						frequency = float(line)
						if self.DO_DEBUG: 
							print("\t\tformant: "+str(formantCount))
						if self.DO_DEBUG: 
							print("\t\t\tfrequency: "+str(frequency))
					else:
						bandwidth = float(line)
						if self.DO_DEBUG: 
							print("\t\t\tbandwidth: "+str(bandwidth))
						arrFormants.append({
							'frequency':frequency,
							'bandwidth':bandwidth,
							'intensity':intensity,
							'intensity_dB':0 if intensity == 0 else 20*numpy.log10(numpy.divide(numpy.sqrt(intensity), reference_sound_pressure)),#20 * log (P/Pref)
							'frameIdx':frameIdx,
						})
						if formantCount == nFormants:
							# add the data here
							x = self.x1 + self.dx * (frameIdx - 1)
							self.arrX.append(x)
							self.arrData.append(arrFormants)
							insideDataStructure = False
							formantCount = 0
			else:
				dataCnt = 0
				insideDataStructure = True
				arrFormants = []
				intensity = float(line)
				frameIdx += 1
				if self.DO_DEBUG: 
					print("\tframeIdx: "+str(frameIdx))
					print("\t\tintensity: "+str(intensity))
	
	# ---------------------------------------------------------------------- #
	
	def read_long_formant_file_data(self, data, file_name):
		insideDataStructure = False
		dataCnt = 0
		intensity = None
		nFormants = None
		frequency = None
		bandwidth = None
		frameIdx = 0
		arrFormants = []
		errMsg = 'in file: ' + file_name
		# -------------------------------------------------- #
		# long text file
		# -------------------------------------------------- #
		lineNum = 8
		for line in data:
			lineNum += 1
			if lineNum == 10 and line != 'frame []:':
				raise Exception('invalid file structure' + errMsg)
			else:
				if insideDataStructure:
					dataCnt += 1
					if dataCnt == 1:
						intensity = self.decodeParam(line, 'intensity', lineNum, fileName)
					elif dataCnt == 2:
						nFormants = int(self.decodeParam(line, 'nFormants', lineNum, fileName))
					elif dataCnt == 3 and line != 'formant []:':
						raise Exception('invalid file structure' + errMsg)
					else:
						tmpCnt = (dataCnt - 4)
						formantCount = tmpCnt / 3 + 1
						if tmpCnt % 3 == 0:
							if line[0:9] != 'formant [':
								raise Exception('invalid file structure' + errMsg)
							formantIdx = int(line.split('[')[1].split(']')[0])
							if self.DO_DEBUG: 
								print("\t\tformant: "+str(formantIdx))
							if formantIdx != formantCount:
								raise Exception('invalid file structure' + errMsg)
						elif tmpCnt % 3 == 1:
							frequency = self.decodeParam(line, 'frequency', lineNum, fileName)
							if self.DO_DEBUG: 
								print("\t\t\tfrequency:"+str(frequency))
						elif tmpCnt % 3 == 2:
							bandwidth = self.decodeParam(line, 'bandwidth', lineNum, fileName)
							if self.DO_DEBUG: 
								print("\t\t\tbandwidth:"+str(bandwidth))
							arrFormants.append({
								'frequency':frequency,
								'bandwidth':bandwidth,
							})
							# add the data here
							x = self.x1 + self.dx * (frameIdx - 1)
							self.arrX.append(x)
							self.arrData.append(arrFormants)
							insideDataStructure = False
				else:
					dataCnt = 0
					insideDataStructure = True
					arrFormants = []
					if line[0:7] != 'frame [':
						raise Exception('invalid file structure' + errMsg)
					frameIdx = int(line.split('[')[1].split(']')[0])
					if self.DO_DEBUG: print("\tframeIdx:"+str(frameIdx))
	
	# ---------------------------------------------------------------------- #
	
	def read_metadata(self, metadata_lines, file_name):
		isShortTextFile = False
		
		metadata_lines[0]
		
		if metadata_lines[0] != 'File type = "ooTextFile"':#Line 1
			raise Exception('expected \'File type = "ooTextFile"\' in line 1 of file "' + file_name + '"')
		
		if metadata_lines[1] != 'Object class = "Formant 2"':#Line 2
			raise Exception('expected \'Object class = "Formant 2"\' in line 2 of file "' + file_name + '"')
		
		if len(metadata_lines[3].split('=')) > 1:#Line 4 of file
			isShortTextFile = False
			if metadata_lines[3].split('=')[0].strip() != 'xmin':
				raise Exception('invalid file structure, in line 4 of file "' + file_name + '"')
			self.xmin = self.decodeParam(metadata_lines[3], 'xmin', 4, file_name)
		else:#Line 4 of file
			isShortTextFile = True
			self.xmin = float(metadata_lines[3])
		
		if isShortTextFile:
			self.xmax = float(metadata_lines[4])#Line 5 of file
			self.nx = int(metadata_lines[5])#Line 6 of file
			self.dx = float(metadata_lines[6])#Line 7 of file
			self.x1 = float(metadata_lines[7])#Line 8 of file
			self.maxnFormants = float(metadata_lines[8])#Line 9 of file
		else:#Long file
			self.xmax = self.decodeParam(metadata_lines[4], 'xmax', 5, file_name)#Line 5 of file
			self.nx = int(self.decodeParam(metadata_lines[5], 'nx', 6, file_name))#Line 6 of file
			self.dx = self.decodeParam(metadata_lines[6], 'dx', 7, file_name)#Line 7 of file
			self.x1 = self.decodeParam(metadata_lines[7], 'x1', 8, file_name)#Line 8 of file
			self.maxnFormants = self.decodeParam(metadata_lines[8], 'maxnFormants', 9, file_name)#Line 9 of file
		return isShortTextFile
	# ---------------------------------------------------------------------- #
	
	def readFile(self, fileName):
		"""
		@todo bug when opening a "long text file"
		@todo refactor this code, it's ugly to look at (too many if 
			statements and indentations)
		"""
		self.clear()
		
		decoded_text, _ , _ = global_path_helper.read_from_file(fileName)
		
		if self.read_metadata(decoded_text.splitlines()[:9], fileName):
			self.read_short_formant_file_data(decoded_text.splitlines()[9:], fileName)
		else:
			self.read_long_formant_file_data(decoded_text.splitlines()[9:], fileName)
		
		decoded_text = None
		
		# check the data
		if len(self.arrX) != len(self.arrData):
			raise Exception("data array sizes don't match!")
		if self.nx != len(self.arrX):
			raise Exception('\nfile "' + fileName + '" promised to contain ' + str(self.nx) + ' frames, but only ' + str(len(self.arrX)) + ' were found')

######################################################################

def calculatePitch(wav_file_path,
					startTime = 0.0,
					endTime = -1,
					timeStep = 0.0,#Praat default is 0.0
					fMin = 60,
					fMax = 600,
					veryAccurate = False,#Praat default is False
					silenceThreshold = 0.0295,#Praat default is 0.03
					voicingThreshold = 0.45,#Praat default is 0.45
					octaveCost = 0.01,#Praat default is 0.01
					octaveJumpCost = 0.25,#Praat default is 0.35
					voicedUnvoicedCost = 0.26,#Praat default is 0.14
					keepPraatScriptFile = False):
	"""
	Utility function to calculate the time-varying fundamental frequency of
	the specified wave file using Praat's 
	<a href="http://www.fon.hum.uva.nl/praat/manual/Sound__To_Pitch__ac____.html">
	To Pitch (ac)...</a> method
	@param wav_file_path input file name
	@param timeStep see Praat's manual
	@param fMin see Praat's manual
	@param fMax see Praat's manual
	@param tmpDataPath the path for temporary files. if None, see @ref runPraatScript
	@param keepPitchTierFile if False, we'll remove the generated 
		PitchTier file and just return the Pitch data
	@param keepPraatScriptFile if False, we'll remove the temporary Praat
		script file
	
	@todo refactor so that this function uses the new @ref runPraatScript(...) 
		function
	@todo add tmpDataPath parameter
	"""
	wav_dir, filename_only, _ = global_path_helper.split_path_filename_extension(wav_file_path)
	pitchTierFileName = wav_dir + filename_only + '.PitchTier'

	txtAccurate = 'no'
	if veryAccurate: txtAccurate = 'yes'
	
	script = ''
	script += "Read from file... %s\n" % wav_file_path
	if startTime > 0 and endTime != -1:
		script += "Extract part... {:.7f} {:.7f} rectangular 1 yes\n".format(startTime, endTime)
	elif startTime > 0:
		script += "endTime = Get end time\n"
		script += "Extract part... {:.7f} endTime rectangular 1 yes\n".format(startTime)
	elif endTime != -1:
		script += "Extract part... 0 {:.7f} rectangular 1 yes\n".format(endTime)
	script += "To Pitch (ac)... %f %f 15 %s %f %f %f %f %f %f\n" % (timeStep,
																	fMin,
																	txtAccurate,
																	silenceThreshold,
																	voicingThreshold,
																	octaveCost,
																	octaveJumpCost,
																	voicedUnvoicedCost,
																	fMax)
	script += "Down to PitchTier\n"
	script += "Save as short text file... %s\n" % pitchTierFileName
	scriptFileName = 'tmp_pitch.praat'
	
	runPraatScript(script, scriptFileName)
	dataT, dataP = readPitchTier(pitchTierFileName, startTime=startTime, endTime=endTime)
	return dataT, dataP

######################################################################

def calculateIntensity(wav_file_path,
						startTime = 0.0,
						endTime = -1,
						fMin = 100,
						timeStep = 0,
						subtractMean = True,
						keepPraatScriptFile = False):
	"""
	call Praat's 
	<a href="http://www.fon.hum.uva.nl/praat/manual/Sound__To_Intensity___.html">
	To Intensity...</a> function to calculate the specified file's
	intensity.
	@param wav_file_path the name of the input file. needs to have a full path
		name if we should keep the IntensityTier file
	@param fMin [Hz] - see Praat's manual
	@param timeStep [s] - see Praat's manual
	@param subtractMean see Praat's manual
	@param tmpDataPath the path for temporary files. if None, see @ref runPraatScript
	@param keepIntensityTierFile if False, we'll remove the generated 
		IntensityTier file and just return the Intensity data
	@param keepPraatScriptFile if False, we'll remove the temporary Praat
		script file
	@return temporal and intensity information as returned by 
		@ref readIntensityTier()
	"""
	wav_dir, filename_only, _ = global_path_helper.split_path_filename_extension(wav_file_path)
	sSubtractMean = 'no'
	if subtractMean: sSubtractMean = 'yes'
	intensityTierFileName = wav_dir + filename_only + '.IntensityTier'
	script = ''
	script += "Read from file... %s\n" % wav_file_path
	if startTime > 0 and endTime != -1:
		script += "Extract part... {:.7f} {:.7f} rectangular 1 yes\n".format(startTime, endTime)
	elif startTime > 0:
		script += "endTime = Get end time\n"
		script += "Extract part... {:.7f} endTime rectangular 1 yes\n".format(startTime)
	elif endTime != -1:
		script += "Extract part... 0 {:.7f} rectangular 1 yes\n".format(endTime)
	script += "To Intensity: %f, %f, \"%s\"\n" % (fMin, timeStep, sSubtractMean)
	script += "Down to IntensityTier\n"
	script += "Save as short text file... %s\n" % intensityTierFileName
	scriptFileName = 'tmp_intensity.praat'
	
	runPraatScript(script, scriptFileName)
	dataT, dataI = readIntensityTier(intensityTierFileName, startTime=startTime, endTime=endTime)
	return dataT, dataI

##############################################################################

def runPraatScript(script, 
					scriptFileName = 'tmp.praat', 
					keepPraatScriptFile = False,
					tmpDataPath = global_values.python_build_dir,
					output_runtime = False):
	"""
	write the specified Praat script to a (temporary) script file and execute
	that script within Praat by making a system call. In order for this to 
	work properly, Praat must be installed and available at the command line.

	@param script a valid Praat script. lines are separated by newline 
		characters (backslash n)
	@param scriptFileName the name of the Praat script file that
		should be executed. DO NOT SUPPLY A PATH HERE!
	@param keepPraatScriptFile if False, the temporary script file will be
		deleted after execution
	@param tmpDataPath where the temporary script file is saved. If None, Python
		will look for the current user's path and append 'tmp' (and if that 
		resulting path is not found, it will be created automatically)
	@throw throws an error if the script execution fails
	@return the time (milliseconds) it took to execute the Praat script
	"""
	if tmpDataPath is None:
		tmpDataPath = global_values.python_build_dir
	
	global_path_helper.verify_or_make_dirs_for(tmpDataPath + scriptFileName)
	global_path_helper.write_to_file(tmpDataPath + scriptFileName, script)
	
	args = ['Praat', tmpDataPath + scriptFileName]
	
	start_time = time.perf_counter()
	
	msg = generalUtility.makeSystemCall(args)
	if msg != '':
		raise Exception("Error executing Praat script: " + str(msg))
	if not keepPraatScriptFile:
		os.remove(tmpDataPath + scriptFileName)
		os.rmdir(tmpDataPath)
	
	if output_runtime:
		runtimes_output = '------------------------------------\n'
		runtimes_output += 'Runtimes for ' + scriptFileName + '\n'
		runtimes_output += 'Script:\n' + script + '\n'
		runtimes_output += 'runtime: {:.7f}\n'.format(time.perf_counter() - start_time)
		runtimes_output += '\n'
		global_path_helper.append_to_file(global_values.python_runtimes_dir + 'runPraatScript.log', runtimes_output)

######################################################################

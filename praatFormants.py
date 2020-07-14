# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#%############################################################
#%Regular Python package imports here
#%############################################################
import matplotlib.pyplot as plt
import numpy
import pathlib
import re
import warnings

#%############################################################
#% Local file imports here
#%############################################################
import global_values
import global_path_helper
import audio_file_helper
import praatTextGrid
import praatUtil

#maxFrequency=5000-5500 - Men
#maxFrequency=5500-6000 - Women
#maxFrequency=7500-8500 - children
def scatterPlotFormants(wav_file_path,
						maxFormantFrequency=5500,#Praat default is 5500 Hz
						windowLength=0.025,#Praat default is 0.025
						dynamicRange=30,#Praat default is 30 dB
						showTextgridFormants=False,
						ax=None):
	####################################################################################
	### Check and fix arguments for problems OR to set default values (if necessary)
	####################################################################################
	##----------------------------------------------------------------------##
	### No audio file specified... can't do anything
	##----------------------------------------------------------------------##
	if wav_file_path is None or wav_file_path == "":
		raise Exception("praatFormants.py->scatterPlotFormants: No audio filename provided")

	##----------------------------------------------------------------------##
	### Check that the specified file actually exists
	##----------------------------------------------------------------------##
	global_path_helper.verify_file_exists(wav_file_path)

	# assemble a Praat script to analyze the formants of the file. Make sure that 
	# you add a backslach in front of every single quote of your Praat script (i.e.,
	# every ' turns into /' - this does not apply here, since the Praat script below 
	# does not contain any single quotes). Also, add a new line (backslash n) at the
	# end of every line in the script
	#
	# In particular, we'll create the script below. Note how the path and file names
	# are being replaced by variables, so that you can easily change them.
	# 
	# do ("Read from file...", "/Users/ch/data/programming/python/lib/demo/AEIOU_vocalFry.wav")
	# do ("To Formant (burg)...", 0, 5, 5000, 0.025, 50)
	# do ("Save as short text file...", "/Users/ch/data/programming/python/lib/demo/AEIOU_vocalFry.Formant")
	
	if maxFormantFrequency == None:
		maxFormantFrequency = 5500
	if windowLength == None:
		windowLength = 0.025
	if dynamicRange == None:
		dynamicRange = 12.5
	
	wav_dir, filename_only, _ = global_path_helper.split_path_filename_extension(wav_file_path)
	formant_file_path = wav_dir + filename_only + '.Formant'
	textgrid_file_path = wav_dir + filename_only + '.TextGrid'
	
	script = ''
	script += 'do ("Read from file...", "' +  wav_file_path + '")\n'
	#five arguments: 
	##### the time step,
	##### the maximum number of formants,
	##### the maximum hertz,
	##### the window length,
	##### Pre-emphasis from (Hz) 
	script += 'do ("To Formant (burg)...", 0, 5, '+'{:.2f},'.format(maxFormantFrequency)+' 0.025, 50)\n'
	script += 'do ("Save as short text file...", "' + str(formant_file_path) + '")\n'
	scriptFileName = 'tmp_formants.praat'
	praatUtil.runPraatScript(script, scriptFileName)


	# read the generated Praat formants file
	formants = praatUtil.PraatFormants()
	formants.readFile(formant_file_path)
	
	if showTextgridFormants:#First, verify .TextGrid file exists
		# read the accompanying Praat text grid (see the Praat TextGrid example for an
		# extended documentation). We expect a TextGrid that contains one IntervalTier
		# lableled 'vowels'. Within this IntervalTier, the occurring vowels are indicated
		textGrid = praatTextGrid.PraatTextGrid(0, 0)
		textGridFile = pathlib.Path(textgrid_file_path)

		if not textGridFile.exists():
			showTextgridFormants = False
			warnings.warn("File '"+str(textgrid_file_path)+"' does not exist.\n")
			warnings.warn("Continuing to show ALL formants (despite flag for .TextGrid file being true)\n")
	if showTextgridFormants:	
		arrTiers = textGrid.readFromFile(textgrid_file_path)
		numTiers = len(arrTiers)
		if numTiers != 1:
			raise Exception("we expect exactly one Tier in this file")
		tier = arrTiers[0]
		if tier.getName() != 'vowels':
			raise Exception("unexpected tier")
	
		# parse the TextGrid: create a dictionary that stores a list of start and end
		# times of all intervals where that particular vowel occurs (that way we'll
		# cater for multiple occurrances of the same vowel in a file, should that ever 
		# happen)
		arrVowels = {}
		for i in range(tier.getSize()):
			if tier.getLabel(i) != '':
				interval = tier.get(i)
				vowel = interval[2]
				if not vowel in arrVowels: 
					arrVowels[vowel] = []
				tStart, tEnd = interval[0], interval[1]
				arrVowels[vowel].append([tStart, tEnd]) 

	n = formants.getNumFrames()
	arrFormants = {}
	arrGraphData = {}
	xtimes = []
	yfrequency = []
	
	intensities = []
	for formantFrames in formants.getAllFormants():
		for formant_dict in formantFrames:
			intensities.append(formant_dict.get('intensity_dB'))
	max_intensity = numpy.amax(intensities)
	intensities = None
	
	for i in range(n):
		t, formantData = formants.get(i)
		if showTextgridFormants:#SHOW ONLY TEXTGRID FORMANTS
			# loop over all vowels and all intervals for each vowel
			for vowel in arrVowels:
				for tStart, tEnd in arrVowels[vowel]:
					if t >= tStart and t <= tEnd:
						for formant in formantData:
							xtimes.append(t)
							yfrequency.append(formant['frequency'])
		else:#SHOW ALL FORMANTS
			for index, formant in enumerate(formantData):
				if index > 0 and formant['intensity_dB'] > max_intensity-dynamicRange/2:
					xtimes.append(t)
					yfrequency.append(formant['frequency'])
	
	
	
	if ax == None:
		plt.scatter(numpy.array(xtimes), numpy.array(yfrequency), marker="D", s=12, c='w', edgecolor='b', linewidth=0.65, zorder=3)
	else:
		ax.scatter(numpy.array(xtimes), numpy.array(yfrequency), marker="D", s=12, c='w', edgecolor='b', linewidth=0.65, zorder=3)

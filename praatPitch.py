# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#%############################################################
#%Regular Python package imports here
#%############################################################
import math
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy
import scipy.signal
#%############################################################
#% Local file imports here
#%############################################################
import global_values
import global_path_helper
import audio_file_helper
import praatUtil

######################################################################
######################################################################
### Plot pitch on a spectrogram subplot from an audio .wav file
#####
#####
### Arguments:
##### wav_file_path			- name of the .wav file (stored in the audio subdirectory from .tex file)
##### startTime				- beginning point of .wav file to plot from
##### endTime				- ending point of .wav file to plot to
##### minViewFrequency		- minimum view frequency (of spectrogram)
##### maxViewFrequency		- maximum view frequency (of spectrogram)
##### timeStep				- frequency of data points (Praat default is 0.0)
##### minPitchHz			- (Praat default is 75 Hz)
##### maxPitchHz			- (Praat default is 600 Hz)
##### veryAccurate			- (Praat default is False)
##### silenceThreshold		- (Praat default is 0.03)
##### voicingThreshold		- (Praat default is 0.45)
##### octaveCost			- (Praat default is 0.01)
##### octaveJumpCost		- (Praat default is 0.35)
##### voicedUnvoicedCost	- (Praat default is 0.14)
##### normalizePitch		- need to normalize pitch for spectrograms, but not pitch plots
##### ax					- the axis (i.e. of a subplot) where to plot pitch data
#####
### Returns:
##### (nothing)
######################################################################
######################################################################
def plotSpectrogramPitch(wav_file_path,
							startTime=0.0,
							endTime=-1,
							minViewFrequency=0.0,
							maxViewFrequency=5000.0,
							timeStep=0.0,#Praat default is 0.0
							minPitchHz=75,#Praat default is 75
							maxPitchHz=600.0,#Praat default is 600
							veryAccurate = False,#Praat default is False
							silenceThreshold = 0.0295,#Praat default is 0.03
							voicingThreshold = 0.45,#Praat default is 0.45
							octaveCost = 0.01,#Praat default is 0.01
							octaveJumpCost = 0.25,#Praat default is 0.35
							voicedUnvoicedCost = 0.26,#Praat default is 0.14
							normalizePitch = False,#Need to normalize pitch for spectrograms, but not pitch plots
							ax=None):
	####################################################################################
	### Check and fix arguments for problems OR to set default values (if necessary)
	####################################################################################
	##----------------------------------------------------------------------##
	### No audio file specified... can't do anything
	##----------------------------------------------------------------------##
	if wav_file_path is None or wav_file_path == '':
		raise Exception("praatPitch.py->plotSpectrogramPitch: No audio filename provided")
	
	##----------------------------------------------------------------------##
	### Check that the specified file actually exists
	##----------------------------------------------------------------------##
	global_path_helper.verify_file_exists(wav_file_path)
	
	### Set minimum viewing frequency for pitch to 0 Hz, if not set properly
	if minViewFrequency == None:
		minViewFrequency = 0.0
	### Set maximum viewing frequency for pitch to 5000 Hz, if not set properly
	if maxViewFrequency == None:
		maxViewFrequency = 5000.0
	### Set minimum pitch to 75 Hz, if not set properly
	if minPitchHz == None:
		minPitchHz = 75.0
	### Set maximum pitch to 75 Hz, if not set properly
	if maxPitchHz == None:
		maxPitchHz = 600.0
	
	##----------------------------------------------------------------------##
	### Create a plot object which is either matplotlib.pyplot (if the axis argument was not specified)
	##### or matplotlib.ax.Axis (if the axis argument was specified)
	##----------------------------------------------------------------------##
	if ax == None or ax is None:
		the_plot = plt
	else:
		the_plot = ax
	
	####################################################################################
	### Calculate all pitches using Praat in the audio file (within start/end times)
	##### and then break the pitches into continuous intervals
	####################################################################################
	##----------------------------------------------------------------------##
	### Have Praat calculate all times and pitches (F0) for audio file
	##----------------------------------------------------------------------##
	times, pitches = praatUtil.calculatePitch(wav_file_path,
												startTime=startTime,
												endTime=endTime,
												timeStep=timeStep,
												fMin=minPitchHz,
												fMax=maxPitchHz,
												veryAccurate = veryAccurate,
												silenceThreshold = silenceThreshold,
												voicingThreshold = voicingThreshold,
												octaveCost = octaveCost,
												octaveJumpCost = octaveJumpCost,
												voicedUnvoicedCost = voicedUnvoicedCost)
	
	##----------------------------------------------------------------------##
	### If the start time is not specified OR is less than the minimum one in Praat data, 
	##### then use the first time of the Praat data
	##----------------------------------------------------------------------##
	if startTime is None or startTime == 0.0 or startTime < times[0]:
		startTime = times[0]
	##----------------------------------------------------------------------##
	### If the end time is not specified OR is greater than the maximum one in Praat data, 
	##### then use the last time of the Praat data
	##----------------------------------------------------------------------##
	if endTime is None or endTime == -1 or endTime > times[-1]:
		endTime = times[-1]
	##----------------------------------------------------------------------##
	### If the timeStep is not specified OR is 0.0, 
	##### then use the time step determined by the Praat data
	##### Ignore the first time, because may be junk (due to start/end time being specified)
	##----------------------------------------------------------------------##
	if timeStep is None or int(timeStep) == 0:
		timeStep = times[2]-times[1]
	
	####################################################################################
	### Separate continuous data into different lists, and store each list
	##### in a single large list
	####################################################################################
	### List of each continuous time list
	croppedTimes = []
	### List of each continuous pitch list
	croppedPitches = []
	### (Temporary) list of continuous time
	nobreakTimes = []
	### (Temporary) list of continuous time
	nobreakPitches = []
	##----------------------------------------------------------------------##
	### Loop through pitch data (which was calculated by Praat)
	##----------------------------------------------------------------------##
	for index, pitch in enumerate(pitches):
		##----------------------------------------------------------------------##
		### Only use data within the specified start/end time range
		##----------------------------------------------------------------------##
		if times[index] >= startTime and times[index] <= endTime:
			##----------------------------------------------------------------------##
			### If the difference of time between last an current timestamp
			##### is approximately the time step used by Praat to calculate data
			##### then we assume it is continuous.
			##### Therefore, continue adding to the (temporary) continuous data list
			##----------------------------------------------------------------------##
			if index > 0 and (times[index]-times[index-1]) <= (timeStep*3):
				nobreakTimes.append(times[index])
				nobreakPitches.append(pitch)
			##----------------------------------------------------------------------##
			### Otherwise, it appears we reached a new set of continuous data.
			##### Therefore, store the previous continuous data list into the overall
			##### list of times and pitches.
			##----------------------------------------------------------------------##
			#elif nobreakTimes is not [] and nobreakPitches is not []:
			else:
				croppedTimes.append(nobreakTimes)
				croppedPitches.append(nobreakPitches)
				nobreakTimes = []
				nobreakPitches = []
	##----------------------------------------------------------------------##
	### Make sure that if the final list of continuous data is stored,
	##### in case it wasn't inside the above FOR loop.
	##----------------------------------------------------------------------##
	if len(nobreakTimes) > 0:
		croppedTimes.append(nobreakTimes)
		croppedPitches.append(nobreakPitches)
		nobreakTimes = []
		nobreakPitches = []
	
	####################################################################################
	### Calculate the normalized pitch frequencies so that they fit properly on
	##### a spectrogram.
	####################################################################################
	normalizedPitches = []
	normalizedNobreakPitches = []
	##----------------------------------------------------------------------##
	### Only normalize if instructed to do so
	##----------------------------------------------------------------------##
	if normalizePitch:
		##----------------------------------------------------------------------##
		### Need to iterate through each of the continuous data lists
		##----------------------------------------------------------------------##
		for eachPitchList in croppedPitches:
			##----------------------------------------------------------------------##
			### Iterate through continuous pitch data
			##----------------------------------------------------------------------##
			for pitch in eachPitchList:
				##----------------------------------------------------------------------##
				#### Calculate the normalized pitch frequency
				##### and store in temporary, continuous pitch data list
				##----------------------------------------------------------------------##
				normalizedNobreakPitches.append(((pitch-minPitchHz)/(maxPitchHz-minPitchHz)) * (maxViewFrequency-minViewFrequency))
			### Append continuous data list to list of all continuous pitches
			normalizedPitches.append(normalizedNobreakPitches)
			### Reset the temporary normalized continuous pitch data list
			normalizedNobreakPitches = []
	##----------------------------------------------------------------------##
	### We were instructed not to normalize
	##----------------------------------------------------------------------##
	else:
		normalizedPitches = croppedPitches
	
	####################################################################################
	### Loop through each set of continuous data points (for pitch)
	##### and plot each continuous line.
	####################################################################################
	for index, timeArray in enumerate(croppedTimes):
		the_plot.plot(numpy.array(timeArray),
						numpy.array(normalizedPitches[index]),
						c='b',
						linewidth=2,
						path_effects=[pe.Stroke(linewidth=4, foreground='w'), pe.Normal()],
						zorder=2)
	##----------------------------------------------------------------------##
	### Setup the y-axis
	##----------------------------------------------------------------------##
	# Set minimum and maximum x-axis values
	the_plot.set_ylim(minViewFrequency, maxViewFrequency)

#####################################################################
######################################################################
### Plot only pitch from an audio .wav file
#####
#####
### Arguments:
##### wav_file_path			- name of the .wav file (stored in the audio subdirectory from .tex file)
##### startTime				- beginning point of .wav file to plot from
##### endTime				- ending point of .wav file to plot to
##### timeStep				- frequency of data points (Praat default is 0.0)
##### minPitchHz			- (Praat default is 75 Hz)
##### maxPitchHz			- (Praat default is 600 Hz)
##### silenceThreshold		- (Praat default is 0.03)
##### voicingThreshold		- (Praat default is 0.45)
##### octaveCost			- (Praat default is 0.01)
##### octaveJumpCost		- (Praat default is 0.35)
##### voicedUnvoicedCost	- (Praat default is 0.14)
##### removeMaximums		- a list of the indices of maximums that SHOULDN'T be plotted
##### ax					- the axis (i.e. of a subplot) where to plot pitch data
#####
### Returns:
##### (nothing)
######################################################################
######################################################################
def plotPurePitch(wav_file_path,
					startTime=0.0,
					endTime=-1,
					timeStep=0.0,#Praat default is 0.0
					minPitchHz=75,#Praat default is False
					maxPitchHz=600.0,#Praat default is 600
					silenceThreshold = 0.0295,#Praat default is 0.03
					voicingThreshold = 0.45,#Praat default is 0.45
					octaveCost = 0.01,#Praat default is 0.01
					octaveJumpCost = 0.25,#Praat default is 0.35
					voicedUnvoicedCost = 0.26,#Praat default is 0.14
					removeMaximums = [],
					ax=None):
	####################################################################################
	### Check and fix arguments for problems OR to set default values (if necessary)
	####################################################################################
	##----------------------------------------------------------------------##
	### No audio file specified... can't do anything
	##----------------------------------------------------------------------##
	if wav_file_path is None or wav_file_path == '':
		raise Exception("praatPitch.py->plotPurePitch: No audio filename provided")
	
	##----------------------------------------------------------------------##
	### Check that the specified file actually exists
	##----------------------------------------------------------------------##
	global_path_helper.verify_file_exists(wav_file_path)
	
	### Set minimum pitch to 75 Hz, if note set properly
	if minPitchHz == None:
		minPitchHz = 75.0
	### Set maximum pitch to 75 Hz, if note set properly
	if maxPitchHz == None:
		maxPitchHz = 600.0
	
	##----------------------------------------------------------------------##
	### Create a plot object which is either matplotlib.pyplot (if the axis argument was not specified)
	##### or matplotlib.ax.Axis (if the axis argument was specified)
	##----------------------------------------------------------------------##
	if ax == None or ax is None:
		the_plot = plt
	else:
		the_plot = ax
	
	####################################################################################
	### Calculate all pitches using Praat in the audio file (within start/end times)
	##### and then break the pitches into continuous intervals
	####################################################################################
	##----------------------------------------------------------------------##
	### Have Praat calculate all times and pitches (F0) for audio file
	##----------------------------------------------------------------------##
	times, pitches = praatUtil.calculatePitch(wav_file_path,
												startTime=startTime,
												endTime=endTime,
												timeStep=timeStep,
												fMin=minPitchHz,
												fMax=maxPitchHz,
												veryAccurate = True,
												silenceThreshold = silenceThreshold,
												voicingThreshold = voicingThreshold,
												octaveCost = octaveCost,
												octaveJumpCost = octaveJumpCost,
												voicedUnvoicedCost = voicedUnvoicedCost)
	##----------------------------------------------------------------------##
	### If the start time is not specified, then use the first time of the Praat data
	##### OTHERWISE, fix the list of times to start at the specified start time
	##----------------------------------------------------------------------##
	'''if startTime == 0.0:
		startTime = times[0]
	else:
		cropped_start_time = numpy.unravel_index((times>=startTime).argmax(), times.shape)[0]
		times = times[cropped_start_time:]
		pitches = pitches[cropped_start_time:]
	##----------------------------------------------------------------------##
	### Use the last time of the Praat data, if not specified
	##----------------------------------------------------------------------##
	if endTime == -1:
		endTime = times[-1]
	else:
		cropped_end_time = numpy.unravel_index((times>=endTime).argmax(), times.shape)[0]
		times = times[:cropped_end_time]
		pitches = pitches[:cropped_end_time]'''
	
	##----------------------------------------------------------------------##
	### If the start time is not specified OR is less than the minimum one in Praat data, 
	##### then use the first time of the Praat data
	##----------------------------------------------------------------------##
	if startTime is None or startTime == 0.0 or startTime < times[0]:
		startTime = times[0]
	##----------------------------------------------------------------------##
	### If the end time is not specified OR is greater than the maximum one in Praat data, 
	##### then use the last time of the Praat data
	##----------------------------------------------------------------------##
	if endTime is None or endTime == -1 or endTime > times[-1]:
		endTime = times[-1]
	##----------------------------------------------------------------------##
	### If the timeStep is not specified OR is 0.0, 
	##### then use the time step determined by the Praat data
	##### Ignore the first time, because may be junk (due to start/end time being specified)
	##----------------------------------------------------------------------##
	if timeStep is None or timeStep == 0.0:
		timeStep = times[2]-times[1]
	
	####################################################################################
	### Separate continuous data into different lists, and store each list
	##### in a single large list
	####################################################################################
	### List of each continuous time list
	croppedTimes = []
	### List of each continuous pitch list
	croppedPitches = []
	### (Temporary) list of continuous time
	nobreakTimes = []
	### (Temporary) list of continuous time
	nobreakPitches = []
	##----------------------------------------------------------------------##
	### Loop through pitch data (which was calculated by Praat
	##----------------------------------------------------------------------##
	for index, pitch in enumerate(pitches):
		##----------------------------------------------------------------------##
		### Only use data within the specified start/end time range
		##----------------------------------------------------------------------##
		if times[index] >= startTime and times[index] <= endTime:
			##----------------------------------------------------------------------##
			### If the difference of time between last an current timestamp
			##### is approximately the time step used by Praat to calculate data
			##### then we assume it is continuous.
			##### Therefore, continue adding to the (temporary) continuous data list
			##----------------------------------------------------------------------##
			if index > 0 and (times[index]-times[index-1]) <= (timeStep*3):
				nobreakTimes.append(times[index])
				nobreakPitches.append(pitch)
			##----------------------------------------------------------------------##
			### Otherwise, it appears we reached a new set of continuous data.
			##### Therefore, store the previous continuous data list into the overall
			##### list of times and pitches.
			##----------------------------------------------------------------------##
			#elif nobreakTimes is not [] and nobreakPitches is not []:
			else:
				croppedTimes.append(nobreakTimes)
				croppedPitches.append(nobreakPitches)
				nobreakTimes = []
				nobreakPitches = []
	##----------------------------------------------------------------------##
	### Make sure that if the final list of continuous data is stored,
	##### in case it wasn't inside the above FOR loop.
	##----------------------------------------------------------------------##
	if len(nobreakTimes) > 0:
		croppedTimes.append(nobreakTimes)
		croppedPitches.append(nobreakPitches)
		nobreakTimes = []
		nobreakPitches = []
	
	####################################################################################
	### Calculate minimum and maximum y-axis frequencies
	##### so that interval is always 10, 20, 30, etc.
	##### depending on how large the maximum and minimum are
	####################################################################################
	### Temporarily set minimum y-axis frequency to maximum Praat pitch frequency
	minViewFrequency = maxPitchHz
	### Temporarily set maximum y-axis frequency to minimum Praat pitch frequency
	maxViewFrequency = minPitchHz
	##----------------------------------------------------------------------##
	### Determine minimum/maximum pitch frequencies from the pitches calculated by Praat 
	##----------------------------------------------------------------------##
	for pitchList in croppedPitches:
		### Ignore, unless the list of continuous pitches contains data
		if pitchList is not None and pitchList != []:
			minViewFrequency = min(pitchList) if min(pitchList) < minViewFrequency else minViewFrequency
			maxViewFrequency = max(pitchList) if max(pitchList) > maxViewFrequency else maxViewFrequency
	
	##----------------------------------------------------------------------##
	### Using minimum and maximum pitches from Praat,
	##### - calculate the interval between y-axis ticks
	##### - calculate the minimum y-axis tick value
	##### - calculate the maximum y-axis tick value
	##----------------------------------------------------------------------##
	yaxisInterval = round(math.ceil((maxViewFrequency-minViewFrequency) / 100) * 100) / 10
	minViewFrequency = int(math.floor(minViewFrequency / yaxisInterval)) * yaxisInterval
	maxViewFrequency = int(math.ceil(maxViewFrequency / yaxisInterval)) * yaxisInterval
	
	####################################################################################
	### Loop through each set of continuous data points (for pitch)
	##### and plot each continuous line.
	##### Also plot the (local) maximum pitches for each continuous line
	##### with a red line and red text indicating the pitch maximum.
	####################################################################################
	# A counter for how many maximum pitches have been plotted
	maximum_counter = 0
	# Loop through the list of lists.  Outer list contains each list of continuous times
	for index, timeArray in enumerate(croppedTimes):
		# Get the corresponding list of continous pitches
		pitchArray = croppedPitches[index]
		# Ignore any empty lists
		if timeArray is not None and timeArray != [] \
			and pitchArray is not None and pitchArray != []:			
			##----------------------------------------------------------------------##
			### Plot a continuous list of pitches, with a blue line
			##----------------------------------------------------------------------##
			the_plot.plot(numpy.array(timeArray),
						numpy.array(pitchArray),
						c='b',
						linewidth=2,
						path_effects=[pe.Stroke(linewidth=4, foreground='w'), pe.Normal()],
						zorder=2)
			
			####################################################################################
			### Plot a line and the numerical value for a (local) maximum pitch
			##### near the point in the plot of pitches
			####################################################################################
			#(Added an extra element at the beginning and end of the pitch list)
			#(->this is to help with finding local maximum pitches at the beginning/end of a line)
			prev_index_of_max = -1
			for index_of_max in scipy.signal.argrelextrema(numpy.array([0]+pitchArray+[0]), numpy.greater)[0]:
				index_of_max -= 1# Because we added an extra element, need to access the previous element in time and pitch lists
				# Make sure we only added maximums that are not excluded
				if maximum_counter not in removeMaximums:
					##----------------------------------------------------------------------##
					### Plot a small horizontal at the pitch maximum 
					##----------------------------------------------------------------------##
					red_line_xvalues = [timeArray[index_of_max],
										timeArray[index_of_max] + ((endTime-startTime) * 0.02),
										timeArray[index_of_max] + ((endTime-startTime) * 0.11)]
					
					red_line_height_percent = 0.05
					if prev_index_of_max > -1 and (timeArray[index_of_max] - timeArray[prev_index_of_max] < ((endTime-startTime) * 0.11)):
						red_line_height_percent = 0.025
					upper_red_line_yvalue = pitchArray[index_of_max]+(maxViewFrequency-minViewFrequency)*red_line_height_percent
					
					red_line_yvalues = [pitchArray[index_of_max],
										upper_red_line_yvalue,
										upper_red_line_yvalue]
					the_plot.plot(numpy.array(red_line_xvalues),
								numpy.array(red_line_yvalues),
								c='r',
								linewidth=0.85,
								clip_on=False,
								zorder=2)
					##----------------------------------------------------------------------##
					### Add text (on the line) indicating the pitch maximum 
					##----------------------------------------------------------------------##
					the_plot.text(timeArray[index_of_max]+((endTime-startTime) * 0.065),
									upper_red_line_yvalue + (maxViewFrequency-minViewFrequency)*0.005,
									"{:.2f} Hz".format(pitchArray[index_of_max]),
									fontproperties=global_values.text_fontproperties,
									size=global_values.text_font_size,
									color='red',
									horizontalalignment='center',
									path_effects=[pe.Stroke(linewidth=0.45, foreground='k'), pe.Normal()],
									zorder=2)
					
					prev_index_of_max = index_of_max
				# Make sure we keep track of which maximum pitch has been plotted
				maximum_counter += 1
	
	##----------------------------------------------------------------------##
	### Setup the x-axis
	##----------------------------------------------------------------------##
	# Set minimum and maximum x-axis values
	the_plot.set_xlim([float("{:.4f}".format(startTime)), float("{:.4f}".format(endTime))])
	# Only allow x-axis ticks for the start and end times
	plt.xticks([float("{:.4f}".format(startTime)), float("{:.4f}".format(endTime))], [float("{:.4f}".format(startTime)), float("{:.4f}".format(endTime))])
	
	##----------------------------------------------------------------------##
	### Setup the y-axis
	##----------------------------------------------------------------------##
	# Set minimum and maximum x-axis values
	the_plot.set_ylim(minViewFrequency, maxViewFrequency)
	# Set up y-axis ticks to always display maximum and minimum values
	### and also have an a calculated interval (i.e. yaxisInterval)
	plt.yticks(numpy.arange(minViewFrequency, maxViewFrequency+yaxisInterval, yaxisInterval))

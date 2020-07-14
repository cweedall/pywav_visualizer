# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#%############################################################
#%Regular Python package imports here
#%############################################################
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy
#%############################################################
#% Local file imports here
#%############################################################
import global_values
import global_path_helper
import audio_file_helper
import praatUtil

######################################################################
######################################################################
### Plot intensity on a spectrogram subplot from an audio .wav file
#####
#####
### Arguments:
##### wav_file_path			- name of the .wav file (stored in the audio subdirectory from .tex file)
##### startTime				- beginning point of .wav file to plot from
##### endTime				- ending point of .wav file to plot to
##### minFrequency			- minimum view frequency (of spectrogram)
##### maxFrequency			- maximum view frequency (of spectrogram)
##### sampleRate			- the sample rate of the .wav file
##### limitToTextgrid		- ???
##### ax					- the axis (i.e. of a subplot) where to plot pitch data
#####
### Returns:
##### (nothing)
######################################################################
######################################################################
def plotIntensity(wav_file_path,
					startTime=0.0,
					endTime=-1,
					minFrequency=100,
					maxFrequency=5000.0,
					sampleRate=None,
					limitToTextgrid=False,
					ax=None):
	####################################################################################
	### Check and fix arguments for problems OR to set default values (if necessary)
	####################################################################################
	##----------------------------------------------------------------------##
	### No audio file specified... can't do anything
	##----------------------------------------------------------------------##
	if wav_file_path is None or wav_file_path == '':
		raise Exception("praatIntensity.py->plotIntensity: No audio filename provided")
	
	##----------------------------------------------------------------------##
	### Check that the specified file actually exists
	##----------------------------------------------------------------------##
	global_path_helper.verify_file_exists(wav_file_path)
	
	### Set minimum viewing frequency for pitch to 0 Hz, if not set properly
	if minFrequency == None:
		minFrequency = 100.0
	### Set maximum viewing frequency for pitch to 5000 Hz, if not set properly
	if maxFrequency == None:
		maxFrequency = 5000.0
	
	##----------------------------------------------------------------------##
	### Create a plot object which is either matplotlib.pyplot (if the axis argument was not specified)
	##### or matplotlib.ax.Axis (if the axis argument was specified)
	##----------------------------------------------------------------------##
	if ax == None or ax is None:
		the_plot = plt
	else:
		the_plot = ax
	
	####################################################################################
	### Calculate all intensities using Praat in the audio file (within start/end times)
	##### and then break the intensities into continuous intervals
	####################################################################################
	##----------------------------------------------------------------------##
	### Have Praat calculate all times and intensities for audio file
	##----------------------------------------------------------------------##
	times, intensities = praatUtil.calculateIntensity(wav_file_path,
														startTime=startTime,
														endTime=endTime,
														fMin = minFrequency,
														timeStep = 0.0,
														subtractMean = True)
	
	##----------------------------------------------------------------------##
	### If the start time is not specified OR is less than the minimum one in Praat data, 
	##### then use the first time of the Praat data
	##----------------------------------------------------------------------##
	if startTime == 0.0 or startTime < times[0]:
		startTime = times[0]
	else:
		cropped_start_time = numpy.unravel_index((times>=startTime).argmax(), times.shape)[0]
		times = times[cropped_start_time:]
		intensities = intensities[cropped_start_time:]
	##----------------------------------------------------------------------##
	### If the end time is not specified OR is greater than the maximum one in Praat data, 
	##### then use the last time of the Praat data
	##----------------------------------------------------------------------##
	if endTime == -1 or endTime > times[-1]:
		endTime = times[-1]
	else:
		cropped_end_time = numpy.unravel_index((times>=endTime).argmax(), times.shape)[0]
		times = times[:cropped_end_time]
		intensities = intensities[:cropped_end_time]
	
	####################################################################################
	### Normalize intensities onto the spectrogram
	####################################################################################
	### Minimum intensity of all intensities
	min_intensity = numpy.amin(intensities)
	### Maximum intensity of all intensities
	max_intensity = numpy.amax(intensities)
	intensities -= min_intensity
	intensities /= (max_intensity-min_intensity)
	intensities *= maxFrequency
	
	####################################################################################
	### Plot intensity data points
	####################################################################################
	the_plot.plot(times,
					intensities,
					c='y',
					linewidth=2,
					path_effects=[pe.Stroke(linewidth=6, foreground='k'), pe.Normal()],
					zorder=2)
	
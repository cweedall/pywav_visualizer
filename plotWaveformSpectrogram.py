# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#%############################################################
#% Regular package imports here
#%############################################################
import math
import matplotlib.cm
import matplotlib.colorbar
import matplotlib.colors as colors
import matplotlib.image
import matplotlib.patheffects
import matplotlib.pyplot as plt
import numpy
import re
import time
#%############################################################
#% Custom or unofficial package imports here
#%############################################################
import global_values
import global_path_helper
import audio_file_helper
import image_file_helper
import praatFormants
import praatIntensity
import praatPitch

######################################################################
######################################################################
### Create a waveform image/plot from an audio .wav file
###
###	
######################################################################
######################################################################
def create_waveform_from_wav_file(wav_file_path,
									startTime=0.0,
									endTime=-1,
									xaxisLabel="Time (s)",
									yaxisLabel="Relative Level",
									showXaxisLabel=True,
									showYaxisLabel=False,
									isSubplot=False,
									ax=None,
									annotations=[]):
	#####################
	### Make the figure (if not a subplot)
	#####################
	if not isSubplot:
		#Close other existing plots to avoid issues
		plt.close("all")
		#Tweak the figsize (width, height) in inches
		plt.figure(figsize=(global_values.figure_width, global_values.figure_height), dpi=global_values.image_DPI)
		ax=plt.gca()

	fig=plt.gcf()

	#####################
	### Load the data and calculate the time of each sample
	#####################
	samplerate, bitdepth, data, peakamplitude = audio_file_helper.get_samplerate_bitdepth_data_peakamplitude(wav_file_path, startTime, endTime)
	
	times = numpy.arange(len(data)) / float(samplerate)
	times += startTime
	
	# Determine the largest amplitude (either negative or positive) and
		# add a small padding.  
	data_max = max(numpy.absolute(numpy.amin(data)), numpy.absolute(numpy.amax(data)))
	normalized_data = numpy.multiply(numpy.divide(data, data_max), peakamplitude)

	#####################
	### Plot the times (x-axis) versus audio data (y-axis)
	###   -also set up plot
	#####################
	#Plot time values (x-axis) against amplitude values (y-axis)
	ax.plot([0,times[-1]], [0,0], color='k', zorder=0)#creates a 'false' x-axis at y=0
	ax.plot(times, normalized_data, color='k', zorder=0)
	
	samplerate, bitdepth, data, normalized_data = None, None, None, None

	##-----------------------------------##
	### General axes setup
	##-----------------------------------##
	customaxis(ax, c_bottom='none') #default: no right and top axis
	ax.set_axisbelow(True)
	ax.xaxis.set_tick_params(bottom=False)

	##-----------------------------------##
	### Set up the x-axis
	##-----------------------------------##
	if isSubplot:
		ax.set_xticklabels(labels="")
		xaxisLabel = ""
	if showXaxisLabel:
		set_audio_xaxis_start_end_times(times, ax, axisLabel=xaxisLabel, startTime=startTime, endTime=endTime)

	##-----------------------------------##
	### Set up the y-axis
	##-----------------------------------##

	# Specify the number of ticks that should exist on y-axis
	yaxisNumTicks = 6
	
	max_view_dB = peakamplitude * 1.025
	peakamplitude = None
	# Use as max and min y-axis values from previous step
	ax.set_ylim(-max_view_dB, max_view_dB)
	# Show min and max values and also zero for y-axis (plus evenly spaced ticks, if numTicks > 3)
		# the max_amp tick somehow doesn't show up...so I append it manually
	ax.set_yticks(numpy.append(numpy.arange(-max_view_dB, 
											max_view_dB, 
											(max_view_dB * 2)  / yaxisNumTicks), 
								[max_view_dB]))
	
	# Because waveform y-ticks are floats which many decimal places,
		# keep zero as '0' and truncate other tick labels to 5 decimal places
	newYaxisTickLabels = ax.get_yticks().tolist()
	for index, item in enumerate(newYaxisTickLabels):
		if item == 0 or item == 0. or abs(item) < 0.001:
			newYaxisTickLabels[index] = str('0 dB') #'0' instead of '0.0' (or '0.00', '0.000', etc.)
		else:
			newYaxisTickLabels[index] =  str("{:.2f} dB".format(abs(item)))
	ax.set_yticklabels(newYaxisTickLabels, fontproperties=global_values.axis_tick_fontproperties)

	# Show the y-axis label, if specified
	if showYaxisLabel:
		ax.set_ylabel(yaxisLabel,
						fontproperties=global_values.axis_label_fontproperties,
						fontsize=global_values.axis_label_font_size)
	
	##-----------------------------------##
	### Set up the gridlines
	##-----------------------------------##
	set_grid(ax, numIntermediateTicks=3, gridColor='#aaaaaa')

	##-----------------------------------##
	### Set up the annotations
	##-----------------------------------##
	for annIndex, annValues in enumerate(annotations):
		if annValues[0] == "range":
			add_range_annotation(ax, annValues[1], annValues[2], annValues[3], annValues[4], annValues[5], annValues[6], annValues[7] if len(annValues) > 6 else False, isSubplot=isSubplot)
		elif annValues[0] == "arrow":
			#add_arrow_annotation(ax, annValues[1], annValues[2], annValues[3], annValues[4], annValues[5], annValues[6] if len(annValues) > 5 else "above left", isSubplot=isSubplot)
			add_arrow_annotation(ax, annValues[1], annValues[2], annValues[3], annValues[4], annValues[5], annValues[6] if len(annValues) > 5 else "above left", isSubplot=isSubplot)
			#["range"[0], 0.751230[1], 1.031664[2], "[o]"[3], -70[4], "blue"[5], "blue"[6], False[7]]
			#["arrow"[0], (0.697614, -0.0252)[1], 0.30[2], "pinch"[3], "above right", False]

	#####################
	### Save and show figure/plot (if not subplot to larger figure)
	#####################
	if not isSubplot:
		#####################
		### Save plot to an image
		#####################
		# You can set the format by changing the extension
			# (e.g. .pdf, .svg, .eps)
		'''filename_RGB = global_path_helper.get_filename_only(wav_file_path) + '_waveform'
		filename_CMKY = filename_RGB + '_CMKY'
		
		filename_RGB, filename_CMKY = image_file_helper.fix_RGB_and_CMYK_filenames(filename_RGB, filename_CMKY)

		plt.savefig(global_values.python_images_dir + filename_RGB,
						format=global_values.image_format,
						bbox_inches='tight',
						dpi=global_values.image_DPI,
						frameon=False,
						aspect='normal',
						pad_inches=0.15,
						transparent=global_values.image_transparency)'''
		filename = global_path_helper.get_filename_only(wav_file_path) + '_waveform'
		filename = image_file_helper.fix_filename_conflicts(filename)
		
		# The frameon kwarg to savefig and the rcParams["savefig.frameon"] rcParam.
		# To emulate frameon = False, set facecolor to fully transparent ("none", or (0, 0, 0, 0)).
		
		fig.patch.set_alpha(0.0)
		ax.patch.set_alpha(0.0)
		plt.savefig(global_values.python_images_dir + '{0:0>2}'.format(global_values.plot_counter) + filename,
						format=global_values.image_format,
						bbox_inches='tight',
						dpi=global_values.image_DPI,
						#frameon=False,
						aspect='normal',
						pad_inches=0.15,
						facecolor=fig.get_facecolor(),
						edgecolor='none',
						transparent=global_values.image_transparency)
		
		### Display plot in GUI window, if desired
		#display_plot(fig, plt)
		
		# Clear axis (if not subplot)
		plt.cla()
		# Clear figure (if not subplot)
		plt.clf()
		# Close figure window (if not subplot)
		plt.close()

		#####################
		### Print plot image to LaTeX
		#####################
		### Convert RGB version of the image to CMYK
		### and delete unneeded RGB image
		'''image_file_helper.convert_RGB_to_CMYK(filename_RGB=filename_RGB, filename_CMKY=filename_CMKY)
		### Output \includegraphic command for Tex
		image_file_helper.create_TeX_include_CMYK_command(filename_CMKY)'''
		if global_values.image_format == 'svg' or global_values.image_format == 'svgz':
			### Output \includegraphic command for Tex
			#image_file_helper.normalize_SVGz_width(filename)
			### Output \includegraphic command for Tex
			image_file_helper.create_TeX_include_SVG_command(filename)

######################################################################
######################################################################
### Create a spectrogram image/plot from an audio .wav file
###
###	
######################################################################
######################################################################
def create_spectrogram_from_wav_file(wav_file_path,
										startTime=0.0,
										endTime=-1,
										maxFrequency=5500.0,
										dynamicRange=None,
										dynamicRangeMin=None,
										xaxisLabel="Time (s)",
										yaxisLabel="Frequency (Hz)",
										showXaxisLabel=True,
										showYaxisLabel=True,
										colorbarLabel="Level (dB)",
										showColorbar=True,
										showColorbarLabel=True,
										showPitch=False,
										showIntensity=False,
										showFormants=False,
										maxFormantFrequency=None,
										showTextgridFormants=False,
										isSubplot=False,
										ax=None):
	#%##################################################################################
	### Make the figure (if not a subplot)
	#%##################################################################################
	if not isSubplot:
		# Close other existing plots to avoid issues
		plt.close("all")
		# Tweak the figsize (width, height) in inches
		plt.figure(figsize=(global_values.figure_width, global_values.figure_height), dpi=global_values.image_DPI)
		ax=plt.gca()

	fig=plt.gcf()

	#%##################################################################################
	### Load the data and calculate the time of each sample
	#%##################################################################################
	samplerate, bitdepth, data, peakamplitude = audio_file_helper.get_samplerate_bitdepth_data_peakamplitude(wav_file_path, startTime, endTime)
	
	times = numpy.arange(len(data)) / float(samplerate)
	times += startTime

	#%##################################################################################
	### Set up values and parameters for calling spectrogram
	#%##################################################################################
	# (Nyquist frequency) - For cutoff frequency of 5000Hz (Sampling Rate)
	Fs = maxFrequency*2.#10000.

	NFFT = int(float(samplerate) * 0.01066666666666666666666666666667)
	# Number of overlaps (I really don't understand why, but /2 is good)
	noverlap = int(NFFT / 1.03)#
	# Gives more detail, the higher the multiplier
	pad_to = NFFT * 8#16#64#32#16
	
	# Use 'inferno' colormap
		# including '_r' after the cmap name will INVERT/REVERSE the colors
	cmap = matplotlib.cm.get_cmap('inferno')
	
	##----------------------------------------------------------------------##
	### From the spectra, find the minimum and maximum
	##### and convert each into decibels (dB)
	##----------------------------------------------------------------------##
	if dynamicRange == None and dynamicRangeMin == None:
		# Minimum amplitude (luminosity) should be 4.5 standard deviations lower than the mean
		vmin = peakamplitude * -0.25#-0.275 GOOD
		# Maximum amplitude (luminosity) should be the actual maximum in dB
		vmax = peakamplitude
	elif dynamicRangeMin == None:
		# Minimum amplitude (luminosity) should be 4.5 standard deviations lower than the mean
		vmin = dynamicRange * -0.25#-0.275 GOOD
		# Maximum amplitude (luminosity) should be the actual maximum in dB
		vmax = dynamicRange
	elif dynamicRange == None:
		# Minimum amplitude (luminosity) should be 4.5 standard deviations lower than the mean
		vmin = dynamicRangeMin
		# Maximum amplitude (luminosity) should be the actual maximum in dB
		vmax = peakamplitude
	else:
		# Minimum amplitude (luminosity) should be 4.5 standard deviations lower than the mean
		vmin = dynamicRangeMin
		# Maximum amplitude (luminosity) should be the actual maximum in dB
		vmax = dynamicRange
		

	#%##################################################################################
	### Plot the times (x-axis) versus audio data (y-axis)
	##### Also set up plot
	#%##################################################################################
	#spectra / Pxx: 2-D array - columns are the periodograms of successive segments
	#freqs: 1-D array - The frequencies corresponding to the rows in spectrum
	#t / spectimes: 1-D array - The times corresponding to midpoints of segments (i.e the columns in spectrum)
	#im /  cax: instance of class AxesImage - The image created by imshow containing the spectrogram
	Pxx, freqs, spectimes, cax = ax.specgram(data,
												NFFT=NFFT,
												Fs=samplerate,
												noverlap=noverlap,
												mode='magnitude',
												scale='dB',
												pad_to=pad_to,
												cmap=cmap,
												vmin=vmin,
												vmax=vmax,
												xextent=(times[0], times[-1]),
												zorder=0)
	
	bitdepth, data, peakamplitude = None, None, None
	Pxx, freqs, spectimes = None, None, None
	
	##-----------------------------------##
	### Show pitch (plot)
	##-----------------------------------##
	if showPitch:
		praatPitch.plotSpectrogramPitch(wav_file_path,
										startTime=startTime,
										endTime=endTime,
										minViewFrequency=0.0,
										maxViewFrequency=maxFrequency,
										#timeStep = 0.0005,
										#minPitchHz=75.0,#Praat default is 75
										#maxPitchHz=600.0,#Praat default is 600
										veryAccurate = False,#Praat default is False
										silenceThreshold = 0.075,#Praat default is 0.03
										voicingThreshold = 0.3,#Praat default is 0.45
										octaveCost = 0.05,#Praat default is 0.01
										octaveJumpCost = 0.15,#Praat default is 0.35
										voicedUnvoicedCost = 0.2,#Praat default is 0.14
										normalizePitch = True,#Need to normalize pitch for spectrograms (but not pitch plots)
										ax=ax)
	
	##-----------------------------------##
	### Show intensity (plot)
	##-----------------------------------##
	if showIntensity:
		praatIntensity.plotIntensity(wav_file_path,
										startTime=startTime,
										endTime=endTime,
										maxFrequency=maxFrequency,
										sampleRate=samplerate,
										minFrequency=100,
										limitToTextgrid=False,
										ax=ax)
										
	samplerate = None

	##-----------------------------------##
	### Show formants (scatterplot)
	##-----------------------------------##
	if showFormants:
		praatFormants.scatterPlotFormants(wav_file_path,
											maxFormantFrequency=maxFormantFrequency,
											showTextgridFormants=showTextgridFormants,
											ax=ax)

	##-----------------------------------##
	### General axes setup
	##-----------------------------------##
	customaxis(ax) #default: no right and top axis

	##-----------------------------------##
	### Set up the x-axis
	##-----------------------------------##
	if showXaxisLabel:
		set_audio_xaxis_start_end_times(times,
											ax,
											axisLabel=xaxisLabel,
											startTime=startTime,
											endTime=endTime)

	##-----------------------------------##
	### Set up the y-axis
	##-----------------------------------##
	ax.set_ylim([0, maxFrequency])
	ax.get_yaxis().set_tick_params(which='both', direction='out')

	# Set y-axis label, if it is set to be shown/visible
	if showYaxisLabel:
		ax.set_ylabel(yaxisLabel,
						labelpad=14,
						fontproperties=global_values.axis_label_fontproperties,
						fontsize=global_values.axis_label_font_size)
	else:
		ax.set_ylabel("")

	if not isSubplot:
		#####################
		### Create and add colorbar to spectrogram
		#####################
		if showColorbar:
			if not showColorbarLabel:
				colorbarLabel = ""
			cbar = create_spectrogram_colorbar(colorbarLabel, cax, theFigure=fig, theParentAxis=ax)

		#####################
		### Save and show figure/plot (if not subplot to larger figure)
		#####################
		# You can set the format by changing the extension
			# (e.g. .pdf, .svg, .eps)
		'''filename_RGB = global_path_helper.get_filename_only(wav_file_path) + '_waveform'
		filename_CMKY = filename_RGB + '_CMKY'
		
		filename_RGB, filename_CMKY = image_file_helper.fix_RGB_and_CMYK_filenames(filename_RGB, filename_CMKY)

		plt.savefig(global_values.python_images_dir + filename_RGB,
						format=global_values.image_format,
						bbox_inches='tight',
						dpi=global_values.image_DPI,
						frameon=False,
						aspect='normal',
						pad_inches=0.15,
						transparent=global_values.image_transparency)'''
		filename = global_path_helper.get_filename_only(wav_file_path) + '_spectrogram'
		filename = image_file_helper.fix_filename_conflicts(filename)
		
		# The frameon kwarg to savefig and the rcParams["savefig.frameon"] rcParam.
		# To emulate frameon = False, set facecolor to fully transparent ("none", or (0, 0, 0, 0)).
		
		fig.patch.set_alpha(0.0)
		ax.patch.set_alpha(0.0)
		plt.savefig(global_values.python_images_dir + '{0:0>2}'.format(global_values.plot_counter) + filename,
						format=global_values.image_format,
						bbox_inches='tight',
						dpi=global_values.image_DPI,
						#frameon=False,
						aspect='normal',
						pad_inches=0.15,
						facecolor=fig.get_facecolor(),
						edgecolor='none',
						transparent=global_values.image_transparency)
		
		### Display plot in GUI window, if desired
		#display_plot(fig, plt)

		# Clear axis (if not subplot)
		plt.cla()
		# Clear figure (if not subplot)
		plt.clf()
		# Close a figure window (if not subplot)
		plt.close()

		#####################
		### Print plot image to LaTeX
		#####################
		### Convert RGB version of the image to CMYK
		### and delete unneeded RGB image
		'''image_file_helper.convert_RGB_to_CMYK(filename_RGB=filename_RGB, filename_CMKY=filename_CMKY)
		### Output \includegraphic command for Tex
		image_file_helper.create_TeX_include_CMYK_command(filename_CMKY)'''
		if global_values.image_format == 'svg' or global_values.image_format == 'svgz':
			### Output \includegraphic command for Tex
			#image_file_helper.normalize_SVGz_width(filename)
			### Output \includegraphic command for Tex
			image_file_helper.create_TeX_include_SVG_command(filename)

	return cax

######################################################################
######################################################################
### Create a colorbar for a spectrogram based on spectrogram image axes
###
###	(separated from spectrogram function so it can be used with multiple subplots)
######################################################################
######################################################################
def create_spectrogram_colorbar(theLabel, theAxesImage, theFigure=plt.figure(), theColorbarAxis=None, theParentAxis=None):
	# Create colorbar using axis image/data (theAxisImage)
		# using its own axis (theColorbarAxis)
		# and stealing from the spectrogram parent axis (theParentAxis)
	cbar = theFigure.colorbar(theAxesImage, cax=theColorbarAxis, ax=theParentAxis)

	# Set tick labels to be right-aligned horizontally
	ticklabs = cbar.ax.get_yticklabels()
	cbar.ax.set_yticklabels(ticklabs, ha='right', fontproperties=global_values.axis_tick_fontproperties)
	# Show NO ticks in x-axis and y-axis of colorbar
	cbar.ax.yaxis.set_tick_params(pad=3, left=False, right=False, labelleft=True, labelright=False)
	cbar.ax.xaxis.set_ticks_position('none')
	cbar.ax.yaxis.set_ticks_position('none')

	# Create colorbar label, set to right side of colorbar
	cbar.set_label(theLabel,
					fontproperties=global_values.axis_label_fontproperties,
					fontsize=global_values.axis_label_font_size, 
					labelpad=15+(global_values.axis_label_font_size/3), 
					rotation=270)
	cbar.ax.yaxis.set_label_position('right')

	return cbar

######################################################################
######################################################################
### Customize the axes for a particular plot
###
###	default: turn off top and right axes
######################################################################
######################################################################
def customaxis(ax, c_left='k', c_bottom='k', c_right='none', c_top='none', direction='out', linelength=5, linewidth=1.25, size=12, pad=8):

	for c_spine, spine in zip([c_left, c_bottom, c_right, c_top], ['left', 'bottom', 'right', 'top']):
		if c_spine != 'none':
			ax.spines[spine].set_color(c_spine)
			ax.spines[spine].set_linewidth(linewidth)
		else:
			ax.spines[spine].set_color('none')

	# no bottom and no top
	if (c_bottom == 'none') & (c_top == 'none'): 
		ax.xaxis.set_ticks_position('none')
	# bottom and top
	elif (c_bottom != 'none') & (c_top != 'none'): 
		ax.tick_params(axis='x', direction='out', width=linewidth, length=linelength, color=c_bottom, labelsize=size, pad=pad)
	# bottom but not top
	elif (c_bottom != 'none') & (c_top == 'none'):
		ax.xaxis.set_ticks_position('bottom')
		ax.tick_params(axis='x', direction='out', width=linewidth, length=linelength, color=c_bottom, labelsize=size, pad=pad)
	# no bottom but top
	elif (c_bottom == 'none') & (c_top != 'none'):
		ax.xaxis.set_ticks_position('top')
		ax.tick_params(axis='x', direction='out', width=linewidth, length=linelength, color=c_top, labelsize=size, pad=pad)

	# no left and no right
	if (c_left == 'none') & (c_right == 'none'):
		ax.yaxis.set_ticks_position('none')
	# left and right
	elif (c_left != 'none') & (c_right != 'none'):
		ax.tick_params(axis='y', direction=direction, width=linewidth, length=linelength, color=c_left, labelsize=size, pad=pad)
	# left but not right
	elif (c_left != 'none') & (c_right == 'none'):
		ax.yaxis.set_ticks_position('left')
		ax.tick_params(axis='y', direction=direction, width=linewidth, length=linelength, color=c_left, labelsize=size, pad=pad)
	# no left but right
	elif (c_left == 'none') & (c_right != 'none'):
		ax.yaxis.set_ticks_position('right')
		ax.tick_params(axis='y', direction=direction, width=linewidth, length=linelength, color=c_right, labelsize=size, pad=pad)

######################################################################
######################################################################
### Set the (time) x-axis based on time data from a .wav file
###
###	(for logistical reasons, the times must be calculated prior to this function call)
###    (audioDataTime = numpy.arange(len(AUDIO_DATA)) / float(AUDIO_SAMPLE_RATE))
######################################################################
######################################################################
def set_audio_xaxis_start_end_times(audioDataTimes, theAxis, axisLabel="Time (s)", startTime=0, endTime=-1):
	# Create x-axis label in bold and padded a bit below tick labels
	theAxis.set_xlabel(axisLabel,
						fontproperties=global_values.axis_label_fontproperties,
						fontsize=global_values.axis_label_font_size,
						labelpad=6+(global_values.axis_label_font_size/3))

	# If endTime is undefined, then set endTime to final x-axis data point
	if endTime < 0:
		endTime = audioDataTimes[-1]

	# Set x-axis beginning and end times
	#theAxis.set_xlim([startTime, endTime])
	# Set minimum and maximum x-axis values
	theAxis.set_xlim([float("{:.3f}".format(startTime)), float("{:.3f}".format(endTime))])
	# Calculate range of x-axis times
	timeRange = abs(float("{:.3f}".format(endTime - startTime)))
	# Define the desired number of ticks for x-axis
	numTicks = 10
	# Apply a fix to forceably show the right-most (last) tick on x-axis
	fixToShowFinalTick = timeRange / numTicks / 100
	# Save the ticks to the x-axis
	theAxis.set_xticks(numpy.arange(startTime, endTime + fixToShowFinalTick, timeRange / numTicks))
	# Set the ticks to be outwards from axis, not inwards (which is default)
	theAxis.get_xaxis().set_tick_params(which='both', direction='out')

	return theAxis.get_xaxis()

######################################################################
######################################################################
### Emulate a grid of points on the plot's axis
###
###	
######################################################################
######################################################################
def set_grid(ax,
				numIntermediateTicks=0,
				numIntermediateXticks=0,
				numIntermediateYticks=0,
				dotSize=0.5,
				gridColor='#888888',
				alongAxes=False,
				in_back=True):
	# Use the ticks set for the x and y axes
	xticks = ax.get_xticks()
	yticks = ax.get_yticks()

	# Calculate distance between ticks
	xPointsAtEvery = abs(xticks[1] - xticks[0])
	yPointsAtEvery = abs(yticks[1] - yticks[0])

	# Distance between xticks and yticks is the same, unless explicitly set differently
	if numIntermediateXticks < numIntermediateTicks:
		numIntermediateXticks = numIntermediateTicks
	if numIntermediateYticks < numIntermediateTicks:
		numIntermediateYticks = numIntermediateTicks

	# Calculate intermediate xtick and ytick interval
	if numIntermediateTicks > 0:
		xPointsAtEvery = abs((max(xticks) - min(xticks)) / (len(xticks) - 1)) / (numIntermediateXticks + 1)
	if numIntermediateYticks > 0:
		yPointsAtEvery = abs((max(yticks) - min(yticks)) / (len(yticks) - 1)) / (numIntermediateYticks + 1)

	# Calculate dot locations for x-axis and y-axis
	xDots = numpy.arange(xticks[0], xticks[-1] + xPointsAtEvery, xPointsAtEvery)
	yDots = numpy.arange(yticks[0], yticks[-1] + yPointsAtEvery, yPointsAtEvery)

	# Create new grid
	dotGrid = []

	# Calculate all dots rising up from x-axis
	for xIndex, xTick in enumerate(xticks[0:] if alongAxes else xticks[1:-1]):
		for yIndex, yValue in enumerate(yDots):
			dotGrid.append([xTick, yValue])
	# Calculate all dots stretching right from y-axis
	for yIndex, yTick in enumerate(yticks[0:] if alongAxes else yticks[1:-1]):
		for xIndex, xValue in enumerate(xDots):
			dotGrid.append([xValue, yTick])

	# If behind plot, set z-order to 0 (i.e. lower than the data that is plotted)
	kywds = dict()
	if in_back:
		kywds['zorder'] = 0

	# Plot the grid of dots
	ax.scatter(*zip(*dotGrid), s=dotSize, color=gridColor, **kywds)

######################################################################
######################################################################
### Create range annotation (e.g. showing length of frication, VOT, etc.)
###
###	Adds horizontal arrow annotation with text in the middle
###	
###	Parameters
###	----------
###	ax : matplotlib.Axes
###	    The axes to draw to
###	
###	start : float
###	    start of line
###	
###	end : float
###	    end of line
###	
###	txt_str : string
###	    The text to add
###	
###	y_height : float
###	    The height of the line
###	
###	isSubplot : boolean
###	    whether part of a subplot or not
###	
###	txt_kwargs : dict or None
###	    Extra kwargs to pass to the text
###	
###	arrow_kwargs : dict or None
###	    Extra kwargs to pass to the annotate
###	
###	Returns
###	-------
###	tuple
###	    (annotation, text)
######################################################################
######################################################################    
def add_range_annotation(ax,
							start,
							end,
							txt_str,
							y_height=.5,
							txt_color="black",
							line_color="blue",
							txt_below=False,
							isSubplot=False,
							txt_kwargs=None,
							arrow_kwargs=None):

	# Calculate the DPI multiplier, because without it, changing DPI breaks things
	#image_DPImultiplier = global_values.image_DPI / 50
	image_DPImultiplier = 2

	# Calculate duration/width of x-axis
	axisDuration = max(ax.get_xticks()) - min(ax.get_xticks())
	# Calculate duration/width of annotation
	duration = end - start
	# Calculate percentage of annotation to x-axis
	durationPercent = duration / axisDuration

	# Calculate amplitude/height of y-axis
	axisAmplitudeRange = abs(max(ax.get_yticks()) - min(ax.get_yticks()))
	# Calculate curly brace/bracket height (2.0% of the y-axis height) plus tweak for dpi
	curlyBraceYaxisPercentage = 0.02 *  math.pow(image_DPImultiplier, 1/3)
	curlyBraceHeight = axisAmplitudeRange * curlyBraceYaxisPercentage

	# If annotation is used for a subplot, then increase curly brace/bracket height a bit
	if isSubplot:
		curlyBraceHeight = axisAmplitudeRange * curlyBraceYaxisPercentage * 3

	# Set arm lengths of curly brace/bracket (the small curved parts at the ends and middle)
	armDataLen = str(4.0 * math.pow(image_DPImultiplier, 1.25))
	armTextLen = str(3.0 * math.pow(image_DPImultiplier, 1.25))

	# Set radians for curly brace/bracket arm angles to 3 (for 50 dpi) or 3 * the DPI multiplier (if higher dpi)
	rad = str(3.0 * image_DPImultiplier)

	# Configure the left and right curly braces/brackets (lengths and curves of ends and middle)
	if arrow_kwargs is None:
		# default to your arrowprops
		arrow_kwargs = {'arrowprops':dict(arrowstyle="-",
											connectionstyle="arc, angleA=270, armA="+armDataLen+", angleB=90, armB="+armTextLen+", rad="+rad if txt_below else "arc, angleA=90, armA="+armDataLen+", angleB=270, armB="+armTextLen+", rad="+rad,
											linewidth=1,
											color=line_color,)}

	# Calculate the y-axis location of the pointy end (that points to text) of curly brace/bracket
	textArrowLocAbove = y_height + curlyBraceHeight
	textArrowLocBelow = y_height - curlyBraceHeight

	# Calculate the y-axis location of the annotation text
	if isSubplot:
		textHeight = axisAmplitudeRange * 2.5 / (1.75 * global_values.annotation_font_size)
	else:
		textHeight = axisAmplitudeRange / (1.75 * global_values.annotation_font_size)
	textYLocationAbove = textArrowLocAbove + (textHeight*2.575)
	textYLocationBelow = textArrowLocBelow - (textHeight*2.575)

	# Create left curly bar
	leftCurlyBar = ax.annotate('',
								xy=((start + end) / 2, textArrowLocBelow if txt_below else textArrowLocAbove),
								xytext=(start, y_height),
								annotation_clip=False,
								zorder=100,
								**arrow_kwargs)
	# Create left curly bar
	rightCurlyBar = ax.annotate('', 
								xy=((start + end) / 2, textArrowLocBelow if txt_below else textArrowLocAbove),
								xytext=(end, y_height),
								annotation_clip=False,
								zorder=100,
								**arrow_kwargs)

	# Create a black outline for the curly bars
	if line_color is not None:
		leftCurlyBar.arrow_patch.set_path_effects([matplotlib.patheffects.Stroke(linewidth=2, foreground="black"), matplotlib.patheffects.Normal()])
		rightCurlyBar.arrow_patch.set_path_effects([matplotlib.patheffects.Stroke(linewidth=2, foreground="black"), matplotlib.patheffects.Normal()])

	if txt_kwargs is None:
		txt_kwargs = {}
	
	if txt_color is None:
		txt_color = 'black'
	
	# Create annotation text
	txt = ax.text((start + end) / 2,
					textYLocationBelow if txt_below else textYLocationAbove,
					txt_str,
					fontproperties=global_values.annotation_fontproperties,
					size=global_values.annotation_font_size,
					color=txt_color,
					ha="center",
					va="bottom" if txt_below else "top",
					zorder=100,
					**txt_kwargs)

######################################################################
######################################################################
### Create arrow annotation (e.g. showing a particular thing at a specific point (e.g.) in time)
###
###	Adds horizontal arrow annotation with text in the middle
###	
###	Parameters
###	----------
###	ax : matplotlib.Axes
###	    The axes to draw to
###	
###	arrowLoc : tuple (i.e. writing coordinates such as (0, 1) )
###	    where the annotation arrow points
###	
###	textDist : float (a percentage)
###	    distance from arrow to put text
###	
###	txt_str : string
###	    The text to add
###	
###	textLoc : string
###	    relative position of text around the arrow
###	    ("above left", "above", "above right", "left", "right", "below left", "below", "below right")
###	
###	isSubplot : boolean
###	    whether part of a subplot or not
###	
###	txt_kwargs : dict or None
###	    Extra kwargs to pass to the text
###	
###	arrow_kwargs : dict or None
###	    Extra kwargs to pass to the annotate
###	
###	Returns
###	-------
###	tuple
###	    (annotation, text)
######################################################################
######################################################################    
def add_arrow_annotation(ax,
							arrowLoc,
							textDist,
							txt_str,
							txt_color="black",
							line_color="blue",
							textLoc="above left",
							isSubplot=False,
							txt_kwargs=None,
							arrow_kwargs=None):

	# Calculate duration/width of y-axis
	axisWidth = max(ax.get_xticks()) - min(ax.get_xticks())
	# Calculate duration/width of x-axis
	axisHeight = max(ax.get_yticks()) - min(ax.get_yticks())

	# Calculate the diagonal distance from arrow to text
	diagonalPercent = math.pow(2 * math.pow((textDist / 2), 2), 1 / 2)
	horizontalDist = axisWidth * (textDist * 0.75) if textLoc == "left" or textLoc == "right" else axisWidth * diagonalPercent
	verticalDist = axisHeight * (textDist * 1.25) if textLoc == "above" or textLoc == "below" else axisHeight * diagonalPercent

	# Default rad = 0, no bending of the line
	rad = 0

	if textLoc == "above":
		textCoord = (arrowLoc[0], arrowLoc[1] + verticalDist)
	elif textLoc == "above right":
		textCoord = (arrowLoc[0] + horizontalDist, arrowLoc[1] + verticalDist)
		rad = 0.3
	elif textLoc == "right":
		textCoord = (arrowLoc[0] + horizontalDist, arrowLoc[1])
	elif textLoc == "below right":
		textCoord = (arrowLoc[0] + horizontalDist, arrowLoc[1] - verticalDist)
		rad = -0.3
	elif textLoc == "below":
		textCoord = (arrowLoc[0], arrowLoc[1] - verticalDist)
	elif textLoc == "below left":
		textCoord = (arrowLoc[0] - horizontalDist, arrowLoc[1] - verticalDist)
		rad = 0.3
	elif textLoc == "left":
		textCoord = (arrowLoc[0] - horizontalDist, arrowLoc[1])
	else:#"above left"
		textCoord = (arrowLoc[0] - horizontalDist, arrowLoc[1] + verticalDist)
		rad = -0.3
	
	if txt_color is None:
		txt_color = 'black'
	
	# Create annotation text (plus arrow)
	txt = ax.annotate(txt_str,
					xy=arrowLoc,
					xycoords='data',
					xytext=textCoord,
					textcoords='data',
					fontproperties=global_values.annotation_fontproperties,
					size=global_values.annotation_font_size,
					va='center',
					ha='center',
					color=txt_color,
					annotation_clip=False,
					zorder=100,
					arrowprops=dict(arrowstyle='fancy',
									connectionstyle='arc3,rad='+str(rad),
									fc='0.75',
									ec=line_color,
									shrinkB=5,),)

######################################################################
######################################################################
### Create a waveform subplot above a spectrogram subplot (plus colorbar) from an audio .wav file
###
###	
######################################################################
######################################################################
def create_waveform_and_spectrogram_from_wav_file(wavFilename,
													startTime=0,
													endTime=-1,
													maxFrequency=5500.,
													onlySpectrogramColorbar=True,
													showPitch=False,
													showIntensity=False,
													showFormants=False,
													maxFormantFrequency=None,
													dynamicRange=None,
													dynamicRangeMin=None,
													showTextgridFormants=False,
													wavFormAnnotations=None,
													output_runtime=True):
	global_values.plot_counter += 1
	start_time = time.perf_counter()
	####################################################################################
	### Check and fix arguments for problems OR to set default values (if necessary)
	####################################################################################
	##----------------------------------------------------------------------##
	### No audio file specified... can't do anything
	##----------------------------------------------------------------------##
	if wavFilename is None or wavFilename == '':
		raise Exception("praatFormants.py->scatterPlotFormants: No audio filename provided")

	wav_file_path = audio_file_helper.get_full_wav_file_path(wavFilename)
	
	##----------------------------------------------------------------------##
	### Check that the specified file actually exists
	##----------------------------------------------------------------------##
	global_path_helper.verify_file_exists(wav_file_path)
	
	if wavFormAnnotations is None:
		wavFormAnnotations=[]
	
	# Close other existing plots to avoid issues
	plt.close("all")

	# Create subplots for waveform, spectrogram, and colorbar
		# get the associated figure and axes
	fig, axs = matplotlib.pyplot.subplots(ncols=1,
											nrows=2,
											figsize=(global_values.figure_width, global_values.figure_height),
											dpi=global_values.image_DPI)
	fig.subplots_adjust(right=0.95)  # making some room for cbar

	##-----------------------------------##
	### Plot waveform
	##-----------------------------------##
	waveform_start_time = time.perf_counter()
	create_waveform_from_wav_file(wav_file_path,
									startTime=startTime,
									endTime=endTime,
									isSubplot=True,
									ax=axs[0],
									annotations=wavFormAnnotations)
	waveform_runtime = time.perf_counter() - waveform_start_time

	##-----------------------------------##
	### Plot spectrogram
	##-----------------------------------##
	spectrogram_start_time = time.perf_counter()
	colorImageMap = create_spectrogram_from_wav_file(wav_file_path,
														startTime=startTime,
														endTime=endTime,
														maxFrequency=maxFrequency,
														showPitch=showPitch,
														showIntensity=showIntensity,
														showFormants=showFormants,
														maxFormantFrequency=maxFormantFrequency,
														dynamicRange=dynamicRange,
														dynamicRangeMin=dynamicRangeMin,
														showTextgridFormants=showTextgridFormants,
														isSubplot=True,
														ax=axs[1])
	spectrogram_runtime = time.perf_counter() - spectrogram_start_time

	##-----------------------------------##
	### Create/plot colorbar (for spectrogram)
	##-----------------------------------##
	# getting the lower left (x0,y0) and upper right (x1,y1) corners:
	[[x00,y00],[x01,y01]] = axs[0].get_position().get_points()
	[[x10,y10],[x11,y11]] = axs[1].get_position().get_points()
	# Set width of colorbar
	colorbarPadding = 0.045
	# Set padding between subplots and colorbar
	colorbarWidth = 0.0125
	# If colorbar should only be height of spectrogram
		# otherwise, set colorbar height to be complete figure
	if onlySpectrogramColorbar:
		cbarAxis = fig.add_axes([x11+colorbarPadding, y10, colorbarWidth, y11-y10])
	else:
		cbarAxis = fig.add_axes([x11+colorbarPadding, y10, colorbarWidth, y01-y10])
	# Create colorbar using color image map from spectrogram and colorbar axis dimensions
	cbar = create_spectrogram_colorbar("Level (dB)",
										colorImageMap,
										theFigure=fig,
										theColorbarAxis=cbarAxis,
										theParentAxis=axs[1])

	#####################
	### Put waveform axis on top so that annotations/text will be
	### visible if there is any overlapping
	#####################
	axs[0].set_zorder(50)
	axs[1].set_zorder(1)

	#####################
	### Save plot to an image
	#####################
	# You can set the format by changing the extension
	# (e.g. .pdf, .svg, .eps)
	filename = global_path_helper.get_filename_only(wav_file_path) + '_waveform'
	filename = image_file_helper.fix_filename_conflicts(filename)
	
	# The frameon kwarg to savefig and the rcParams["savefig.frameon"] rcParam.
	# To emulate frameon = False, set facecolor to fully transparent ("none", or (0, 0, 0, 0)).
	
	fig.patch.set_alpha(0.0)
	axs[0].patch.set_alpha(0.0)
	axs[1].patch.set_alpha(0.0)
	plt.savefig(global_values.python_images_dir + '{0:0>2}'.format(global_values.plot_counter) + filename,
					format=global_values.image_format,
					bbox_inches='tight',
					dpi=global_values.image_DPI,
					#frameon=False,
					aspect='normal',
					pad_inches=0.15,
					facecolor=fig.get_facecolor(),
					edgecolor='none',
					transparent=global_values.image_transparency)
	
	### Optimize the SVG file
	image_file_helper.optimize_SVG(global_values.cli_python_images_dir + '{0:0>2}'.format(global_values.plot_counter) + filename)
	
	### Display plot in GUI window, if desired
	#display_plot(fig, plt)

	# Clear axis
	plt.cla()
	# Clear figure
	plt.clf()
	# Close a figure window
	plt.close()

	#####################
	### Print plot image to LaTeX
	#####################
	if global_values.image_format == 'svg' or global_values.image_format == 'svgz':
		### Normalize SVGz to a standarized width (defined by global_values.normalized_SVGz_width)
		#image_file_helper.normalize_SVGz_width(filename)
		### Output \includegraphic command for Tex
		image_file_helper.create_TeX_include_SVG_command(filename)
	
	if output_runtime:
		runtimes_output = '------------------------------------\n'
		runtimes_output += 'Runtimes for ' + wav_file_path + '\n'
		runtimes_output += 'waveform plot time: {:.7f}\n'.format(waveform_runtime)
		runtimes_output += 'spectrogram  plot time: {:.7f}\n'.format(spectrogram_runtime)
		runtimes_output += 'waveform+spectrogram plot time: {:.7f}\n'.format(time.perf_counter() - start_time)
		runtimes_output += '\n'
		global_path_helper.append_to_file(global_values.python_runtimes_dir + 'create_waveform_and_spectrogram_from_wav_file.log', runtimes_output)

def display_plot(figure, plot):
	# Fix/tighten the margins around figure plot
		# (this should be called after all axes have been added)
	figure.subplots_adjust(left = 0.085)#small fix needed before plt.show()
	figure.subplots_adjust(right = 0.9725)#small fix needed before plt.show()
	figure.subplots_adjust(bottom = 0.120)#small fix needed before plt.show()
	figure.subplots_adjust(top = 0.9725)#small fix needed before plt.show()
	plot.subplots_adjust(wspace=0, hspace=0.075)#small fix needed before plt.show()
	plot.show()
	###Waveform:
	#Remove/tighten the margins around figure plot
		#(this should be called after all axes have been added)
	#pad - padding between the figure edge and the edges of subplots, as a fraction of the font-size.
	#h_pad - height padding between edges of adjacent subplots
	#w_pad - width padding between edges of adjacent subplots
	#plt.tight_layout(pad=2.15)#, h_pad=0., w_pad=0.)
	#plt.show()
	###Spectrogram:
	#Remove/tighten the margins around figure plot
		#(this should be called after all axes have been added)
	#pad - padding between the figure edge and the edges of subplots, as a fraction of the font-size.
	#h_pad - height padding between edges of adjacent subplots
	#w_pad - width padding between edges of adjacent subplots
	#plt.tight_layout(pad=2.15)#plt.tight_layout()#pad=1.5, h_pad=0., w_pad=0.)
	#fig.subplots_adjust(right = 1.1)#small fix needed for plt.show() when specgram+colorbar on same pyplot
	#plt.show()
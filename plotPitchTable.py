# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#%############################################################
#%Regular package imports here
#%############################################################
import matplotlib.image
import matplotlib.pyplot as plt
import numpy
import re
import time
#%############################################################
#% Local file imports here
#%############################################################
import global_values
import global_path_helper
import audio_file_helper
import image_file_helper
import praatPitch

######################################################################
######################################################################
###Create a waveform subplot above a spectrogram subplot (plus colorbar) from an audio .wav file
###
###	
######################################################################
######################################################################
def create_pitch_and_table_from_wav_file(wavFilename,
											xaxisLabel="Time (s)",
											yaxisLabel="Frequency (Hz)",
											startTime=0.0,
											endTime=-1,
											timeStep = 0.0,#Praat default is 0.0 (calculated)
											minPitch=75.0,
											maxPitch=600.0,
											silenceThreshold=0.03,#Praat default is 0.03
											voicingThreshold=0.45,#Praat default is 0.45
											octaveCost=0.01,#Praat default is 0.01
											octaveJumpCost=0.35,#Praat default is 0.35
											voicedUnvoicedCost=0.14,#Praat default is 0.14
											showIntensity=False,
											languageBreaks=[],
											language=[],
											glossBreaks=[],
											glosses=[],
											removeMaximums=[],
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
		raise Exception("plotPitchTable.py->create_pitch_and_table_from_wav_file: No audio filename provided")

	wav_file_path = audio_file_helper.get_full_wav_file_path(wavFilename)
	
	##----------------------------------------------------------------------##
	### Check that the specified file actually exists
	##----------------------------------------------------------------------##
	global_path_helper.verify_file_exists(wav_file_path)
	
	if languageBreaks is None:
		languageBreaks=[]
	if language is None:
		language=[]
	if glossBreaks is None:
		glossBreaks=[]
	if glosses is None:
		glosses=[]
	if removeMaximums is None:
		removeMaximums=[]
	
	### Close other existing plots to avoid issues
	plt.close("all")

	### Create subplots for waveform, spectrogram, and colorbar
	##### get the associated figure and axes
	fig, axs = matplotlib.pyplot.subplots(ncols=1,
											nrows=1,
											figsize=(global_values.figure_width, global_values.figure_height),
											dpi=global_values.image_DPI)
	
	pitch_start_time = time.perf_counter()
	praatPitch.plotPurePitch(wav_file_path,
								startTime=startTime,
								endTime=endTime,
								timeStep = timeStep,#Praat default is 0.0 (calculated)
								minPitchHz=minPitch,#Praat default is 75
								maxPitchHz=maxPitch,#Praat default is 500
								silenceThreshold = silenceThreshold,#Praat default is 0.03
								voicingThreshold = voicingThreshold,#Praat default is 0.45
								octaveCost = octaveCost,#Praat default is 0.01
								octaveJumpCost = octaveJumpCost,#Praat default is 0.35
								voicedUnvoicedCost = voicedUnvoicedCost,#Praat default is 0.14
								#silenceThreshold = 0.03,#Praat default is 0.03
								#voicingThreshold = 0.45,#Praat default is 0.45
								#octaveCost = 0.01,#Praat default is 0.01
								#octaveJumpCost = 0.35,#Praat default is 0.35
								#voicedUnvoicedCost = 0.14,#Praat default is 0.14
								removeMaximums = removeMaximums,
								ax=axs)
	pitch_runtime = time.perf_counter() - pitch_start_time
	
	##-----------------------------------##
	###Show intensity (plot)
	##-----------------------------------##
	'''if showIntensity:
		praatIntensity.plotIntensity(wav_file_path,
										startTime=startTime,
										endTime=endTime,
										maxFrequency=maxFrequency,
										sampleRate=samplerate,
										minFrequency=100,
										limitToTextgrid=False,
										ax=ax)'''
	
	#-----------------------------------##
	###Create and show language/gloss table
	##-----------------------------------##
	
	table_start_time = time.perf_counter()
	line_times = sorted(numpy.unique(languageBreaks + glossBreaks))
	
	for line_time in line_times:
		plt.plot(numpy.array([line_time, line_time]),
					numpy.array([plt.ylim()[0], plt.ylim()[1]]),
					c='k',
					linewidth=0.25,
					zorder=0)
	
	glosses_column_widths = []
	for index, break_point in enumerate(glossBreaks):
		if index == 0:
			glosses_column_widths.append((break_point - startTime) / (endTime - startTime))
		else:
			glosses_column_widths.append((break_point - glossBreaks[index-1]) / (endTime - startTime))
	glosses_column_widths.append((endTime - glossBreaks[-1]) / (endTime - startTime))
	
	language_column_widths = []
	for index, break_point in enumerate(languageBreaks):
		if index == 0:
			language_column_widths.append((break_point - startTime) / (endTime - startTime))
		else:
			language_column_widths.append((break_point - languageBreaks[index-1]) / (endTime - startTime))
	language_column_widths.append((endTime - languageBreaks[-1]) / (endTime - startTime))
	
	gloss_table = axs.table(cellText=[glosses, glosses], colWidths=glosses_column_widths, cellLoc='center', loc='bottom')
	language_table = axs.table(cellText=[language], colWidths=language_column_widths, cellLoc='center', loc='bottom')
	
	for key, cell in gloss_table.get_celld().items():
		cell.set_text_props(fontproperties=global_values.gloss_fontproperties)
	
	for key, cell in language_table.get_celld().items():
		cell.set_text_props(fontproperties=global_values.language_fontproperties)
	
	for cell in gloss_table._cells:
		if gloss_table._cells[cell]._text.get_text() == '':
			gloss_table._cells[cell].set_color('lightgrey')
			gloss_table._cells[cell].set_edgecolor('black')
		else:
			if '{sc}' in gloss_table._cells[cell]._text.get_text():
				gloss_table._cells[cell].set_text_props(fontproperties=global_values.gloss_small_caps_fontproperties)
				gloss_table._cells[cell]._text.set_text(gloss_table._cells[cell]._text.get_text().replace('{sc}', '{}'))
			if '{}' in gloss_table._cells[cell]._text.get_text():
				if gloss_table._cells[cell]._text.get_text().startswith('{}'):
					gloss_table._cells[cell]._loc = 'left'
					gloss_table._cells[cell].PAD = 0.04
					gloss_table._cells[cell]._text.set_horizontalalignment('left')
				elif gloss_table._cells[cell]._text.get_text().endswith('{}'):
					gloss_table._cells[cell]._loc = 'right'
					gloss_table._cells[cell]._text.set_horizontalalignment('right')
					gloss_table._cells[cell].PAD = 0.03
				gloss_table._cells[cell]._text.set_text(gloss_table._cells[cell]._text.get_text().replace('{}', ''))
	
	for cell in language_table._cells:
		if language_table._cells[cell]._text.get_text() == '':
			language_table._cells[cell].set_color('lightgrey')
			language_table._cells[cell].set_edgecolor('black')
		else:
			if '{}' in language_table._cells[cell]._text.get_text():
				if language_table._cells[cell]._text.get_text().startswith('{}'):
					language_table._cells[cell]._loc = 'left'
					language_table._cells[cell].PAD = 0.04
					language_table._cells[cell]._text.set_horizontalalignment('left')
				elif language_table._cells[cell]._text.get_text().endswith('{}'):
					language_table._cells[cell]._loc = 'right'
					language_table._cells[cell]._text.set_horizontalalignment('right')
					language_table._cells[cell].PAD = 0.03
				language_table._cells[cell].set_text_props(fontproperties=global_values.language_fontproperties)
				language_table._cells[cell]._text.set_text(language_table._cells[cell]._text.get_text().replace('{}', ''))
	
	#gloss_table.set_fontsize(18)
	#language_table.set_fontsize(18)
	gloss_table.set_fontsize(24)
	language_table.set_fontsize(24)
	gloss_table.scale(1, 3)
	language_table.scale(1, 3)
	
	table_runtime = time.perf_counter() - table_start_time
	
	##-----------------------------------##
	###Format x-axis and y-axis 
	##-----------------------------------##
	plt.tick_params(axis='both', which='major', labelsize=global_values.axis_tick_font_size)
	for label in axs.get_xticklabels() :
		label.set_fontproperties(global_values.axis_tick_fontproperties)
	plt.ylabel(yaxisLabel,
				fontproperties=global_values.axis_label_fontproperties,
				fontsize=global_values.axis_label_font_size)
	plt.xlabel(xaxisLabel,
				fontproperties=global_values.axis_label_fontproperties,
				fontsize=global_values.axis_label_font_size,
				labelpad=-1*int(global_values.axis_label_font_size/3))
	
	axs.spines['bottom'].set_position(('data', plt.ylim()[0] - ((plt.ylim()[1] - plt.ylim()[0]) * (gloss_table.properties()['child_artists'][0].get_height() * 2))))
	
	#####################
	###Save plot to an image
	#####################
	#You can set the format by changing the extension
	#(e.g. .pdf, .svg, .eps)
	'''filename = global_path_helper.get_filename_only(wav_file_path) + '_pitch_plot'
	#filename_CMKY = filename_RGB + '_CMKY'
	
	#filename_RGB, filename_CMKY = image_file_helper.fix_RGB_and_CMYK_filenames(filename_RGB, filename_CMKY)
	filename = image_file_helper.fix_filename_conflicts(filename)
	
	#if global_values.image_format == 'svg' or global_values.image_format == 'svgz':
	#filename_CMKY = filename_RGB
	
	plt.savefig(global_values.python_images_dir + '{0:0>2}'.format(global_values.plot_counter) + filename,
					fontproperties=global_values.generic_fontproperties,
					format=global_values.image_format,
					bbox_inches='tight',
					dpi=global_values.image_DPI,
					#dpi=600,#global_values.image_DPI*2,
					frameon='false',
					aspect='normal',
					pad_inches=0.15,
					transparent=global_values.image_transparency)'''
	filename = global_path_helper.get_filename_only(wav_file_path) + '_pitch_plot'
	filename = image_file_helper.fix_filename_conflicts(filename)
	
	fig.patch.set_alpha(0.0)
	#axs[0].patch.set_alpha(0.0)
	#axs[1].patch.set_alpha(0.0)
	axs.patch.set_alpha(0.0)
	plt.savefig(global_values.python_images_dir + '{0:0>2}'.format(global_values.plot_counter) + filename,
					format=global_values.image_format,
					bbox_inches='tight',
					dpi=global_values.image_DPI,
					frameon=False,
					aspect='normal',
					pad_inches=0.15,
					facecolor=fig.get_facecolor(),
					edgecolor='none',
					transparent=global_values.image_transparency)
	
	### Optimize the SVG file
	image_file_helper.optimize_SVG(global_values.cli_python_images_dir + '{0:0>2}'.format(global_values.plot_counter) + filename)
	
	#Clear axis
	plt.cla()
	#Clear figure
	plt.clf()
	#Close a figure window
	plt.close()

	#####################
	###Print plot image to LaTeX
	#####################
	if global_values.image_format == 'svg' or global_values.image_format == 'svgz':
		### Normalize SVGz to a standarized width (defined by global_values.normalized_SVGz_width)
		#image_file_helper.normalize_SVGz_width(filename)
		### Output \includegraphic command for Tex
		image_file_helper.create_TeX_include_SVG_command(filename)
	
	if output_runtime:
		runtimes_output = '------------------------------------\n'
		runtimes_output += 'Runtimes for ' + wav_file_path + '\n'
		runtimes_output += 'pitch plot time: {:.7f}\n'.format(pitch_runtime)
		runtimes_output += 'table  plot time: {:.7f}\n'.format(table_runtime)
		runtimes_output += 'pitch+table plot time: {:.7f}\n'.format(time.perf_counter() - start_time)
		runtimes_output += '\n'
		global_path_helper.append_to_file(global_values.python_runtimes_dir + 'create_pitch_and_table_from_wav_file.log', runtimes_output)
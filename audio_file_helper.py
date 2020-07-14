# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#%############################################################
#%Regular package imports here
#%############################################################
#import inspect
import numpy
import os
import pydub
#%############################################################
#% Local file imports here
#%############################################################
import global_values

######################################################################
######################################################################
### Get the sample rate, bit depth (e.g. 16-bit), (raw) data, and peak amplitude (in dB)
#####
#####
### Arguments:
##### wavFilename		- the name of the .wav file
#####
### Returns:
##### sample_rate		- the sample rate of the .wav file (e.g. 192 kHz, etc.)
##### bit_depth			- the bit rate of the .wav file (e.g. 16-bit, etc.)
##### data				- the data chunks of the .wav file
##### peak_amplitude	- the peak amplitude/intensity of the .wav file (e.g. 62 dB, etc.)
######################################################################
######################################################################
def get_samplerate_bitdepth_data_peakamplitude(wav_file_path, startTime=0, endTime=-1):
	wav_data = pydub.AudioSegment.from_file(wav_file_path, format='wav')
	
	wav_data = wav_data[(startTime*1000):(endTime*1000 if endTime >= 0 else -1)]

	sample_rate = wav_data.frame_rate
	bit_depth = wav_data.sample_width * 8
	
	### Normalize the data down to 16-bit range (if .wav file is 24-bits or 32-bits)
	if bit_depth > 16:
		data = numpy.divide(wav_data.get_array_of_samples(), 2**16)
	else:
		data = wav_data.get_array_of_samples()

	peak_amplitude = 20 * numpy.log10(wav_data.max) / (wav_data.sample_width-1)
	
	wav_data = None
	
	return sample_rate, bit_depth, data, peak_amplitude

######################################################################
######################################################################
### Get the audio data, converted to decibels (dB)
#####
#####
### Arguments:
##### data				- the (audio) data of the .wav file
#####
### Returns:
##### array				- data array containing dB values (instead of raw data)
######################################################################
######################################################################
def get_data_dB(data=[]):
	numpy.seterr(divide='ignore')
	data_dB = numpy.log10(numpy.absolute(data))
	numpy.seterr(divide='warn')
	data_dB[numpy.isneginf(data_dB)]=0
	return data_dB

######################################################################
######################################################################
### Get number of channels of an audio file within the current Tex project
#####
#####
### Arguments:
##### wavFilename		- the name of the .wav file
#####
### Returns:
##### int				- number of channels (e.g. mono-1, stereo-2) of .wav file
#####						(within the Tex audio subdirectory)
######################################################################
######################################################################
def get_wav_file_channels(wavFilename=''):
	return pydub.AudioSegment.from_file(global_values.audio_dir + wavFilename, format='wav').channels

######################################################################
######################################################################
### Convert an audio file (within the current Tex project) to mono
#####
#####
### Arguments:
##### wavFilename		- the name of the .wav file
#####
### Returns:
##### string			- name of the new mono (1 channel) .wav file
#####						(within the Tex audio subdirectory)
######################################################################
######################################################################
def convert_wav_file_to_mono(wavFilename=''):
	### Get the original .wav file as a pydub.AudioSegment
	sound = pydub.AudioSegment.from_file(global_values.audio_dir + wavFilename, format='wav')
	### Set the pydub.AudioSegment object down to mono (1 channel)
	sound = sound.set_channels(1)
	### Create a new filename with "_mono" in the name (so that we retain the original multi-channel .wav file
	new_mono_wav_filename = (global_values.audio_dir + wavFilename)[:-4]+'_mono.wav'
	### Write the new pydub.AudioSegment audio to a file
	sound.export(new_mono_wav_filename, format='wav')
	### Return the name of the new mono (1 channel) .wav file
	return new_mono_wav_filename

######################################################################
######################################################################
### Get the full path to an audio file within the current Tex project
#####
#####
### Arguments:
##### wavFilename		- the name of the .wav file
#####
### Returns:
##### string			- the full path to .wav file
#####						(within the Tex audio subdirectory)
######################################################################
######################################################################
def get_full_wav_file_path(wavFilename=''):
	### If .wav file has multiple channels (e.g. stereo),
	##### then convert the file, write a new mono file,
	##### and return the mono filename
	if get_wav_file_channels(wavFilename) > 1:
		return convert_wav_file_to_mono(wavFilename)
	### Otherwise, the file is already mono.
	##### Therefore, return the full path to the requested file.
	else:
		return global_values.audio_dir + wavFilename

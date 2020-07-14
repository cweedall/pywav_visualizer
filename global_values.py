# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#%##################################################################################
#%Regular Python package imports here
#%##################################################################################
import matplotlib.font_manager
import os

### Keep track of the current plot
### necessary for keeping track of which page to reference in the merged PDF
plot_counter = 0

#%##################################################################################
### Paths for directories and files
#%##################################################################################
##----------------------------------------------------------------------##
### Global OS directories and files
##----------------------------------------------------------------------##
### Windows directory
windows_dir = 'C:/Windows/'

### The directory where Windows fonts reside
font_dir = windows_dir + 'Fonts/'

### Windows System32 (32-bit) directory
windows_sys32_dir = windows_dir + 'System32/'

### Windows System (64-bit) directory
windows_sys64_dir = windows_dir + 'SysWOW64/'

### Windows Program Files directory (64-bit)
program_files_64bit_dir = 'C:/Program Files/'

### Windows Program Files directory (64-bit)
program_files_32bit_dir = 'C:/Program Files (x86)/'

### The directory OS, where color profiles are stored
color_profiles_dir = windows_sys32_dir + 'spool/drivers/color/'


##----------------------------------------------------------------------##
### Relative directories to the .tex file
##----------------------------------------------------------------------##
### Default directory where .tex file is
tex_dir = (os.getcwd() + '/').replace("\\", "/")

### Directory where TeX build files are ---> relative to the .tex file
tex_build_dir = tex_dir + '_build_files/'

### Directory where temporary Python build files go ---> relative to the .tex file
python_build_dir = tex_build_dir + 'python_Praat/'

### Directory where Python runtime files go ---> relative to the .tex file
python_runtimes_dir = tex_build_dir + 'python_runtimes/'

### Directory where audio files are ---> relative to the .tex file
audio_dir = tex_dir + 'audio/'

### Directory where images files are ---> relative to the .tex file
images_dir = tex_dir + 'images/'

### Directory where generated Python images files are stored ---> relative to the .tex file
python_images_dir = tex_dir + 'python_images/'

### Directory where PDFX-related files are stored ---> relative to the .tex file
pdfx_dir = tex_dir + '_pdfx/'
### PDFX definitions for profile and OutputIntents are - to make PDF 100% conform to PDFX standards
#pdfx_outputintents_profile = 'PDFX_def.ps'

### Directory where external utilities (executables) are ---> relative to the .tex file
external_utility_exe_dir = tex_dir + '_external_utility_exe/'


##----------------------------------------------------------------------##
### Color profiles
##----------------------------------------------------------------------##
#PSOuncoated_v3_FOGRA52.icc is a CMKY color profile for uncoated paper
#colorProfile = 'PSOuncoated_v3_FOGRA52.icc'
#USWebCoatedSWOP.icc is a CMKY color profile for uncoated paper
color_CMYK_print_profile = 'USWebCoatedSWOP.icc'
#sRGB Color Space Profile.icm is a RGB color profile for displays/monitors
color_RGB_display_profile = 'sRGB Color Space Profile.icm'

##----------------------------------------------------------------------##
### Executable files
##----------------------------------------------------------------------##
### Set the path and filename of convert.exe (from ImageMagick)
##### which converts RGB image to CMYK image
#ImageMagick_convert_CMD = program_files_64bit_dir + 'ImageMagick-7.0.5-Q16/convert.exe'
ImageMagick_convert_CMD = program_files_64bit_dir + 'ImageMagick-7.0.8-Q16/convert.exe'

### Set the path and filename of inkscape.exe (from Inkscape)
##### which converts SVG and SVGZ files to EPS, PS, PDF, PNG, etc.
#Inkscape_CMD = program_files_64bit_dir + 'Inkscape/inkscape.exe'

##ghostscript_CMD = program_files_64bit_dir + 'gs/gs9.22/bin/gswin64c.exe'
ghostscript_CMD = program_files_64bit_dir + 'gs/gs9.27/bin/gswin64c.exe'

pdftk_CMD = external_utility_exe_dir + 'pdftk/pdftk.exe'

rsvg_convert_CMD = external_utility_exe_dir + 'rsvg-convert/rsvg-convert.exe'

svgstopdf_CMD = external_utility_exe_dir + 'svgstopdf/svgstopdf.exe'

##----------------------------------------------------------------------##
###  Fix directory and file paths, if necessary for OS
##### Because of Windows using backslashes in file/directory paths
##### create a new path for use in the command line environment
##### Default python paths with forward slashes is the same as the 
##### regular paths in *nix OSes but replaces with (double) backslashes
##### for Windows so it can be used properly in Python strings
##----------------------------------------------------------------------##
if os.name == 'nt':
	cli_audio_dir = audio_dir.replace("/", "\\")
	cli_color_profiles_dir = color_profiles_dir.replace("/", "\\")
	cli_images_dir = images_dir.replace("/", "\\")
	cli_python_images_dir = python_images_dir.replace("/", "\\")
	cli_pdfx_dir = pdfx_dir.replace("/", "\\")
	#cli_ImageMagick_convert_CMD = ImageMagick_convert_CMD.replace("/", "\\")
	#cli_Inkscape_CMD = Inkscape_CMD.replace("/", "\\")
	cli_ghostscript_CMD = ghostscript_CMD.replace("/", "\\")
	cli_pdftk_CMD = pdftk_CMD.replace("/", "\\")
	cli_rsvg_convert_CMD = rsvg_convert_CMD.replace("/", "\\")
	cli_svgstopdf_CMD = svgstopdf_CMD.replace("/", "\\")
else:
	cli_audio_path = audio_dir
	cli_color_profiles_dir = color_profiles_dir
	cli_images_dir = images_dir
	cli_python_images_dir = python_images_dir
	cli_pdfx_dir = pdfx_dir
	#cli_ImageMagick_convert_CMD = ImageMagick_convert_CMD
	#cli_Inkscape_CMD = Inkscape_CMD
	cli_ghostscript_CMD = ghostscript_CMD
	cli_pdftk_CMD = pdftk_CMD
	cli_rsvg_convert_CMD = rsvg_convert_CMD
	cli_svgstopdf_CMD = svgstopdf_CMD

#%##################################################################################
### Global values
#%##################################################################################
##----------------------------------------------------------------------##
### Plot values
##----------------------------------------------------------------------##
#(6.8, 3.84) fourth size
#(9.06666666, 5.1) third size
#(13.6, 7.68) half size
#(27.2, 15.3) full size
figure_width = 13.6
figure_height = 7.68

##----------------------------------------------------------------------##
### Font values
##----------------------------------------------------------------------##
##--------------------------------------------------##
### Full path to TTF and OTF font files (for the OS)
##--------------------------------------------------##
### BentonSans Regular
font_bentonsans_file = font_dir + 'BentonSans-Regular.otf'
### BentonSans Medium (not bold...half-way there)
font_bentonsans_medium_file = font_dir + 'BentonSans-Medium.otf'
### BentonSans Regular SC (small caps)
font_bentonsans_regular_sc_file = font_dir + 'BentonSans-RegularSC.otf'
### BentonSans Medium SC (small caps) (not bold...half-way there)
font_bentonsans_medium_sc_file = font_dir + 'BentonSans-MediumSC.otf'
### Charis SIL
font_charissil_file = font_dir + 'CharisSIL-R_0.ttf'#charissil-r_0.ttf
### Charis SIL Bold
font_charissil_bold_file = font_dir + 'CharisSIL-B_0.ttf'


generic_fontproperties = matplotlib.font_manager.FontProperties(family='sans-serif',
																	variant='normal',
																	style='normal',
																	stretch='normal',
																	weight='normal',
																	fname=font_bentonsans_file)

### Axis label font family
axis_label_fontproperties = matplotlib.font_manager.FontProperties(family='sans-serif',
																	variant='normal',
																	style='normal',
																	stretch='normal',
																	weight='bold',
																	fname=font_bentonsans_medium_file)
### Axis tick label font family
axis_tick_fontproperties = matplotlib.font_manager.FontProperties(family='sans-serif',
																	variant='normal',
																	style='normal',
																	stretch='normal',
																	weight='normal',
																	fname=font_bentonsans_file)
### Annotation font family
annotation_fontproperties = matplotlib.font_manager.FontProperties(family='serif',
																	variant='normal',
																	style='normal',
																	stretch='normal',
																	weight='normal',
																	fname=font_charissil_bold_file)
### Text (annotation-like text) font family
text_fontproperties = matplotlib.font_manager.FontProperties(family='sans-serif',
																variant='normal',
																style='normal',
																stretch='ultra-expanded',
																weight='normal',
																fname=font_bentonsans_file)
### Gloss (in table) font family
gloss_fontproperties = matplotlib.font_manager.FontProperties(family='sans-serif',
																variant='normal',
																style='normal',
																stretch='normal',
																weight='normal',
																fname=font_bentonsans_file)
### Gloss (in table) small caps font family
gloss_small_caps_fontproperties = matplotlib.font_manager.FontProperties(family='sans-serif',
																			variant='normal',
																			style='normal',
																			stretch='normal',
																			weight='normal',
																			fname=font_bentonsans_regular_sc_file)
### Language (in table) font family
language_fontproperties = annotation_fontproperties


### Matplotlib Axis label font size
axis_label_font_size = 18
### Matplotlib Axis tick label font size
axis_tick_font_size = 14
### Matplotlib Annotation font size
annotation_font_size = 28#16
### Matplotlib Text font size
text_font_size = 18#16

##----------------------------------------------------------------------##
### Image-specific values
##----------------------------------------------------------------------##
#Quality of image dots per inch (dpi)
	#50 is the default for testing purposes
	#100 is good for drafts
	#300 or 600 is necessary for final version - which will be printed
image_DPI = 72
#image_DPI = 100

#Whether images should be saves with transparent background (True) or not (False)
image_transparency = True#False

#Default image extension
#(supported formats: eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff)
image_format = 'svg'
#image_format = 'svgz'
#image_format = 'eps'
#image_format = 'pdf'
#image_format = 'png'
#image_extension = '.'.join(image_format)
image_extension = '.' + image_format

### The width that all SVG and SVGZ files should have
normalized_SVGz_width = 1200



POWER_QUANTITY = 1 # energy, power
FIELD_QUANTITY = 2 # pressure
def rmsToDb(rmsValue, 
			valueType = FIELD_QUANTITY, 
			dbBase = 0, 
			rmsBase = 1.0):
	""" 
	performs a RMS to dB conversion
	@param rmsValue the input value
	@param valueType indicates whether the RMS value comes from a field
		quantity (FIELD_QUANTITY) such as sound pressure, or from a power 
		quantity (POWER_QUANTITY) such as energy or power. This will determine
		the multiplication factor (either 20 or 10, respectively). See 
		<a href="http://en.wikipedia.org/wiki/Decibel">
		power and field quantities</a> on Wikipedia for more info.
	@param dbBase base value that is added to the result (zero is default)
	@param rmsBase base value by which the rms value is divided before 
		conversion (one is default, i.e. no effect)
	@return [dB]
	"""
	if rmsValue <= 0:
		raise Exception("RMS value must not be zero or below")
	factor = None
	if valueType == FIELD_QUANTITY: factor = 20.0
	elif valueType == POWER_QUANTITY: factor = 10.0
	else:
		raise Exception("undefined value type (must be either FIELD_QUANTITY " \
			+ "or POWER_QUANTITY")
	return dbBase + (factor * math.log10(rmsValue / float(rmsBase)))
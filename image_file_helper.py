# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#%############################################################
#%Regular package imports here
#%############################################################
import os
import subprocess
import sys
#%############################################################
#% Local file imports here
#%############################################################
import global_values
import global_path_helper

######################################################################
######################################################################
### Delete previously generated Python files
#####
#####
### Arguments:
##### (nothing)
#####
### Returns:
##### (nothing)
######################################################################
######################################################################
def delete_previously_generated_python_files():
	### Delete previous images in Python images folder (we want to recreate them all)
	subprocess.run(['del', '/F', '/Q', global_values.cli_python_images_dir+'*'], shell=True)

######################################################################
######################################################################
### Merge all generated Python PDF files (based on SVGs)
#####
#####
### Arguments:
##### (nothing)
#####
### Returns:
##### (nothing)
######################################################################
######################################################################
def merge_all_generated_python_pdf_files():
	### Clips larger images on subsequent (i.e. not the first) PDF pages
	### Don't use anymore, because svgstopdf (with fc-cache and fc-list) works
	### perfectly - all pages of PDF are sized according to the original PDF size
	'''rsvg_convert_cmd = [global_values.cli_rsvg_convert_CMD,
						'--unlimited',
						'--keep-aspect-ratio',
						'--keep-image-data',
						'-f',
						'pdf',
						'-o',
						global_values.cli_python_images_dir+'merged_python_svgs_RGB.pdf',
						global_values.cli_python_images_dir+'*.svg']'''
	svgstopdf_cmd = [global_values.cli_svgstopdf_CMD,
						global_values.cli_python_images_dir+'*.svg',
						global_values.cli_python_images_dir+'merged_python_svgs_RGB.pdf']
	### 
	gs_cmd = [global_values.cli_ghostscript_CMD,
				'-dQUIET',
				'-dBATCH',
				'-dNOPAUSE',
				'-dNOSAFER',
				'-dPDFSETTINGS=/prepress',
				'-o',
				#global_values.cli_python_images_dir+'merged_python_svgs_CMYK.pdf',
				global_values.cli_python_images_dir+'merged_python_svgs.pdf',
				'-sDEVICE=pdfwrite',
				'-dOverrideICC=true',
				'-sICCProfilesDir='+global_values.cli_color_profiles_dir,
				'-sOutputICCProfile='+global_values.color_CMYK_print_profile,
				'-sDefaultRGBProfile='+global_values.color_RGB_display_profile,
				'-sDefaultCMYKProfile='+global_values.color_CMYK_print_profile,
				'-sGraphicICCProfile='+global_values.color_CMYK_print_profile,
				'-sImageICCProfile='+global_values.color_CMYK_print_profile,
				'-sTextICCProfile='+global_values.color_CMYK_print_profile,
				'-sProcessColorModel=DeviceCMYK',
				'-sColorConversionStrategy=CMYK',
				'-sColorConversionStrategyForImages=CMYK',
				'-dUNROLLFORMS',
				'-dCompatibilityLevel=1.7',
				'-dNOINTERPOLATE',
				'-dHaveTransparency=true',
				'-dRenderIntent=3',
				'-dGraphicIntent=3',
				'-dImageIntent=3',
				'-dTextIntent=3',
				'-dDeviceGrayToK=true',
				'-sColorConversionStrategyForImages=CMYK',
				'-sColorConversionStrategyForGraphics=CMYK',
				'-sColorConversionStrategyForText=CMYK',
				'-dDetectDuplicateImages',
				'-dDetectBlends=true',
				'-dConvertImagesToIndexed=true',
				'-dAntiAliaColorImages=true',
				'-dAntiAliasGrayImages=true',
				'-dAntiAliasMonoImages=true',
				'-dColorImageResolution=1000',
				#'-dUseCIEColor',
				#'-dNONATIVEFONTMAP',
				#'-dNOCCFONTS',
				'-dEmbedAllFonts=true',
				'-dSubsetFonts=false',
				'-sFONTPATH=C:/Windows/Fonts',
				#'-dCompressFonts=true',
				#'-dCompressStreams=true',
				#'-dCompressPages=true',
				'-dCompressFonts=false',
				'-dCompressStreams=false',
				'-dCompressPages=false',
				#'-dNoOutputFonts',
				'-c',
				'.setpdfwrite <</NeverEmbed [ ]>> setdistillerparams',
				'-f',
				global_values.cli_python_images_dir+'merged_python_svgs_RGB.pdf']
	### PDFTK is supposed to optimize the PDF
	### however, it seems to cause minor spacing variations in the images
	### therefore...not using it anymore
	'''pdftk_cmd = [global_values.cli_pdftk_CMD,
					global_values.cli_python_images_dir+'merged_python_svgs_CMYK.pdf',
					'output',
					global_values.cli_python_images_dir+'merged_python_svgs.pdf',
					'compress']'''
	### 
	#subprocess.run(rsvg_convert_cmd + ['&&'] + gs_cmd + ['&&'] + pdftk_cmd, env=dict(os.environ, PANGOCAIRO_BACKEND='fc'), shell=True)
	#subprocess.run(svgstopdf_cmd + ['&&'] + gs_cmd + ['&&'] + pdftk_cmd, env=dict(os.environ, PANGOCAIRO_BACKEND='fc'), shell=True)
	subprocess.run(svgstopdf_cmd + ['&&'] + gs_cmd, env=dict(os.environ, PANGOCAIRO_BACKEND='fc'), shell=True)

######################################################################
######################################################################
### Convert generated Python RGB image file to CMKY image file
##### also delete the old RGB image file
#####
### Arguments:
##### filename_RGB		- filename for the old RGB
##### filename_CMKY		- filename for the new CMKY
#####
### Returns:
##### (nothing)
######################################################################
######################################################################
'''def convert_RGB_to_CMYK(filename_RGB='', filename_CMKY=''):
	### Convert RGB version of the image to CMYK
	subprocess.run([global_values.cli_ImageMagick_convert_CMD,
						global_values.cli_python_images_dir+filename_RGB,
						'-colorspace', 'CMYK',
						'-profile',
						global_values.cli_color_profiles_dir+global_values.color_CMYK_print_profile,
						global_values.cli_python_images_dir+filename_CMKY], shell=True)
	### Delete unneeded RGB image
	subprocess.run(['del', global_values.cli_python_images_dir+filename_RGB], shell=True)'''

######################################################################
######################################################################
### Optimize SVG image, by stripping space and other minor tweaks
##### that reduce filesize.
#####
### Arguments:
##### filename			- filename for the original SVG
#####
### Returns:
##### (nothing)
######################################################################
######################################################################
def optimize_SVG(filename=''):
	if filename is not '':
		### Find the index of the '.svg' extension
		### and make a new filename with '_optimize' inserted before '.svg'
		idx = filename.index('.svg')
		filename_optimized = filename[:idx] + '_optimize' + filename[idx:]
		### Scour is a Python package which is available via the command line
		### which reduces unnecessary space/characters/text in an SVG file
		### A new optimized SVG file is created.
		scour_cmd = ['scour',
						'--quiet',
						'-i',
						filename,
						'-o',
						filename_optimized,
						'--strip-xml-space',
						'--no-line-breaks',
						'--enable-viewboxing',
						'--enable-id-stripping',
						'--enable-comment-stripping',
						'--shorten-ids',
						'--indent=none',
						'--create-groups']
		### Delete the original SVG file
		delete_old_svg_cmd = ['del',
								'/F',
								'/Q',
								filename]
		### 
		subprocess.run(scour_cmd + ['&&'] + delete_old_svg_cmd, shell=True)
######################################################################
######################################################################
### Convert generated Python RGB image file to CMKY image file
##### also delete the old RGB image file
#####
### Arguments:
##### filename_RGB		- filename for the old RGB
##### filename_CMKY		- filename for the new CMKY
#####
### Returns:
##### (nothing)
######################################################################
######################################################################
'''def normalize_SVGz_width(filename=''):
	### 
	rsvg_convert_cmd = [global_values.cli_rsvg_convert_CMD,
							'--unlimited',
							'--keep-aspect-ratio',
							'--keep-image-data',
							'-w',
							str(global_values.normalized_SVGz_width),
							'-f',
							'svg',
							'-o',
							global_values.cli_python_images_dir+'{0:0>2}new_'.format(global_values.plot_counter)+filename,
							global_values.cli_python_images_dir+'{0:0>2}'.format(global_values.plot_counter)+filename]
	### 
	delete_old_svg_cmd = ['del',
							'/F',
							'/Q',
							global_values.cli_python_images_dir+'{0:0>2}'.format(global_values.plot_counter)+filename]
	### 
	rename_new_svg_cmd = ['rename',
							global_values.cli_python_images_dir+'{0:0>2}new_'.format(global_values.plot_counter)+filename,
							'{0:0>2}'.format(global_values.plot_counter)+filename]
	### 
	subprocess.run(rsvg_convert_cmd + ['&&'] + delete_old_svg_cmd + ['&&'] + rename_new_svg_cmd, env=dict(os.environ, PANGOCAIRO_BACKEND='fc'), shell=True)
'''
######################################################################
######################################################################
### Create \includegraphics command for TeX, based on image filename
#####
### Arguments:
##### filename			- filename for image to include in TeX
#####
### Returns:
##### (nothing)
######################################################################
######################################################################
def create_TeX_include_SVG_command(filename=''):#def create_TeX_include_CMYK_command(filename=''):
	#print('\t\t\\includegraphics[width=0.9\\textwidth]{' + global_values.python_images_dir+filename + '}%',file=sys.stdout, flush=True)
	print('\t\t\\begingroup\\graphicspath{{'+global_values.python_images_dir+'}}\\includegraphics[interpolate=false,width=0.9\\textwidth,page='+str(global_values.plot_counter)+']{merged_python_svgs.pdf}\\endgroup%',file=sys.stdout, flush=True)

######################################################################
######################################################################
### Append a number to filename
##### if one (or more) files with the same name already exist(s)
#####
### Arguments:
##### filename			- filename for the intended image
#####
### Returns:
##### (nothing)
######################################################################
######################################################################
def fix_filename_conflicts(filename=''):
	fixed_filename = filename
	if os.path.isfile(global_values.python_images_dir + filename + global_values.image_extension):
		fileRenameCounter = 2
		while (os.path.isfile(global_values.python_images_dir + fixed_filename + '_(' + str(fileRenameCounter) + ')' + global_values.image_extension)):
			fileRenameCounter += 1
		fixed_filename = fixed_filename + '_(' + str(fileRenameCounter) + ')'
	return fixed_filename+global_values.image_extension

	
	
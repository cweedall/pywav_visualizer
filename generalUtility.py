# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""

@package generalUtility This module contains some general-purpose utility functions

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

@warning DISCLAIMER: this module (and the others in this library) was developed 
on a Mac, and was never really tested a Windows platform. There might be 
problems with the backslashes used in Windows path indicators.
"""

import subprocess

######################################################################

def makeSystemCall(args):
	""" 
	make a system call 
	@param args must be an array, the first entry being the called program 
	@return returns a tuple with communication from the called system process, 
		consisting of stdoutdata, stderrdata
	"""
	msg = subprocess.check_output(args, stdin=subprocess.PIPE, stderr=subprocess.PIPE).decode("utf-8")
	#msg = subprocess.check_output()["ntpq", "-p"]).decode("utf-8")
	#msg = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
	#msg = subprocess.call(args) #- recommended version; we don't use it, since we want to get back the system message
	return msg

##############################################################################

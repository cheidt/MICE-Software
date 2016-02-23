#!/usr/bin/env python

import os
from os import listdir

#geometry_dir = os.environ['MAUS_ROOT_DIR'] + "/files/geometry/download/gdml/"
geometry_dir = "/vols/fets2/heidt/maus/geometry/108/gdml/"
for input_file in listdir(geometry_dir):
  if "Doublet.gdml" in input_file:
    read_file    = geometry_dir + input_file
    write_file   = input_file
    doublet_file = open(read_file,'r')
    new_file     = open(write_file,'w')
    
    move_fibers = 1
    control_list = {"reverse_fibers": False, \
                    "place_fibers": False, \
                    "resize_fibers": False}
    
    if control_list["reverse_fibers"]:
      for line in doublet_file:
        if '<position name="fibrePos' in line:
          line_s = line.split('"')
          fiber_number = float((filter(str.isdigit, line_s[1])))
          for x_g in range(len(line_s)):
            if "x" in line_s[x_g]:
              x_pos = -1*float(line_s[x_g+1])
              line_s[x_g+1] = str(x_pos)
          con = '"'
          line = con.join(line_s)
          
        new_file.write(line)
    
    if control_list["place_fibers"]:    
      if "ViewV" in input_file or "ViewW" in input_file:
        central_fiber = 749.5
      elif "ViewU" in input_file and "Station5" in input_file and "Tracker1" in input_file:
        central_fiber = 753
      else:
        central_fiber = 742.5
      
      for line in doublet_file:
        if '<position name="fibrePos' in line:
          line_s = line.split('"')
          fiber_number = float((filter(str.isdigit, line_s[1])))
          for x_g in range(len(line_s)):
            if "x" in line_s[x_g]:
              x_pos = 0.2135 * (central_fiber - (fiber_number))
              line_s[x_g+1] = str(x_pos)
          con = '"'
          line = con.join(line_s)
        
        if 'hz=' in line:
          line_s = line.split('"')
          for hz_g in range(len(line_s)):
            if "hz" in line_s[hz_g]:
              print x_pos, "  ", input_file, "  fiber: ", fiber_number
              length = 2*pow(161**2 - x_pos**2,0.5)
              line_s[hz_g+1] = str(length)
          con = '"'
          line = con.join(line_s)
        
        new_file.write(line)
      
    if control_list["resize_fibers"]:
      if "ViewV" in input_file or "ViewW" in input_file:
        central_fiber = 749.5
      elif "ViewU" in input_file and "Station5" in input_file and "Tracker1" in input_file:
        central_fiber = 753
      else:
        central_fiber = 742.5
      
      for line in doublet_file:
        if '<position name="fibrePos' in line:
          line_s = line.split('"')
          fiber_number = float((filter(str.isdigit, line_s[1])))
          for x_g in range(len(line_s)):
            if "x" in line_s[x_g]:
              x_pos = 0.2135 * (central_fiber - (fiber_number))
              line_s[x_g+1] = str(x_pos)

        if 'hz=' in line:
          line_s = line.split('"')
          for hz_g in range(len(line_s)):
            if "hz" in line_s[hz_g]:
              length = 2*pow(161**2 - x_pos**2,0.5)
              line_s[hz_g+1] = str(length)
          con = '"'
          line = con.join(line_s)
        
        new_file.write(line)
      
      
    doublet_file.close()
    new_file.close()
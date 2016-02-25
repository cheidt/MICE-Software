#####################################################################
# Differs from Lab 7 mapping in that Station 1 bulkhead 5 and       #
#  Station 5 bulkhead 4, in the upstream tracker and Station 1      #
#  bulkhead 1 in the downstream tracker are not reversed.  Waiting  #
#  for confirmation that this is correct.                           #
# -Chris Heidt                                                      #
#####################################################################

#!/usr/bin/env python
from math import floor
import copy

class Tracker_Mapping:
  def __init__ (self):
    clean_log = open('mapping_log', 'w')
    clean_log.close()
    clean_map = open('map_file', 'w')
    clean_map.close()

    self.verbosity = 1
    self.wg_place = {}
    self.map = {}

#####################################################################
# chan_map maps the channel number inside the ADC electronics to    #
#   the fiber numbers in the tracker.  Tracker fibers are placed    #
#   sequencally in the connectors such that the first position      #
#   is the first fiber in a section of plane.                       #
#####################################################################  
    self.chan_map = [ 61,  60,  62,  63,  65,  64,  66,  67,  58,  59, \
                      57,  56,  72,  69,  68,  70,  53,  52,  54,  55, \
                      71,  74,  75,  73,  50,  51,  49,  48,  78,  79, \
                      77,  76,  45,  44,  46,  47,  81,  80,  82,  83, \
                      42,  43,  41,  40,  88,  85,  84,  86,  37,  36, \
                      38,  39,  87,  90,  91,  89,  34,  35,  33,  32, \
                      95,  94,  93,  92,  28,  29,  30,  31,  96,  97, \
                      99,  98,  25,  27,  26,  23, 103, 102, 100, 101, \
                      22,  20,  21,  24, 104, 105, 107, 106,  19,  18, \
                      16,  17, 111, 110, 108, 109,  12,  13,  15,  14, \
                     112, 113, 115, 114,   9,  11,  10,   7, 119, 118, \
                     116, 117,   6,   4,   5,   8, 120, 121, 123, 122, \
                       3,   2,   0,   1, 127, 126, 124, 125]

    self.Write_Log("Starting tracker mapping.")
    self.WG_Placement()
    self.Chan_Placement()

#####################################################################
# This function determines the physical location based upon         #
#   waveguide number (each tracker/station/plane combination is     #
#   unique).  Probably a prettier way to do this...                 #
#####################################################################
  def Chan_Placement(self):
    for key in self.wg_place:
      for x in range(len(self.wg_place[key])):
        WG = int(self.wg_place[key][x][0])
        mod = int(self.wg_place[key][x][1])
        if WG == 26:
            self.Map(1, 1, 1, key, mod, WG)
        elif WG == 31:
            self.Map(1, 2, 1, key, mod, WG)
        elif WG == 21:
            self.Map(1, 3, 1, key, mod, WG)
        elif WG == 16:
            self.Map(1, 4, 1, key, mod, WG)
        elif WG == 10:
            self.Map(1, 5, 1, key, mod, WG)
        elif WG == 56:
          self.Map(0, 1, 1, key, mod, WG)
        elif WG == 51:
          self.Map(0, 2, 1, key, mod, WG)
        elif WG == 46:
          self.Map(0, 3, 1, key, mod, WG)
        elif WG == 41:
          self.Map(0, 4, 1, key, mod, WG)
        elif WG == 36:
          self.Map(0, 5, 1, key, mod, WG)
        
        elif WG == 27:
          self.Map(1, 1, 2, key, mod, WG)
        elif WG == 32:
          self.Map(1, 2, 2, key, mod, WG)
        elif WG == 22:
          self.Map(1, 3, 2, key, mod, WG)
        elif WG == 17:
          self.Map(1, 4, 2, key, mod, WG)
        elif WG == 8:
          self.Map(1, 5, 2, key, mod, WG)
        elif WG == 57:
          self.Map(0, 1, 2, key, mod, WG)
        elif WG == 52:
          self.Map(0, 2, 2, key, mod, WG)
        elif WG == 47:
          self.Map(0, 3, 2, key, mod, WG)
        elif WG == 42:
          self.Map(0, 4, 2, key, mod, WG)
        elif WG == 37:   
          self.Map(0, 5, 2, key, mod, WG)

        elif WG == 28:
          self.Map(1, 1, 3, key, mod, WG)
        elif WG == 33:
          self.Map(1, 2, 3, key, mod, WG)
        elif WG == 23:
          self.Map(1, 3, 3, key, mod, WG)
        elif WG == 18:
          self.Map(1, 4, 3, key, mod, WG)
        elif WG == 6:
          self.Map(1, 5, 3, key, mod, WG)
        elif WG == 58:
          self.Map(0, 1, 3, key, mod, WG)
        elif WG == 53:
          self.Map(0, 2, 3, key, mod, WG)
        elif WG == 48:
          self.Map(0, 3, 3, key, mod, WG)
        elif WG == 43:
          self.Map(0, 4, 3, key, mod, WG)
        elif WG == 38:
          self.Map(0, 5, 3, key, mod, WG)

        elif WG == 29:
          self.Map(1, 1, 4, key, mod, WG)
        elif WG == 34:
          self.Map(1, 2, 4, key, mod, WG)
        elif WG == 24:
          self.Map(1, 3, 4, key, mod, WG)
        elif WG == 19:
          self.Map(1, 4, 4, key, mod, WG)
        elif WG == 7:
          self.Map(1, 5, 4, key, mod, WG)
        elif WG == 59:
          self.Map(0, 1, 4, key, mod, WG)
        elif WG == 54:
          self.Map(0, 2, 4, key, mod, WG)
        elif WG == 49:
          self.Map(0, 3, 4, key, mod, WG)
        elif WG == 44:
          self.Map(0, 4, 4, key, mod, WG)
        elif WG == 13:
          self.Map(0, 5, 4, key, mod, WG)

        elif WG == 30:
          self.Map(1, 1, 5, key, mod, WG)
        elif WG == 35:
          self.Map(1, 2, 5, key, mod, WG)
        elif WG == 25:
          self.Map(1, 3, 5, key, mod, WG)
        elif WG == 20:
          self.Map(1, 4, 5, key, mod, WG)
        elif WG == 9:
          self.Map(1, 5, 5, key, mod, WG)
        elif WG == 60:
          self.Map(0, 1, 5, key, mod, WG)
        elif WG == 55:
          self.Map(0, 2, 5, key, mod, WG)
        elif WG == 50:
          self.Map(0, 3, 5, key, mod, WG)
        elif WG == 45:
          self.Map(0, 4, 5, key, mod, WG)
        elif WG == 15:
          self.Map(0, 5, 5, key, mod, WG)
        else:
          self.Write_Log("There is no Light Guide "+str(WG))
    
  def Map(self, tracker, station, bulk, key, mod, WG):
    for x in range(128):
      if x%8 < 4:
        board = key
        bank  = int(floor((mod-1)/2))
      else:
        board = key + 1
        bank  = int(3 - floor((mod-1)/2))

      if bulk == 1:
        plane = 0
        in_chan = x
      elif bulk == 2:
        if x < 86:
          plane = 0
          in_chan = x + 128
        else:
          plane = 2
          in_chan = x - 86
      elif bulk == 3:
        plane = 2
        in_chan = x + 42
      elif bulk == 4:
        if x < 42:
          plane = 2
          in_chan = x + 170
        else:
          plane = 1
          in_chan = x - 42
      elif bulk == 5:
        plane = 1
        in_chan = x + 86
      else:
        Write_Log("Can not determine plane and channel")

      if (mod%2):
        chan_out = self.chan_map[x]
      else:
        chan_out = self.chan_map[127-x]

      write_map = open('map_file', 'a')
      if not WG == 56:
        write_map.write(str(board)+' '+str(bank)+' '+str(chan_out)+' '+\
                        str(tracker)+' '+str(station)+' '+str(plane)+' '+\
                        str(in_chan)+' '+str(WG)+' '+str(WG)+' '+\
                        str(x+1)+'\n')
      else:
        write_map.write(str(board)+' '+str(bank)+' '+str(chan_out)+' '+\
                        str(tracker)+' '+str(station)+' '+str(plane)+' '+\
                        str(127-in_chan)+' '+str(WG)+' '+str(WG)+' '+\
                        str(x+1)+'\n')
      write_map.close()

  def WG_Placement(self):
    read_WG = open('WG_placement', 'r')
    cryo = 0
    side = 0
    mod  = 0
    WG   = 0
    for line in read_WG:
      if '*' in line:
        continue
      elif 'Cryo' in line:
        temp = line.split(' ')
        cryo = int(temp[1])-1
      elif 'RHS' in line:
        side = 2
      elif 'LHS' in line:
        side = 0
      else:
        temp    = line.split('-')
        mod     = int(temp[0])
        temp[1] = temp[1].replace(' ','')
        temp[1] = temp[1].replace('\n','')
        if not temp[1]:
          WG = 0
        else:
          WG = temp[1]
        key = 4*cryo+side
        if key not in self.wg_place:
          self.wg_place[key] = [[WG,mod]]
        else:
          self.wg_place[4*cryo+side].append([WG,mod])
    read_WG.close()
    self.Write_Log(self.wg_place)
    self.Check_Data()
        
# Currently does not work, no idea why...       
  def Check_Data(self):
    for key in self.wg_place:
      for x in range(len(self.wg_place[key])):
        test_dict = copy.deepcopy(self.wg_place)
        WG = self.wg_place[key][x][0]
        test_dict[key].pop(x)
        for test_key in test_dict:
          for y in range(len(test_dict[test_key])):
            if test_dict[test_key][y] == WG:
              self.Write_Log("Light guide "+str(WG)+" enter twice")
    
  def Write_Log(self, message):
    log_out = open('mapping_log', 'a')
    log_out.write(str(message)+'\n')
    if self.verbosity == 1:
      print message
    log_out.close()

if __name__ == "__main__":
  Tracker_Mapping()

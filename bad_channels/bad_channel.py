#!/usr/bin/env python

import libMausCpp
import ROOT
from ROOT import gROOT
import os
from os import listdir
import numpy as np
from math import floor
import _ctypes

class Analysis:
  def __init__ (self):
  
  # defines where to cut on bad channel noise
    self.bc_noise_cut = 2.0 # twice the expected value 
    self.bc_quiet_cut = 0.5 # half the expected value
    self.event_cut = -1     # number of events to process, -1 for all events
    
  # Designed mostly for testing purposes, when turned on allows much quicker 
  # loading times on data that has already been analyized once.
    self.load_previous = False
    self.save_record = True
    self.previous_filename = "bc_history.root"

  # Maus data location
    self.run_number = "7417"
    self.data_directory = "/vols/fets2/heidt/offline/data/7417/"
    self.scifi_map_file = "scifi_mapping_2015-09-11.txt"
    self.scifi_map_directory = os.environ["MAUS_ROOT_DIR"]+"/files/cabling/"

  # Analysis
    self.process()
  # Output  
    self.Output()
    
##################################################################################################
  # Formats the data and calls Bad_Channels() which does the analysis
  def process(self):
    self.Load_mapp()

    self.unit_hist = ROOT.TH1D("unit","unit_hist_longr",212,0,212)
    for i in range(212):
      self.unit_hist.SetBinContent(i,1) 

    if self.load_previous == True:
      self.prev_file = ROOT.TFile(self.previous_filename, "READ")
      self.Recreate_ROOT()

    if self.load_previous == False:
  # Creates the container ROOT files and loads up the MAUS processed file.
      self.Make_ROOT()
      file_in = self.Load_file()
      print "Reading MAUS processed file: ",file_in
      root_file = ROOT.TFile(file_in, "READ") 
  # Checks spill/event is good data
      data = ROOT.MAUS.Data()
      tree = root_file.Get("Spill")
      if not tree:
        return
      tree.SetBranchAddress("data", data)
      print "Filling Histogram"
      peat_count = 0
      if self.event_cut > tree.GetEntries() or self.event_cut <= 0:
        self.event_cut = tree.GetEntries()
      for i in range(self.event_cut):
        peat_count += 1
        if (peat_count % 100 == 0):
          print "Filling event: ",peat_count, "/", self.event_cut
        tree.GetEntry(i)
        self.spill = data.GetSpill()
        if not self.spill.GetDaqEventType() == "physics_event":
          continue
        if self.spill.GetReconEvents().size() == 0:
          print "No Recon Events"
          continue

  # Fills the ROOT containers with data from the MAUS files
        self.Fill_Hists()
    
    check_out = open("check_out.txt", "w")
    for tra in range(0,2):
      for sta in range(1,6):
        for pla in range(0,3):
          for bin in range(len(self.dig_cont[tra][sta][pla])):
            check_out.write("Tracker: ")
            check_out.write(str(tra))
            check_out.write(" Station: ")
            check_out.write(str(sta))
            check_out.write(" Plane: ")
            check_out.write(str(pla))
            check_out.write(" Bin: ")
            check_out.write(str(bin))
            check_out.write(" = ")
            check_out.write(str(self.dig_cont[tra][sta][pla].GetBinContent(bin)))
            check_out.write("\n")
    check_out.close()
    
    print "Running bad channel analysis"
    self.Bad_Channels()
    
##################################################################################################
  # Pulls out tracker digits and sorts them into histos sorted by plane/station/tracker
  def Fill_Hists(self):
    for rc in range(self.spill.GetReconEvents().size()):
      digit = self.spill.GetReconEvents()[rc].GetSciFiEvent().digits()
      for di in range(len(digit)):
        trac = stat = chan = plan = nupe = -1
        trac = digit[di].get_tracker()
        stat = digit[di].get_station()
        chan = digit[di].get_channel()
        plan = digit[di].get_plane()
        nupe = digit[di].get_npe()
        cont = self.dig_cont[trac][stat][plan].GetBinContent(chan)
        self.dig_cont[trac][stat][plan].SetBinContent(chan, cont+1)
        self.Record[trac][stat][plan].SetBinContent(chan, cont+1)

##################################################################################################
  # loads tracker mapping, used to call back to bank/board for bad channel list
  # used by Map_to_VLSB()
  def Load_mapp(self):
    print "Loading Map"
    mapfi = open(self.scifi_map_directory + self.scifi_map_file,'r')
    self.map=[]
    for line in mapfi:
      line = line.strip('\n')
      self.map.append(line.split(" "))

##################################################################################################
  # Takes the zero channels from all previous functions and writes them out
  # to a bad channels list.
  def Dead_Channels(self):
    self.dig_emp_list = []
    for tra in range(0,2):
      for sta in range(1,6):
        for pla in range(0,3):
          for bin in range(len(self.dig_cont[tra][sta][pla])):
            if self.dig_cont[tra][sta][pla].GetBinContent(bin) == 0:
              BB = self.Map_to_VLSB(tra,sta,pla,bin)
              if BB != [-1,-1]:
                self.dig_emp_list.append(BB)

##################################################################################################
  # Uses map to determine board and bank info
  def Map_to_VLSB(self,tracker,station,plane,channel):
    board = channel_ro = -1
    for mp in range(len(self.map)):
      if int(self.map[mp][3])==tracker and int(self.map[mp][4])==station and \
         int(self.map[mp][5])==plane   and int(self.map[mp][6])==channel:
        board=int(self.map[mp][0])*4+int(self.map[mp][1])
        channel_ro=int(self.map[mp][2])
        continue
    if board == -1 or channel_ro == -1:
      print "NOT FOUND! ",tracker,"  ",station,"  ",plane,"  ",channel
    VLSB=[board,channel_ro]
    return VLSB
      
##################################################################################################
  # Calls the recursive functions Hot_Channels() and Shh_Channels() which look
  # for hot and quite channels respectively.
  def Bad_Channels(self):
    for tra in self.dig_cont:
      for sta in self.dig_cont[tra]:
        for pla in self.dig_cont[tra][sta]:
          # print "Bad channels analysis in: tracker ", tra," station ",sta," plane ",pla
          fit_hist = self.dig_cont[tra][sta][pla]
          self.Hot_Channels(fit_hist)
          self.Shh_Channels(fit_hist)
          self.dig_cont[tra][sta][pla] = fit_hist
    self.Dead_Channels()

###################################################################################################
  # Attempts to fit various functions to digit counts
  def Fit_Hist(self, fit_hist):
    status=fit_hist.Fit("gaus","SQ")
    fit = "gaus"
    if status.CovMatrixStatus() < 3:
      # print "Problem with fitting, attempting a linear fit"
      fit_hist.GetListOfFunctions().Clear()
      status = fit_hist.Fit("pol1","SQ")
      # fit_hist.Draw()
      # raw_input("Press Enter to Exit")
      fit = "pol1"
    return fit

##################################################################################################
  # Looks at channels/fit ratio and cuts above bc_noise_cut criteria then sets bin content
  # equal to zero.  Bad bins are read out in Dead_Channels()
  def Hot_Channels(self, fit_hist):
    fit = self.Fit_Hist(fit_hist)
    hdiff=fit_hist.Clone("hdiff")
    hdiff.Divide(hdiff.GetFunction(fit))
    hdiff.GetListOfFunctions().Clear()
    bin = hdiff.GetMaximumBin()
    max = hdiff.GetBinContent(int(bin))
    if (max > self.bc_noise_cut):
  # The lines below exists for testing purposes only.
  #    fit_hist.Draw()
  #    raw_input("Press Enter to Exit")
      fit_hist.SetBinContent(bin,0)
      self.Hot_Channels(fit_hist)

##################################################################################################
  # Looks at channel/fit ratio and cuts below bc_quite_cut criteria then sets bin content
  # equal to zero.  Bad bins are read out in Dead_Channels()
  def Shh_Channels(self, fit_hist):
    fit = self.Fit_Hist(fit_hist)
    hdiff=fit_hist.Clone("hdiff")
    hdiff.Divide(hdiff.GetFunction(fit))
    hdiff.GetListOfFunctions().Clear()
    hdiff.Divide(self.unit_hist,hdiff)
    bin = hdiff.GetMaximumBin()
    min = hdiff.GetBinContent(int(bin))
    if (min > 1.0/self.bc_quiet_cut):
  # The lines below exists for testing purposes only.
  #    fit_hist.Draw()
  #    raw_input("Press Enter to Exit")
      fit_hist.SetBinContent(bin,0)
      self.Shh_Channels(fit_hist)

##################################################################################################
  # Creates the container root file that will be passed around script.
  def Make_ROOT(self):
    print "Creating empty ROOT file"
    self.dig_cont={}
    self.Record={}
    for tra in range(0,2):
      self.dig_cont[tra]={}
      self.Record[tra]={}
      if tra == 0:
        trs = "U"
      else:
        trs = "D"
      for sta in range(1,6):
        self.dig_cont[tra][sta]={}
        self.Record[tra][sta]={}
        for pla in range(0,3):
          if pla == 0 or pla == 1 or pla == 2:
            dig_name="DC_Tk%s%d%d" %(trs,sta,pla)
            dig_titl="Digit Scan Tk%s S%d P%d" %(trs,sta,pla)
            self.dig_cont[tra][sta][pla]=ROOT.TH1D(dig_name,dig_titl,212,0,212)

            dig_name="Rec_Tk%s%d%d" %(trs,sta,pla)
            dig_titl="Digit Scan Tk%s S%d P%d" %(trs,sta,pla)
            self.Record[tra][sta][pla]=ROOT.TH1D(dig_name,dig_titl,212,0,212)

##################################################################################################
  # Loads a previously generated root file.
  def Recreate_ROOT(self):
    print "Loading previously used ROOT file"
    self.dig_cont={}
    for tra in range(0,2):
      self.dig_cont[tra]={}
      if tra == 0:
        trs = "U"
      else:
        trs = "D"
      for sta in range(1,6):
        self.dig_cont[tra][sta]={}
        for pla in range(0,3):
          dig_name="Rec_Tk%s%d%d" %(trs,sta,pla)
          self.dig_cont[tra][sta][pla]=self.prev_file.Get(dig_name)

##################################################################################################
  # Outputter
  def Output(self):
    out_root = ROOT.TFile("bc_out_test.root",'RECREATE')
    for tr in range(0,2):
      for st in range(1,6):
        for pl in range(0,3):
          self.dig_cont[tr][st][pl].Write()
    out_root.Close()

    if self.save_record == True:
      out_record = ROOT.TFile(self.previous_filename,'RECREATE')
      for tr in range(0,2):
        for st in range(1,6):
          for pl in range(0,3):
            self.Record[tr][st][pl].Write()
      out_record.Close()

    dead_list =  open("dead_channel_list.txt","w")
    for dl in range(len(self.dig_emp_list)):
      dead_list.write(str(self.dig_emp_list[dl][0]))
      dead_list.write("  ")
      dead_list.write(str(self.dig_emp_list[dl][1]))
      dead_list.write("\n")
    raw_input("Press Enter to Exit")

##################################################################################################
  # Searches set directory and finds a processed MAUS file.
  def Load_file(self):
    for input_file in listdir(self.data_directory):
      if self.run_number in input_file and ".root" in input_file:
        file_in = self.data_directory + input_file
    return file_in

##################################################################################################

if __name__ == "__main__":
  Analysis()


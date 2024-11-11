#!/usr/bin/env python

import math
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import numpy as np
from dataclasses import dataclass
from kiutils.board import Board

# load the PCB file
pcb = Board().from_file("./sao-petal.kicad_pcb")
#------------------
plot_scatter=False
plot_polar=False
plot_positions=False
#------------------
# plotting control
# select one of the following:
plot_scatter=True
#plot_polar=True
#plot_positions=True

#----------------------------------------
# Setup colors used by the plots
#----------------------------------------
had_yellow = '#f3bf10'
had_grey = '#1a1a1a'
# tableau colors
spiral_colors = [
  'tab:gray',
  'tab:brown',
  'tab:orange',
  'tab:olive',
  'tab:green',
  'tab:cyan',
  'tab:blue',
  'tab:purple',
  'tab:pink',
  'tab:red',
]

# Defines the arrangements of spirals and leds
NUM_SPIRALS = 8 # how many spirals
NUM_LAMPS = 7 # how many lamps per spiral

@dataclass
class Part:
  '''Holds desired part information.'''
  refdes: str
  posn: list[float]
  angle: float  # angle in degrees
  def __post_init__(self):
    self.pre = self.refdes.rstrip('0123456789')
    self.seq = int( self.refdes[len(self.pre):] )
    self.anorm_special()
    #self.anorm()
    self.theta = float(np.deg2rad(self.angle))
  def __repr__(self):
    return \
      f'{self.pre:s}.{self.seq:02d} ' \
      f'[ {self.posn[0]:8.3f}, {self.posn[1]:8.3f} ] ' \
      f'{self.angle:>8.1f}'
      # f'{self.refdes:<10s}'
  def __str__(self):
    return self.__repr__()
  def __lt__(a,b):
    return a.seq < b.seq
  def anorm_special(self):
    '''Normalize the part rotation angle based on actual LED data.'''
    if self.seq < 30: 
      if self.angle < -50.0: 
        self.angle += 360.0
    return self.angle
  def anorm(self):
    '''Normalize the part rotation angle on +/- 180 degs.'''
    if self.angle < -180.0: self.angle += 360.0
    if self.angle > +180.0: self.angle -= 360.0
    return self.angle

class Parts(list):
  '''List of parts, subclassed for printing purposes.'''
  def __str__(self):
    return '\n'.join(str(p) for p in self)
  def __repr__(self):
    return self.__str__()

def fetch_leds():
  '''Loads in LED parts from the PCB file.'''
  for i, f in enumerate(pcb.footprints):
    refdes = f.properties['Reference']
    if refdes.startswith("LED"):
      if refdes == 'LED57': continue
      x = f.position.X
      y = f.position.Y
      a = f.position.angle
      parts.append( Part( refdes, [x, y], a ) );
  parts.sort()

#************************************************************************
#***                 LET THE PLOTTING BEGIN
#************************************************************************

# fetch all LED parts from the PCB
parts = Parts()
fetch_leds()
print(parts)

#----------------------------------------
# radii constants for for polar plot
rmin = 300
rsep = 50
rmax = 600

#----------------------------------------
# lists of values extracted from the parts
# for convenient slicing and plotting
angles = [ p.angle for p in parts ]
thetas = [ p.theta for p in parts ]
seqs = [ p.seq for p in parts ]
radii=[]
xposns = [ p.posn[0] for p in parts ]
yposns = [ p.posn[1] for p in parts ]
# build list of radii values for polar plot,
# map each spiral to different radius bands
for isp in range(0,NUM_SPIRALS): # loop over the spirals
  for lamp in range(0,NUM_LAMPS):
    radii.append( rmax - rsep*isp - lamp )

#----------------------------------------
# function to slice long lists
# used to make each spiral sublist
from itertools import islice
def split_list(lst, step):
  sublists = []
  for i in range(0, len(lst), step):
    sublists.append(list(islice(lst, i, i+step)))
  return sublists
 
#----------------------------------------
@dataclass
class Spiral:
  '''Lists needed for plotting a single spiral.'''
  angles: list[float]
  thetas: list[float]
  seqs: list[int]
  radii: list[int]
  xposns: list[int]
  yposns: list[int]
  def __post_init__(self):
    pass

#----------------------------------------
# bust up the lists into segments, one per spiral
splits = [
  split_list( angles, NUM_LAMPS ),
  split_list( thetas, NUM_LAMPS ),
  split_list( seqs, NUM_LAMPS ),
  split_list( radii, NUM_LAMPS ),
  split_list( xposns, NUM_LAMPS ),
  split_list( yposns, NUM_LAMPS ),
]
spirals=[]
for isp in range(NUM_SPIRALS):
  spirals.append(Spiral( *list(zip(*splits))[isp] ))
#----------------------------------------
# now plotting data is in...
# * one big honking set of lists, 0...55
# * eight lists, one per spiral
#----------------------------------------


#************************************************************************
#***                 LET THE PLOTTING BEGIN
#************************************************************************

if plot_scatter:
  fig = plt.figure(figsize=(8, 5), dpi=200)
  ax = fig.add_subplot()
  # ----------------------------------------
  mkr = mpl.markers.MarkerStyle(marker="d")
  for isp, sp in enumerate(spirals):
    for i in range(NUM_LAMPS):
      mkr._transform = mkr.get_transform().rotate_deg(sp.angles[i])
      ax.scatter(sp.seqs[i], sp.angles[i], 
                 marker=mkr, s=50, color=spiral_colors[isp] )
    ax.plot(sp.seqs, sp.angles, '-', color=spiral_colors[isp], 
            linewidth=2, alpha = 0.35 )
  # ----------------------------------------
  # all this code just to set the grid, 
  # axis, ticks, and labels, and background
  # colors
  LW = 1.0
  AL = 0.35
  fig.set_facecolor(had_grey)
  ax.set_facecolor(had_grey)
  ax.xaxis.label.set_color(had_yellow)
  ax.yaxis.label.set_color(had_yellow)
  ax.tick_params(axis='x', colors=had_yellow)
  ax.tick_params(axis='y', colors=had_yellow)
  for x in [ 'bottom', 'top', 'right', 'left', ]:
    ax.spines[x].set_color(had_yellow)
    ax.spines[x].set_linewidth(LW)
    #ax.spines[x].set_alpha(AL)
  # ----------------------------------------
  # setup the axes / grids
  ax.grid(color=had_yellow, linewidth=LW, alpha=AL)
  ax.yaxis.grid( True,  which='major' )
  ax.xaxis.grid( True,  which='major' )
  ax.set_yticks([-90, 0, 90, 180, 270 ])
  ax.set_xticks([ x+1 for x in range(0,56,7)])
  lbl_xticks = [ f'#{i+1}' for i in range(NUM_SPIRALS) ]
  ax.set_xticklabels(lbl_xticks, rotation=0, #fontsize = 9, 
    style='italic', horizontalalignment='left')
  ax.set_xlabel('LED Spiral')
  ax.set_ylabel("LED Rotation Angle (degs)")


if plot_polar:
  fig = plt.figure(figsize=(5, 5), dpi=200)
  ax = fig.add_subplot(projection='polar')
  # ----------------------------------------
  # set colors and (lack of) axes
  fig.set_facecolor(had_grey)
  ax.grid(False)
  #ax.set_xticklabels([]) 
  ax.set_yticklabels([])
  ax.axis("off")
  # ----------------------------------------
  # draw four quadrant lines
  # where rotation angles would fall 
  # if they placed with "normal" angles
  for degree in [0, 90, 180, 270]:
    rad = np.deg2rad(degree)
    ax.plot([rad,rad], [rmax+rsep, rmax-8*rsep], color=had_yellow,
            linewidth=1.5 )
  # ----------------------------------------
  # Now plot the spirals
  for isp, sp in enumerate(spirals):
    # plot markers (these are easy)
    ax.scatter(sp.thetas, sp.radii, marker='o', 
      s = 50, color=spiral_colors[isp] )
    # plot the lines between the markers
    for i in range(NUM_LAMPS-1):
      # matplotlib "line" doesn't plot a real line in polar graphs
      # you have to do interpolation, pick 50 steps per segment
      x = np.linspace( sp.thetas[i], sp.thetas[i+1], 50)
      f = interp1d(sp.thetas[i:i+2], sp.radii[i:i+2])
      y = f(x)
      ax.plot(x, y, '-', color=spiral_colors[isp], 
              linewidth=2, alpha = 0.35 )

  
if plot_positions:
  fig = plt.figure(figsize=(5, 5), dpi=200)
  ax = fig.add_subplot()
  # ----------------------------------------
  # plot the positions
  for isp, sp in enumerate(spirals):
    ax.scatter(sp.xposns, sp.yposns,
       marker='o', s=50, color=spiral_colors[isp] )
  # ----------------------------------------
  # all this code just to set the grid, 
  # axis, ticks, and labels, and background
  # colors
  LW = 1.0
  AL = 0.35
  fig.set_facecolor(had_grey)
  ax.set_facecolor(had_grey)
  ax.xaxis.label.set_color(had_yellow)
  ax.yaxis.label.set_color(had_yellow)
  ax.tick_params(axis='x', colors=had_yellow)
  ax.tick_params(axis='y', colors=had_yellow)
  for x in [ 'bottom', 'top', 'right', 'left', ]:
    ax.spines[x].set_color(had_yellow)
    ax.spines[x].set_linewidth(LW)
    #ax.spines[x].set_alpha(AL)
  # ----------------------------------------
  # setup the axes / grids
  ax.set_xticks( np.arange(115, 160.01, 5) )  # delta 45
  ax.set_yticks( np.arange( 60, 105.01, 5) )  # delta 45
  ax.set_xlim(115,160)
  ax.set_ylim(60,105)
  ax.grid(color=had_yellow, linewidth=LW, alpha=AL)
  ax.yaxis.grid( True,  which='major' )
  ax.xaxis.grid( True,  which='major' )
  ax.set_xticklabels([])
  ax.set_yticklabels([])
  ax.set_xlabel('LED Position, X')
  ax.set_ylabel('LED Position, Y')


if plot_scatter or plot_polar or plot_positions:
  fig.set_dpi(300)
  plt.show()

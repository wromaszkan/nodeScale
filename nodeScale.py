#!/usr/bin/env python

################################################################################
# MIT License
#
# Copyright (c) 2021 UCLA NanoCAD Laboratory
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
################################################################################

""" Scaling area/power/energy/latency between VLSI nodes
Author:        Wojciech Romaszkan
Organization:  NanoCAD Laboratory, University of California, Los Angeles
License:       MIT
"""

import argparse
import logging
import logging.handlers
import sys
import datetime
import socket
import os

__author__ = "Wojciech Romaszkan, NanoCAD Laboratory, UCLA"
__license__ = "MIT"

# Area conversion coefficients
areaDict = {
'180':   {'180': 1  , '130': 0.34, '90': 0.15, '65': 0.08, '45': 0.053, '32': 0.025, '20': 0.011, '16': 0.01 , '14': 0.0093, '10': 0.0055, '7': 0.0032},
'130':   {'180': 2.9, '130': 1   , '90': 0.44, '65': 0.23, '45': 0.16 , '32': 0.072, '20': 0.033, '16': 0.03 , '14': 0.027 , '10': 0.016 , '7': 0.0092},
'90':    {'180': 6.6, '130': 2.3 , '90': 1   , '65': 0.53, '45': 0.35 , '32': 0.16 , '20': 0.075, '16': 0.067, '14': 0.061 , '10': 0.036 , '7': 0.021},
'65':    {'180': 12 , '130': 4.3 , '90': 1.9 , '65': 1   , '45': 0.66 , '32': 0.31 , '20': 0.14 , '16': 0.13 , '14': 0.12  , '10': 0.068 , '7': 0.039},
'45':    {'180': 19 , '130': 6.4 , '90': 2.8 , '65': 1.5 , '45': 1    , '32': 0.46 , '20': 0.21 , '16': 0.19 , '14': 0.17  , '10': 0.1   , '7': 0.059},
'32':    {'180': 40 , '130': 14  , '90': 6.1 , '65': 3.3 , '45': 2.2  , '32': 1    , '20': 0.46 , '16': 0.41 , '14': 0.38  , '10': 0.22  , '7': 0.13},
'20':    {'180': 88 , '130': 30  , '90': 13  , '65': 7.1 , '45': 4.7  , '32': 2.2  , '20': 1    , '16': 0.89 , '14': 0.82  , '10': 0.48  , '7': 0.28},
'16':    {'180': 99 , '130': 34  , '90': 15  , '65': 7.9 , '45': 5.3  , '32': 2.4  , '20': 1.1  , '16': 1    , '14': 0.91  , '10': 0.54  , '7': 0.31},
'14':    {'180': 110, '130': 37  , '90': 16  , '65': 8.7 , '45': 5.8  , '32': 2.7  , '20': 1.2  , '16': 1.1  , '14': 1     , '10': 0.59  , '7': 0.34},
'10':    {'180': 180, '130': 63  , '90': 28  , '65': 15  , '45': 9.8  , '32': 4.5  , '20': 2.1  , '16': 1.9  , '14': 1.7   , '10': 1     , '7': 0.58},
'7':     {'180': 320, '130': 110 , '90': 48  , '65': 25  , '45': 17   , '32': 7.8  , '20': 3.6  , '16': 3.2  , '14': 2.9   , '10': 1.7   , '7': 1},
}

# Energy/power conversion coefficients
depCoeffDict = {
'180'  :[ 0      ,97.09 ,-356.7 ,406.5  ,0       ,24.64    ,-17.98  ,0     ,101000 ,-79720],
'130'  :[ -76.65 ,334.9 ,-493.4 ,275.8  ,7.171   ,-6.709   ,2.904   ,27020 ,-15450 ,5630  ],
'90'   :[ -60.34 ,262.5 ,-384.2 ,210.9  ,4.762   ,-4.781   ,2.092   ,17320 ,-11230 ,4328  ],
'65'   :[ -53.3  ,230.4 ,-333.9 ,178.6  ,3.755   ,-4.398   ,1.975   ,12890 ,-10510 ,4362  ],
'HP45' :[ -501.6 ,1567  ,-1619  ,566.1  ,1.018   ,-0.3107  ,0.1539  ,5462  ,-1760  ,522.4 ],
'HP32' :[ -1047  ,2982  ,-2797  ,873.5  ,0.8367  ,-0.4341  ,0.1701  ,4001  ,-1733  ,533.6 ],
'LP45' :[ -285.7 ,1239  ,-1795  ,898.8  ,1.103   ,-0.362   ,0.2767  ,6297  ,-3009  ,1124  ],
'LP32' :[ -325.9 ,1374  ,-1922  ,913.2  ,0.9559  ,-0.7823  ,0.471   ,4557  ,-3037  ,1323  ],
'HP20' :[ 0      ,34.63 ,-66.37 ,41.15  ,0.373   ,-0.1582  ,0.04104 ,2922  ,-1286  ,299.9 ],
'HP16' :[ 0      ,24.8  ,-47.52 ,28.87  ,0.2958  ,-0.1241  ,0.03024 ,2133  ,-882.6 ,197.7 ],
'HP14' :[ -40.66 ,109.2 ,-100.6 ,35.92  ,0.2363  ,-0.09675 ,0.02239 ,1675  ,-711   ,159   ],
'HP10' :[ -34.95 ,93.65 ,-85.99 ,30.4   ,0.2068  ,-0.09311 ,0.02375 ,1456  ,-621.6 ,143.8 ],
'HP7'  :[ -28.58 ,76.6  ,-70.26 ,24.69  ,0.1776  ,-0.09097 ,0.02447 ,1179  ,-515.7 ,123.4 ],
'LP20' :[ -160.5 ,514.1 ,-558.6 ,217.5  ,0.2632  ,-0.14    ,0.06841 ,2096  ,-962.4 ,287.1 ],
'LP16' :[ -114.6 ,366.7 ,-397.4 ,153.6  ,0.2139  ,-0.1187  ,0.05639 ,1609  ,-715.5 ,205.7 ],
'LP14' :[ -85.37 ,271.6 ,-292.2 ,111.4  ,0.1556  ,-0.06472 ,0.03066 ,1259  ,-554.1 ,152.3 ],
'LP10' :[ -71.76 ,228.6 ,-246.3 ,93.91  ,0.1261  ,-0.0518  ,0.02769 ,1046  ,-422.7 ,118.9 ],
'LP7'  :[ -61.79 ,196.1 ,-210.3 ,79.55  ,0.09365 ,-0.03409 ,0.02043 ,815.2 ,-307.3 ,87.54 ],
}

class nodeScale(object):
   """Class for converting metrics"""
   
   def __init__(self):
      """Initialize the object
      
      Arguments:
      """
      # Get logging info if called
      logging.getLogger(__name__)

   def convert(self, metric, value, srcNode, dstNode, srcVdd=1, dstVdd=1):
      """Run simulation
      
      Arguments:
      - metric: metric to convert (area/power/energy/delay)
      - value: value to convert
      - srcNode: source node
      - dstNode: destination node
      - srcVdd: source voltage
      - dstVdd: destination voltage
      """

      logging.info("Converting {}: {} from {} to {}. Source VDD: {}, Destination VDD: {}".format(metric, value, srcNode, dstNode, srcVdd, dstVdd))

      if (metric == 'area'):
         if(srcNode[1] == "P"):
            srcNode = srcNode[2:]
         if(dstNode[1] == "P"):
            dstNode= dstNode[2:]
         area = float(value)/areaDict[dstNode][srcNode]
         logging.info("Scaled area: {}".format(area))
         return(area)
      elif (metric == 'd'):
         dFacSrc = depCoeffDict[srcNode][0]*float(srcVdd)**3 + \
                  depCoeffDict[srcNode][1]*float(srcVdd)**2 + \
                  depCoeffDict[srcNode][2]*float(srcVdd)    + \
                  depCoeffDict[srcNode][3]
         dFacDst = depCoeffDict[dstNode][0]*float(dstVdd)**3 + \
                  depCoeffDict[dstNode][1]*float(dstVdd)**2 + \
                  depCoeffDict[dstNode][2]*float(dstVdd)    + \
                  depCoeffDict[dstNode][3]
         delay = float(value) * dFacDst/dFacSrc
         logging.infoprint("Scaled delay: {}".format(delay))
         return(delay)
      elif (metric == 'energy'):
         eFacSrc = depCoeffDict[srcNode][4]*float(srcVdd)**2 + \
                  depCoeffDict[srcNode][5]*float(srcVdd)**1 + \
                  depCoeffDict[srcNode][6]
         eFacDst = depCoeffDict[dstNode][4]*float(dstVdd)**2 + \
                  depCoeffDict[dstNode][5]*float(dstVdd)**1 + \
                  depCoeffDict[dstNode][6]
         energy = float(value) * eFacDst/eFacSrc
         logging.info("Scaled energy: {}".format(energy))
         return(energy)
      elif (metric == 'power'):
         pFacSrc = depCoeffDict[srcNode][7]*float(srcVdd)**2 + \
                  depCoeffDict[srcNode][8]*float(srcVdd)**1 + \
                  depCoeffDict[srcNode][9]
         pFacDst = depCoeffDict[dstNode][7]*float(dstVdd)**2 + \
                  depCoeffDict[dstNode][8]*float(dstVdd)**1 + \
                  depCoeffDict[dstNode][9]
         power = float(value) * pFacDst/pFacSrc
         logging.info("Scaled power: {}".format(power))
         return(power)

def main():

   #################################################
   # Argument parses
   parser = argparse.ArgumentParser(description='Convert area/delay/power/energy between VLSI nodes')
   # Metric to convert
   parser.add_argument('-c', dest='convert', help='Convert "a" - area, "d" - delay, "p" - power, "e" - energy')
   # Source node
   parser.add_argument('-s', dest='source',  help='Source node: 180, 130, 90, 65, [HP/LP]45/32/20/16/14/10/7')
   # Destination node
   parser.add_argument('-d', dest='dest',    help='Destination node: 180, 130, 90, 65, [HP/LP]45/32/20/16/14/10/7')
   # Converted value
   parser.add_argument('-v', dest='value',   help='Value to convert')
   # Source voltage
   parser.add_argument('-t', dest='svolt',   help='Source Voltage')
   # Destination voltage
   parser.add_argument('-u', dest='dvolt',   help='Destination Voltage')

   args = parser.parse_args()

   # Convert metric names
   mtrDict = {'a': 'area', 'p': 'power', 'e': 'energy', 'd': 'delay'}
   metric = mtrDict[args.convert]


   # Logging
   logFile = "nodeScale.log"
   logLev  = logging.INFO

   # Stream handler for printing
   logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
   rootLogger = logging.getLogger()
   # Clean up old handlers
   rootLogger.handlers = []

   # Set up file logging
   fileHandler = logging.handlers.RotatingFileHandler("{0}/{1}".format("./", logFile), backupCount=10)
   fileHandler.setFormatter(logFormatter)
   rootLogger.addHandler(fileHandler)

   # Set up console logging
   consoleHandler = logging.StreamHandler(sys.stdout)
   consoleHandler.setFormatter(logFormatter)
   rootLogger.addHandler(consoleHandler)

   # Set up logging level
   rootLogger.setLevel(logLev)

   # Get current time
   curTime = datetime.datetime.now()
   logging.info("Timestamp: " + str(curTime))

   # Hostname  
   logging.info("Hostname: " + socket.gethostname())

   # Get PID
   logging.info("PID: " + str(os.getpid()))

   # Run conversion 
   ndScl = nodeScale()
   ndScl.convert(metric, args.value, args.source, args.dest, args.svolt, args.dvolt)

if __name__ == '__main__':
   main()


'''
 * @(#) TopCode.py
 * 
 * Tangible Object Placement Codes (TopCodes)
 * Copyright (c) 2007 Michael S. Horn
 * 
 *           Michael S. Horn (michael.horn@tufts.edu)
 *           Tufts University Computer Science
 *           161 College Ave.
 *           Medford, MA 02155
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License (version 2) as
 * published by the Free Software Foundation.
 * 
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
'''

import math
import numpy as np
#from Scanner import Scanner

'''
 * TopCodes (Tangible Object Placement Codes) are black-and-white
 * circular fiducials designed to be recognized quickly by
 * low-resolution digital cameras with poor optics. The TopCode symbol
 * format is based on the open SpotCode format:
 *
 *  http://www.highenergymagic.com/spotcode/symbols.html
 *
 * Each TopCode encodes a 13-bit number in a single data ring on the
 * outer edge of the symbol. Zero is represented by a black sector and
 * one is represented by a white sector.
 *
 * @author Michael Horn, Port by Daniel Nugent
 * @version $Revision: 1.4 $, $Date: 2015/7/30 $
'''



class TopCode(object):
   

    '''
    Create a topcode. ID number optional
    '''
    def __init__(self, code = None):
        # Number of sectors in the data ring 
        self.SECTORS = 13

        # Width of the code in units (ring widths) 
        self.WIDTH = 8

        # Span of a data sector in radians 
        self.ARC = (2.0 * math.pi / self.SECTORS)



        # The symbol's code, or -1 if invalid. 
        self.code = -1

        # The width of a single ring. 
        self.unit = 72.0 / self.WIDTH
       
        # The angular orientation of the symbol (in radians) 
        self.orientation = 0

        # Horizontal center of a symbol 
        self.x = 0.0

        # Vertical center of a symbol 
        self.y = 0.0

        # Buffer used to decode sectors 
        self.core = np.zeros((self.WIDTH), np.int)

        if code is not None:
            self.code = code

        self.q = 0

    '''
    Returns the ID number for this symbol.  Calling the decode()
    function will set this value automatically.
    '''
    def getCode(self):
        return self.code

    '''
    Sets the ID number for this symbol.
    '''
    def setCode(self, code):
        self.code = code

    '''
    Returns the orientation of this code in radians and accurate
    to about plus or minus one degree.  This value gets set
    automatically by the decode() function.
    '''
    def getOrientation(self):
        return self.orientation

    '''
    Sets the angular orientation of this code in radians.
    '''
    def setOrientation(self, orientation):
          self.orientation = orientation
   
    '''
    Returns the diameter of this code in pixels.  This value
    will be set automatically by the decode() function.
    '''
    def getDiameter(self):
        return self.unit * self.WIDTH
   
    '''
    Sets the diameter of this code in pixels.
    '''
    def setDiameter(self, diameter):
        self.unit = diameter / self.WIDTH
   
   
    '''
    Returns the x-coordinate for the center point of the symbol.
    This gets set automatically by the decode() function.
    '''
    def getCenterX(self):
        return self.x
   

    '''
    Returns the y-coordinate for the center point of the symbol.
    This gets set automatically by the decode() function.
    '''
    def getCenterY(self):
        return self.y
   

    '''
    Sets the x- and y-coordinates for the center point of the symbol.
    '''
    def setLocation(self, x, y):
        self.x = x
        self.y = y
   

    '''
    Returns True if this code was sucessfully decoded.
    '''
    def isValid(self):
        return self.code > 0


    '''
    Decodes a symbol given any point (cx, cy) inside the center
    circle (bulls-eye) of the code.  
    '''
    def decode(self, scanner, cx, cy):


        up = (scanner.ydist(cx, cy, -1) + scanner.ydist(cx - 1, cy, -1) + scanner.ydist(cx + 1, cy, -1))

        down = (scanner.ydist(cx, cy, 1) + scanner.ydist(cx - 1, cy, 1) + scanner.ydist(cx + 1, cy, 1))

        left = (scanner.xdist(cx, cy, -1) + scanner.xdist(cx, cy - 1, -1) + scanner.xdist(cx, cy + 1, -1))


        right = (scanner.xdist(cx, cy, 1) + scanner.xdist(cx, cy - 1, 1) + scanner.xdist(cx, cy + 1, 1))

        self.x = cx
        self.y = cy
        self.x += (right - left) / 6.0
        self.y += (down - up) / 6.0
        self.unit = self.readUnit(scanner)
        self.code = -1
        if (self.unit < 0):
             return -1

        c = 0
        maxc = 0
        arca = 0.0
        maxa = 0.0
        maxu = 0.0

        '''
        ------------------------------------------
        | Try different unit and arc adjustments, |
        | save the one that produces a maximum    |
        | confidence reading...                   |
        ------------------------------------------
          '''
        for u in range(-2,3):
            for a in range(0,10):
                arca = a * self.ARC * 0.1
                c = self.readCode(scanner,self.unit + (self.unit * 0.05 * u), arca)
                if( c > maxc):
                    maxc = c
                    maxa = arca
                    maxu = self.unit + (self.unit * 0.05 * u)


          #One last call to readCode to reset orientation and code
        if (maxc > 0):
            self.unit = maxu
            self.readCode(scanner, self.unit, maxa)
            self.code = self.rotateLowest(self.code, maxa)
      
        return self.code

    '''
    Attempts to decode the binary pixels of an image into a code
    value.
     
    scanner - image scanner
    unit    - width of a single ring (codes are 8 units wide)
    arca    - Arc adjustment.  Rotation correction delta value.    
    '''
    def readCode(self, scanner, unit, arca):

        dx , dy = 0.0, 0.0  # direction vector
        dist = 0.0
        c = 0
        sx, sy = 0, 0
        bit, bits = 0, 0
        self.code = -1
        
        for sector in range(self.SECTORS - 1, -1, -1):
            dx = math.cos(self.ARC * sector + arca)
            dy = math.sin(self.ARC * sector + arca)
            # Take 8 samples across the diameter of the symbol
            for i in range(0, self.WIDTH):
                dist = (i - 3.5) * unit
                sx = int(round(self.x + float(dx) * dist))
                sy = int(round(self.y + float(dy) * dist))
                self.core[i] = scanner.getSample3x3(sx, sy)
                
         

            # white rings
            if (self.core[1] <= 128 or self.core[3] <= 128 or self.core[4] <= 128 or self.core[6] <= 128):
                return 0
         

            # black ring
            if (self.core[2] > 128 or self.core[5] > 128):
                return 0

            # compute confidence in self.core sample
            c += (self.core[1] + self.core[3] + self.core[4] + self.core[6] + (0xff - self.core[2]) + (0xff - self.core[5]))

            # data rings
            c += abs(self.core[7] * 2 - 0xff)

            # opposite data ring
            c += (0xff - abs(self.core[0] * 2 - 0xff))

            bit = 1 if (self.core[7] > 128) else 0
            bits <<= 1
            bits += bit

        if (self.checksum(bits)):
            self.code = bits
            return c
        else:
            return 0
     
 

      
    '''
    rotateLowest() tries each of the possible rotations and returns
    the lowest.  
    '''
    def rotateLowest(self, bits, arca):
        min = bits
        mask = 0x1fff

        # slightly overcorrect arc-adjustment
        # ideal correction would be (self.ARC / 2),
        # but there seems to be a positive bias
        # that falls out of the algorithm.
        arca -= (self.ARC * 0.65)
      
        self.orientation = 0

        for i in range(1, self.SECTORS + 1):
            bits = (((bits << 1) & mask) | (bits >> (self.SECTORS - 1)))
            if (bits < min): 
                min = bits
                self.orientation = (i * -self.ARC)

        self.orientation += arca
        return min
   
   
    '''
    Only codes with a checksum of 5 are valid
    '''
    def checksum(self, bits):
        sum = 0
        for i in range(0,self.SECTORS):
            sum += (bits & 0x01)
            bits = bits >> 1
        return (sum == 5)

   
    '''
    Returns True if the given point is inside the bulls-eye
    '''
    def inBullsEye(self, px, py):
        return (((self.x - px) * (self.x - px) + (self.y - py) * (self.y - py)) <= (self.unit * self.unit))


    '''
    Determines the symbol's unit length by counting the number
    of pixels between the outer edges of the first black ring. 
    North, south, east, and west readings are taken and the average
    is returned.
    '''
    def readUnit(self, scanner): 
        sx = int(round(self.x))
        sy = int(round(self.y))
        iwidth = scanner.getImageWidth()
        iheight = scanner.getImageHeight()

        whiteL = True
        whiteR = True
        whiteU = True
        whiteD = True  
        sample = 0
        distL = 0
        distR = 0
        distU = 0
        distD = 0
        i = 1
        while True:
            if (sx - i < 1 or sx + i >= iwidth - 1 or sy - i < 1 or sy + i >= iheight - 1 or i > 100):
                return -1

            # Left sample
            sample = scanner.getBW3x3(sx - i, sy)
            if (distL <= 0): 
                if (whiteL and sample == 0):
                    whiteL = False
                elif (not whiteL and sample == 1):
                    distL = i

            # Right sample
            sample = scanner.getBW3x3(sx + i, sy)
            if (distR <= 0): 
                if (whiteR and sample == 0):
                    whiteR = False
                elif (not whiteR and sample == 1):
                    distR = i

            # Up sample
            sample = scanner.getBW3x3(sx, sy - i)
            if (distU <= 0):
                if (whiteU and sample == 0):
                    whiteU = False
                elif (not whiteU and sample == 1):
                    distU = i

             
            # Down sample
            sample = scanner.getBW3x3(sx, sy + i)
            if (distD <= 0):
                if (whiteD and sample == 0):
                    whiteD = False
                elif (not whiteD and sample == 1):
                    distD = i

            if (distR > 0 and distL > 0 and distU > 0 and distD > 0):
                u = (distR + distL + distU + distD) / 8.0
                if (abs(distR + distL - distU - distD) > u):
                    return -1
                else:
                    return u
            i += 1


    def annotate(self, img, scanner):
        dx, dy = 0,0
        dist = 0
        sx, sy = 0,0
        bits = 0

        for sector in range(self.SECTORS -1, -1, -1):
            dx = math.cos(self.ARC * sector + orientation)
            dy = math.sin(self.ARC * sector + orientation)
      
            # Take 8 samples across the diameter of the symbol
            sample = 0
            for i in range(3,self.WIDTH):
                dist = (i - 3.5) * self.unit

                sx = int(round(x + dx * dist))
                sy = int(round(y + dy * dist))
                sample = scanner.getBW3x3(sx, sy)
                '''
                g.setColor(Color.BLACK if (sample == 0) else Color.WHITE)
                Rectangle2D rect = new Rectangle2D.Float(sx - 0.6, sy - 0.6, 1.2, 1.2)
                g.fill(rect)
                g.setColor(Color.RED)
                g.setStroke(new BasicStroke(0.25))
                g.draw(rect)
                '''
   
    '''
    Draws this spotcode with its current location and orientation
    '''
    def draw(self, img):

        bits = self.code
        '''
        arc = Arc2D.Float(Arc2D.PIE)
        sweep = 360.0f / self.SECTORS
        sweepa = (-orientation * 180 / math.pi())

        r = self.WIDTH * 0.5 * self.unit
      

        circ = Ellipse2D.Float(x - r, y - r, r * 2, r * 2)
        g.setColor(Color.white)
        g.fill(circ)
      
        for i in range(self.SECTORS - 1, -1, -1):
            arc.setArc(x - r, y - r, r * 2, r * 2, i * sweep + sweepa, sweep, Arc2D.PIE)
            g.setColor(Color.white if ((bits & 0x1) > 0) else Color.black)
            g.fill(arc)
            bits >>= 1

        r -= self.unit
        g.setColor(Color.white)
        circ.setFrame(x - r, y - r, r * 2, r * 2)
        g.fill(circ)

        r -= self.unit
        g.setColor(Color.black)
        circ.setFrame(x - r, y - r, r * 2, r * 2)
        g.fill(circ)

        r -= self.unit
        g.setColor(Color.white)
        circ.setFrame(x - r, y - r, r * 2, r * 2)
        g.fill(circ)
        '''

    '''
    Debug routine that prints the 13 least significant bits of a
    integer.    
    '''
    def printBits(self, bits):
        for i in range(self.SECTORS-1, -1, -1):
            if (((bits>>i) & 0x01) == 1):
                print "1"
            else:
                print "0"
            if ((44 - i) % 4 == 0):
                print " " 
      
        print " = " + bits


   
    '''
     Generates a list of all valid TopCodes
    '''
    def generateCodes(self):
        
        n = 99
        base = 0 
        codes = []
        code = TopCode()

        bits = 0
        count = 0
      
        while (count < n):
            bits = code.rotateLowest(base, 0)

            # Found a valid code
            if (bits == base and code.checksum(bits)):
                code.setCode(bits)
                code.setOrientation(0)
                codes.append(code)
                code = TopCode()
                count += 1
 

            # Try next value
            base += 1
        return codes
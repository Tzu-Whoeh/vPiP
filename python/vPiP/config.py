# Copyright 2016 Brian Innes
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from os.path import expanduser, isfile, exists, dirname
from os import makedirs
from .coordinates import Coordinate, PolarCoordinate
from math import sqrt, floor
import errno

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


class PolarConfig:
    def __init__(self):
        self.resetCommand = -128
        self.penUpCommand = -127
        self.penDownCommand = 127
        self.stepsMaxValue = 126.0
        self.configFile = None
        self.configured = False
        self.penSize = 0
        self.machineWidth = 0
        self.machineHeight = 0
        self.mmPerRev = 0.0
        self.stepsPerRev = 0
        self.stepMultiplier = 0
        self.serialPort = ''
        self.timeSliceUS = 0
        self.baud = 0
        self.motorAccel = 0.0
        self.motorMaxSpeed = 0.0
        self.penUp = 0
        self.penDown = 0
        self.homeX = 0
        self.homeY = 0
        self.polarDraw = False
        self.size = ''
        self.width = 0
        self.height = 0
        self.posX = 0
        self.posY = 0
        self.margin = 0
        self.pixels = 0
        self.rotate = False
        self.screenX = 0
        self.showImage = False
        self.saveImage = False
        self.stepsSizeMM = 0.0
        self.stepsPerValue = 0.0
        self.MaxSpeedMMs = 0.0
        self.AccelerationMMs2 = 0.0
        self.pixelsPerMM = 0.0
        self.heightPixels = 0.0
        self.heightScreen = 0
        self.loadConfig()

    def __str__(self):
        return '\n'.join(
            ("***** System configuration *****",
             "configured = {}".format(self.configured),
             "penSize = {}".format(self.penSize),
             "machineWidth = {}".format(self.machineWidth),
             "machineHeight = {}".format(self.machineHeight),
             "mmPerRev = {}".format(self.mmPerRev),
             "stepsPerRev = {}".format(self.stepsPerRev),
             "stepMultiplier = {}".format(self.stepMultiplier),
             "serialPort = {}".format(self.serialPort),
             "timeSliceUS = {}".format(self.timeSliceUS),
             "baud = {}".format(self.baud),
             "motorAccel = {}".format(self.motorAccel),
             "motorMaxSpeed = {}".format(self.motorMaxSpeed),
             "penUp = {}".format(self.penUp),
             "penDown = {}".format(self.penDown),
             "homeX = {}".format(self.homeX),
             "homeY = {}".format(self.homeY),
             "polarDraw = {}".format(self.polarDraw),
             "size = {}".format(self.size),
             "width = {}".format(self.width),
             "height = {}".format(self.height),
             "posX = {}".format(self.posX),
             "posY = {}".format(self.posY),
             "margin = {}".format(self.margin),
             "pixelsX = {}".format(self.pixels),
             "pixelsY = {}".format(self.heightPixels),
             "rotate = {}".format(self.rotate),
             "stepsSizeMM = {}".format(self.stepsSizeMM),
             "stepsPerValue = {}".format(self.stepsPerValue),
             "MaxSpeedMMs = {}".format(self.MaxSpeedMMs),
             "AccelerationMMs2 = {}".format(self.AccelerationMMs2),
             "screenX = {}".format(self.screenX),
             "screenY = {}".format(self.heightScreen),
             "showImage = {}".format(self.showImage),
             "saveImage = {}".format(self.saveImage)))

    def loadConfig(self):
        self.configFile = expanduser("~/.vpip/config.cfg")
        print("Config is being read from %s\n" % self.configFile)
        if isfile(self.configFile):
            config = configparser.ConfigParser()
            config.read(self.configFile)
            self.configured = True
            self.penSize = config.getfloat('vpip', 'penSize')
            self.machineWidth = config.getint('vpip', 'machineWidth')
            self.machineHeight = config.getint('vpip', 'machineHeight')
            self.mmPerRev = config.getfloat('vpip', 'mmPerRev')
            self.stepsPerRev = config.getint('vpip', 'stepsPerRev')
            self.stepMultiplier = config.getint('vpip', 'stepMultiplier')
            self.serialPort = config.get('vpip', 'serialPort')
            self.timeSliceUS = config.getfloat('vpip', 'timeSliceUS')
            self.baud = config.getint('vpip', 'baud')
            self.motorAccel = config.getfloat('vpip', 'motorAccel')
            self.motorMaxSpeed = config.getfloat('vpip', 'motorMaxSpeed')
            self.penUp = config.getint('vpip', 'penUp')
            self.penDown = config.getint('vpip', 'penDown')
            self.homeX = config.getint('vpip', 'homeX')
            self.homeY = config.getint('vpip', 'homeY')
            self.polarDraw = config.getboolean('vpip', 'polarDraw')
            self.size = config.get('Paper', 'size')
            self.width = config.getint('Paper', 'width')
            self.height = config.getint('Paper', 'height')
            self.posX = config.getint('Paper', 'posX')
            self.posY = config.getint('Paper', 'posY')
            self.margin = config.getint('Paper', 'margin')
            self.pixels = config.getint('Paper', 'pixels')
            self.rotate = config.getboolean('Paper', 'rotate')
            self.screenX = config.getint('Screen', 'screenX')
            self.showImage = config.getboolean('Screen', 'showImage')
            self.saveImage = config.getboolean('Screen', 'saveImage')
        else:
            self.configured = False
            self.createDefaultConfig()
            self.loadConfig()
        if self.rotate:
            self.width, self.height = self.height, self.width
        self.stepsSizeMM = (1.0 / self.stepsPerRev / self.stepMultiplier) * self.mmPerRev
        stepsPerRevolution = self.stepsPerRev * self.stepMultiplier
        self.stepsPerValue = self.stepsMaxValue / self.stepMultiplier
        self.MaxSpeedMMs = min(self.motorMaxSpeed, (
            (self.stepsPerValue / (self.timeSliceUS / 1000000.0)) / stepsPerRevolution) * self.mmPerRev)
        self.AccelerationMMs2 = self.MaxSpeedMMs / self.motorAccel
        self.pixelsPerMM = float(self.pixels) / (self.width - 2 * self.margin)
        self.heightPixels = int(floor(float(self.height - 2 * self.margin) * self.pixelsPerMM))
        self.heightScreen = int(floor(float(self.heightPixels) * self.screenX / self.pixels))

    def createDefaultConfig(self):
        config = configparser.ConfigParser()
        config.add_section('vpip')
        config.set('vpip', 'penSize', '1.0')
        config.set('vpip', 'machineWidth', '1')
        config.set('vpip', 'machineHeight', '1')
        config.set('vpip', 'mmPerRev', '1.0')
        config.set('vpip', 'stepsPerRev', '1')
        config.set('vpip', 'stepMultiplier', '1')
        config.set('vpip', 'serialPort', 'none')
        config.set('vpip', 'timeSliceUS', '1.0')
        config.set('vpip', 'baud', '57600')
        config.set('vpip', 'motorAccel', '1.0')
        config.set('vpip', 'motorMaxSpeed', '1.0')
        config.set('vpip', 'penUp', '0')
        config.set('vpip', 'penDown', '0')
        config.set('vpip', 'homeX', '0')
        config.set('vpip', 'homeY', '0')
        config.set('vpip', 'polarDraw', 'True')
        config.add_section('Paper')
        config.set('Paper', 'size', 'custom')
        config.set('Paper', 'width', '1')
        config.set('Paper', 'height', '1')
        config.set('Paper', 'posX', '1')
        config.set('Paper', 'posY', '1')
        config.set('Paper', 'margin', '1')
        config.set('Paper', 'pixels', '1')
        config.set('Paper', 'rotate', 'False')
        config.add_section('Screen')
        config.set('Screen', 'screenX', '1')
        config.set('Screen', 'showImage', 'False')
        config.set('Screen', 'saveImage', 'False')
        if not exists(dirname(self.configFile)):
            try:
                makedirs(dirname(self.configFile))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(self.configFile, 'w') as configfile:
            config.write(configfile)

    def writeConfig(self):
        if self.configured:
            config = configparser.ConfigParser()
            config.add_section('vpip')
            config.set('vpip', 'penSize', self.penSize)
            config.set('vpip', 'machineWidth', self.machineWidth)
            config.set('vpip', 'machineHeight', self.machineHeight)
            config.set('vpip', 'mmPerRev', self.mmPerRev)
            config.set('vpip', 'stepsPerRev', self.stepsPerRev)
            config.set('vpip', 'stepMultiplier', self.stepMultiplier)
            config.set('vpip', 'serialPort', self.serialPort)
            config.set('vpip', 'timeSliceUS', self.timeSliceUS)
            config.set('vpip', 'baud', self.baud)
            config.set('vpip', 'motorAccel', self.motorAccel)
            config.set('vpip', 'motorMaxSpeed', self.motorMaxSpeed)
            config.set('vpip', 'penUp', self.penUp)
            config.set('vpip', 'penDown', self.penDown)
            config.set('vpip', 'homeX', self.homeX)
            config.set('vpip', 'homeY', self.homeY)
            config.set('vpip', 'polarDraw', self.polarDraw)
            config.add_section('Paper')
            config.set('Paper', 'size', self.size)
            config.set('Paper', 'width', self.width)
            config.set('Paper', 'height', self.height)
            config.set('Paper', 'posX', self.posX)
            config.set('Paper', 'posY', self.posY)
            config.set('Paper', 'margin', self.margin)
            config.set('Paper', 'pixelsX', self.pixels)
            config.set('Paper', 'rotate', self.rotate)
            config.add_section('Screen')
            config.set('Screen', 'screenX', self.screenX)
            config.set('Screen', 'showImage', self.showImage)
            config.set('Screen', 'saveImage', self.saveImage)
            if not exists(dirname(self.configFile)):
                try:
                    makedirs(dirname(self.configFile))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            with open(self.configFile, 'w') as configfile:
                config.write(configfile)
        else:
            print('ERROR-Trying to write configuration when unconfigured!')

    def system2drawingCoords(self, coord):
        """
        :param coord:
        :rtype: Coordinate
        """
        mmCoord = coord.translate(self.posX - self.margin, self.posY - self.margin)
        return mmCoord * self.pixelsPerMM

    def drawing2systemCoords(self, coord):
        """
        :param coord:
        :rtype: Coordinate
        """
        mmCoord = coord.divide(self.pixelsPerMM)
        return mmCoord.translate(self.posX + self.margin, self.posY + self.margin)

    def drawing2screenCoords(self, coord):
        """
        :type coord: Coordinate
        :rtype: Coordinate
        """
        return coord * self.screenX / self.pixels

    def system2polarCoords(self, coord):
        """
        :param coord:
        :rtype: PolarCoordinate
        """
        xdiff = float(self.machineWidth) - coord.x
        return PolarCoordinate.fromCoords(sqrt(coord.x * coord.x + coord.y * coord.y),
                                          sqrt(xdiff * xdiff + coord.y * coord.y), coord.penup)

    def polar2systemCoords(self, coord):
        """
        :param coord:
        :rtype: Coordinate
        """
        if coord.leftDist + coord.rightDist > self.machineWidth:
            # print "polar2systemCoords-{}".format(coord)
            x = ((float(coord.leftDist * coord.leftDist) - (coord.rightDist * coord.rightDist) +
                  float(self.machineWidth * self.machineWidth)) / (2.0 * self.machineWidth))
            y = sqrt((coord.leftDist * coord.leftDist) - (x * x))
            return Coordinate.fromCoords(x, y, coord.penup)
        else:
            print("WARN: polar2systemCoords received invalid coordinate {}").format(coord)
            return Coordinate.fromCoords(0, 0, coord.penup)

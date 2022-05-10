from abc import abstractmethod
import os
import logging
import logging.handlers
import discord
from sgl.discord import Util


class APlugin():
  pluginName = None
  logger: logging.Logger = None

  @property
  @abstractmethod
  def discordEventBusCallbacks(self):
    raise NotImplementedError("Property discordEventBusCallbacks is not implemented")

  @staticmethod
  @abstractmethod
  def pluginDescription():
    raise NotImplementedError("Method pluginDescription is not implemented")

  @staticmethod
  @abstractmethod
  def checkConfiguration():
    raise NotImplementedError("Method checkConfiguration is not implemented")

  def __init__(self, child):
    self.pluginName = child if type(child) == str else child.__name__
    self.logger = self.getLogger()

  def getLogger(self, maxBytes=100000000, backupCount=10):
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    filePath = os.path.realpath('./log/' + self.pluginName + '.log')
    Util.createSubDirWhenMissing(filePath)
    handler = logging.handlers.RotatingFileHandler(filePath, maxBytes=maxBytes, backupCount=backupCount)
    # formatter = logging.Formatter('%(asctime)s|%(process)d|%(threadName)s %(name)s %(pathname)s %(filename)s:%(module)s:%(funcName)s(%(lineno)d) [%(levelname)s]: %(message)s')
    formatter = logging.Formatter('%(asctime)s:%(funcName)s(%(lineno)d) [%(levelname)s]: %(message)s')
    # formatter.converter = time.gmtime  # if you want UTC time
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

  def printException(self, msg='EXCEPTION IN'):
    Util.printException(msg, self.logger)

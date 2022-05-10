import sys, os
from abc import abstractmethod
import logging
import logging.handlers
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
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(self._setupFileHandler(maxBytes, backupCount))
    logger.addHandler(self._setupConsoleHandler())
    return logger

  def _setupFileHandler(self, maxBytes, backupCount):
    filePath = os.path.realpath('./log/' + self.pluginName + '.log')
    Util.createSubDirWhenMissing(filePath)
    handler = logging.handlers.RotatingFileHandler(filePath, maxBytes=maxBytes, backupCount=backupCount, encoding='utf-8')
    # formatter = logging.Formatter('%(asctime)s|%(process)d|%(threadName)s %(name)s %(pathname)s %(filename)s:%(module)s:%(funcName)s(%(lineno)d) [%(levelname)s]: %(message)s')
    formatter = logging.Formatter('%(asctime)s:%(funcName)s(%(lineno)d) [%(levelname)s]: %(message)s')
    # formatter.converter = time.gmtime  # if you want UTC time
    handler.setFormatter(formatter)
    return handler

  def _setupConsoleHandler(self):
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    return handler

  def printException(self, msg='EXCEPTION IN'):
    Util.printException(msg, self.logger)

from importlib import import_module
import discord
from sgl.discord import Util
from sgl.discord.APlugin import APlugin
from sgl.discord.Conf import Conf
from sgl.discord.DiscordEventBus import DiscordEventBus


def _loadClass(className, package='sgl.discord.plugins'):
  Class = None
  try:
    moduleName = '{0}.{1}'.format(package, className)
    module = import_module(moduleName)
    Class = getattr(module, className)
  except Exception:
    Util.printException()
  return Class


def loadAll(client: discord.Client, discordEventBus: DiscordEventBus = None, printPluginDescriptionMode=1):
  isFailedAny = False  # Keep testing the rest and return nothing
  plugins: dict = {}
  for className in Conf.data['app']['plugins']:
    APluginClass = _loadClass(className)
    if APluginClass is None:
      print("Failed to find plugin {0}".format(className))
      continue
    try:
      if APluginClass.checkConfiguration():
        plugin: APlugin = APluginClass(client)
        if discordEventBus: discordEventBus.add(plugin)
        plugins[className] = plugin
        if printPluginDescriptionMode > 1: print(APluginClass.pluginDescription())
      else:
        if printPluginDescriptionMode > 0: print(APluginClass.pluginDescription())
        isFailedAny = True
    except Exception:
      isFailedAny = True  # Keep testing the rest and return nothing
      Util.printException("Failed to create plugin {0}".format(className))
      if className in plugins:
        plugins.pop(className)

  if isFailedAny:
    Conf.saveConfigFile()
    return None

  return plugins

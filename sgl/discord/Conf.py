import io, pathlib, json
import os

import sgl.discord.Util as Util


class Conf():
  """Static Config Provider"""

  filePath = None
  confFolder = None
  data = {"app": None}

  @staticmethod
  def loadConfigFile(filePath):
    Util.createSubDirWhenMissing(filePath)
    Conf.filePath = filePath
    Conf.confFolder = pathlib.Path(filePath).parent.absolute()
    jsonData = Conf.readFileToJson(filePath)

    Conf.data["app"] = jsonData if jsonData else {}
    if not "plugins" in Conf.data["app"]:
      Conf.data["app"]["plugins"] = Conf._listAvailablePlugins()
    for plugin in Conf.data["app"]["plugins"]:
      pluginFilePath = "{0}/{1}".format(Conf.confFolder, plugin + '.json')
      if not pathlib.Path(pluginFilePath).is_file(): continue
      jsonData = Conf.readFileToJson(pluginFilePath)
      if jsonData:
        Conf.data[plugin] = jsonData

    if jsonData == None:
      Conf.saveConfigFile()
      print("A default config was generated, please inspect it at '{0}'".format(filePath))

  @staticmethod
  def _listAvailablePlugins():
    try:
      filesInPluginsFolder = os.listdir(os.path.dirname(os.path.realpath(__file__)) + '/plugins')
      pluginFiles = filter(lambda file: not file.startswith('__'), filesInPluginsFolder)
      return [(file.replace('.py', '')) for file in pluginFiles]
    except Exception:
      Util.printException()

  @staticmethod
  def saveConfigFile(sort_keys=False, indent=4, ensure_ascii=False):
    Conf.saveJsonToFile(Conf.data["app"], Conf.filePath, sort_keys, indent, ensure_ascii)
    for plugin in Conf.data:
      if plugin == "app": continue
      pluginFilePath = "{0}/{1}".format(Conf.confFolder, plugin + '.json')
      Conf.saveJsonToFile(Conf.data[plugin], pluginFilePath, sort_keys, indent, ensure_ascii)

  @staticmethod
  def readFileToJson(filePath):
    result = None
    file = None
    try:
      file = io.open(filePath, 'r', encoding='utf8')
      result = json.load(file)
    except Exception:
      Util.printException()
    finally:
      if file and not file.closed:
        file.close()
    return result

  @staticmethod
  def saveJsonToFile(jsonData, filePath, sort_keys=False, indent=4, ensure_ascii=False):
    file = None
    try:
      file = io.open(filePath, 'w', encoding='utf8')
      file.write(json.dumps(jsonData, sort_keys=sort_keys, indent=indent, ensure_ascii=ensure_ascii))
    except Exception:
      Util.printException()
    finally:
      if file and not file.closed:
        file.close()

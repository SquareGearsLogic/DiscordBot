import pathlib, os
import linecache
import sys


def createSubDirWhenMissing(filePath):
  logDir = pathlib.Path(os.path.realpath(filePath)).parent.absolute()
  if not logDir.is_dir():
    logDir.mkdir(parents=True, exist_ok=True)


def printException(msg='EXCEPTION IN', logger=None):
  exc_type, exc_obj, tb = sys.exc_info()
  f = tb.tb_frame
  lineno = tb.tb_lineno
  filename = f.f_code.co_filename
  linecache.checkcache(filename)
  # line = linecache.getline(filename, lineno, f.f_globals)
  msg = '{} {}({}): {}'.format(msg, filename, lineno, exc_obj)
  if logger:
    logger.error(msg)
  else:
    print(msg)

import asyncio
import logging

from sgl.discord import Util


class DiscordEventBus():
  """TODO: Well, probably I'm reinventing a wheel, but I didn't get how to subscribe multiple listeners to a single discord.Client object\n
     Use this Bus to subscribe you discord plugins for events of shared discord.Client object (i.e. single connection to discord).\n
     Your plugin class must have "discordEventBusCallbacks" dictionary field that maps discord.Client event_names to your class methods"""

  listeners = None
  client = None
  isLocked = False

  def __init__(self, client):
    self.client = client
    self._bindEvents()

  def add(self, listener):
    """Add your plugin class object that contains "discordEventBusCallbacks" dictionary field before calling discord.Client::run()"""
    if self.isLocked or listener is None or hasattr(listener, 'discordEventBusCallbacks')==False or listener.discordEventBusCallbacks is None:
      return False
    for eventName in listener.discordEventBusCallbacks:
      self.listeners[eventName].append(listener)
    return True

  def remove(self, listener):
    """Remove your plugin class object that contains "discordEventBusCallbacks" dictionary field after your discord.Client is disconnected"""
    if self.isLocked: return False
    for eventListeners in self.listeners:
      if listener in self.listeners[eventListeners]: self.listeners[eventListeners].remove(listener)
    return True

  def list(self):
    """Lists all supported events and plugins attached to them"""
    result = {}
    for eventName in self.listeners:
      result[eventName] = [(type(listener).__name__) for listener in self.listeners[eventName]] # Simply collects plugin class names
    return result

  def _emit(self, event_name, args=None):
    """Street magic to async call listener's class method by its string name"""
    if not self.isLocked: return False
    for listener in self.listeners[event_name]:
      if not event_name in listener.discordEventBusCallbacks: continue
      listenerMethodName = listener.discordEventBusCallbacks[event_name]
      try:
        if args:
          asyncio.create_task(getattr(listener, listenerMethodName)(*args))
        else:
          asyncio.create_task(getattr(listener, listenerMethodName)())
      except Exception:
        Util.printException()
    return True

  def _bindEvents(self):
    self.listeners = {} # TODO: Some better automation is required here. For now - don't forget to add what you bind!

    self.listeners['on_ready'] = []
    @self.client.event
    async def on_ready():
      self.isLocked = True
      self._emit('on_ready')

    self.listeners['on_disconnect'] = []
    @self.client.event
    async def on_disconnect():
      self.isLocked = False
      self._emit('on_disconnect')

    self.listeners['on_message'] = []
    @self.client.event
    async def on_message(*args):
      self._emit('on_message', args)

    self.listeners['on_raw_reaction'] = []
    self.listeners['on_raw_reaction_add'] = []
    @self.client.event
    async def on_raw_reaction_add(*args):
      self._emit('on_raw_reaction_add', args)
      self._emit('on_raw_reaction', args)

    self.listeners['on_raw_reaction_remove'] = []
    @self.client.event
    async def on_raw_reaction_remove(*args):
      self._emit('on_raw_reaction_remove', args)
      self._emit('on_raw_reaction', args)

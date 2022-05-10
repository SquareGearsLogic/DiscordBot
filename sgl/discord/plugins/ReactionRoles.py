import discord

from sgl.discord.APlugin import APlugin
from sgl.discord.Conf import Conf


class ReactionRoles(APlugin):
  client: discord.Client = None
  emojiRolesDict: dict = {}    #static
  emojiPriorityDict: dict = {} #static
  channelTopicDict: dict = {}  #static
  topic = None
  discordEventBusCallbacks = {'on_ready': '_onReady',
                              'on_message': '_onMessage',
                              'on_raw_reaction': '_onReaction'}

  def __init__(self, client: discord.Client):
    super().__init__(ReactionRoles)
    self.client = client

  @staticmethod
  def checkConfiguration():
    if 'ReactionRoles' in Conf.data and Conf.data['ReactionRoles']:
      return True

    topic = 'default topic (FIXME!)'
    Conf.data['ReactionRoles'] = Conf.data['ReactionRoles'] if 'ReactionRoles' in Conf.data else {}
    Conf.data['ReactionRoles'][topic] = {}
    Conf.data['ReactionRoles'][topic]['welcomeMsg'] = 'Please pick you roles in faction:\n🚜 - Miner\n🚛 - Courier'
    Conf.data['ReactionRoles'][topic]['welcomeMsgId'] = None
    Conf.data['ReactionRoles'][topic]['channelId'] = 1234567890
    Conf.data['ReactionRoles'][topic]['roles'] = {'🚜': 123456789,  # Miner role.
                                                  '🚛': 987654321,  # Courier role.
                                                  # discord.PartialEmoji(name='🚛'): 987654321,   # TODO: Support this
                                                  # discord.PartialEmoji(name='green', id=0): 0, # TODO: Support this
                                                  }
    return False

  @staticmethod
  def pluginDescription():
    return "ReactionRoles:\n" \
           "This plugin helps to manage member roles that they pick themselves by reacting to bot's welcome message with specific emoji mapped to a role.\n" \
           "The currently only UTF8 emojies supported for the 'role' parameter in config file.\n" \
           "Config file contains 'topic'(s), and it is recommended to lock each topic to a specific 'channelId'.\n" \
           "You will also need to describe this topic and roles in the 'welcomeMsg' that will be printed and pinned by bot once you type\n" \
           "'!rr_welcome topicname'\n" \
           "Once this is done, the 'welcomeMsgId' will be populated to config automatically.\n" \
           "NOTE: Admin's nickname can't be changed by bot!!!"

  def _resolveRoles(self):
    ReactionRoles.emojiRolesDict = {}
    for topic in Conf.data['ReactionRoles']:
      ReactionRoles.emojiRolesDict[topic] = self._normalizeEmoji(Conf.data['ReactionRoles'][topic]['roles'])

  def _normalizeEmoji(self, emojiRolesDict):
    # Turns emoji to discord.PartialEmoji(name='green', id=0)
    result: dict = {}
    for e in emojiRolesDict:
      emoji = e if type(e) == discord.PartialEmoji else discord.PartialEmoji(name=e)
      result[emoji] = emojiRolesDict[e]
    return result

  def _collectEmojiPriority(self):
    for topic in ReactionRoles.emojiRolesDict:
      ReactionRoles.emojiPriorityDict[topic] = []
      for emoji in ReactionRoles.emojiRolesDict[topic]:
        ReactionRoles.emojiPriorityDict[topic].append(emoji.name)

  def _collectCannelsAndTopics(self):
    ReactionRoles.channelTopicDict = {}
    for topic in Conf.data['ReactionRoles']:
      channelId = Conf.data['ReactionRoles'][topic]['channelId'] if Conf.data['ReactionRoles'][topic].get('channelId', None) else None
      ReactionRoles.channelTopicDict[channelId]: discord.TextChannel = topic

  async def _onReady(self):
    self._resolveRoles()
    self._collectEmojiPriority()
    self._collectCannelsAndTopics()
    self.logger.info('Connected.')

  async def _onMessage(self, message: discord.Message):
    if message.author == self.client.user: return
    topic = ReactionRoles.channelTopicDict.get(message.channel.id, None)
    if message.content.lower().startswith('!rr_welcome'):
      try:
        topic = message.content.replace('!rr_welcome', '', 1).strip()
        if topic in Conf.data['ReactionRoles']:
          await message.delete()
          await self._postWelconeMsg(topic, message.channel, message.author)
        else:
          await message.author.send("Wrong topic name")
      except Exception as e:
        self.printException("[{0}] Can't add role: {1}".format(self.topic, e))

  async def _postWelconeMsg(self, topic, channel: discord.TextChannel, author: discord.Member):
    welcomeMsgId = Conf.data['ReactionRoles'][topic].get('welcomeMsgId', None)
    welcomeMsg = Conf.data['ReactionRoles'][topic].get('welcomeMsg', None)
    if welcomeMsgId:
      msg: discord.Message = await channel.fetch_message(welcomeMsgId)
      await author.send("It already exists in this channel: {0}".format(msg.jump_url))
    else:
      msg = await channel.send(welcomeMsg)
      Conf.data['ReactionRoles'][topic]['channelId'] = channel.id
      Conf.data['ReactionRoles'][topic]['welcomeMsgId'] = msg.id
      self._collectCannelsAndTopics()
      Conf.saveConfigFile()
      await msg.pin()
      for emoji in ReactionRoles.emojiRolesDict[topic]:
        await msg.add_reaction(emoji)
      self.logger.info("[{0}] Welcome posted #{1} @ channel #{2}: {3}".format(self.topic, msg.id, channel.id, msg.jump_url))

  async def _onReaction(self, payload: discord.RawReactionActionEvent):
    if payload.member == self.client.user: return
    topic = ReactionRoles.channelTopicDict.get(payload.channel_id, None)
    if topic is None or payload.message_id != Conf.data['ReactionRoles'][topic]['welcomeMsgId'] \
       or payload.emoji not in ReactionRoles.emojiRolesDict[topic]:
      return
    guild = await self.client.fetch_guild(payload.guild_id)
    member = payload.member if payload.member else await guild.fetch_member(payload.user_id)
    name = member.nick if member.nick is not None else member.name
    roleId = ReactionRoles.emojiRolesDict[topic].get(payload.emoji, None)
    role = discord.Guild = guild.get_role(roleId) if roleId else None
    if role is None: return
    newName = name.replace(payload.emoji.name, '', 1)
    if payload.event_type == 'REACTION_ADD':
      newName = await self._insertEmoji(topic, payload.emoji.name, name.replace(payload.emoji.name, ''))
    await self._setUserRoleAndName(payload.event_type, member, role, newName)

  async def _insertEmoji(self, topic, emoji, name):
    newEmojiPriority = ReactionRoles.emojiPriorityDict[topic].index(emoji)
    namePosId = 0
    for c in name:
      if c not in ReactionRoles.emojiPriorityDict[topic]:
        break
      else:
        if ReactionRoles.emojiPriorityDict[topic].index(c) < newEmojiPriority:
          namePosId += 1
        else:
          break
    return name[:namePosId] + emoji + name[namePosId:]

  async def _setUserRoleAndName(self, event, member, role, newName):
    if (not event in ['REACTION_ADD', 'REACTION_REMOVE']):
      self.logger.error('[{0}] Unexpected reaction event {1}'.format(self.topic, event))
      return False

    if event == 'REACTION_ADD':
      self.logger.info("[{0}] Adding role '{1.name}' #{1.id} for '{2}' #{3.id}".format(self.topic, role, newName, member))
      try:
        await member.add_roles(role)
      except discord.HTTPException as e:
        self.printException("[{0}] Can't add role: {1}".format(self.topic, e))
        return False

    if event == 'REACTION_REMOVE':
      self.logger.info("[{0}] Removing role '{1.name}' #{1.id} for '{2}' #{3.id}".format(self.topic, role, newName, member))
      try:
        await member.remove_roles(role)
      except discord.HTTPException as e:
        self.printException("[{0}] Can't remove role: {1}".format(self.topic, e))
        return False

    try:
      await member.edit(nick=newName)  # or discord.Client.change_nickname(payload.member, 'new name')
    except discord.HTTPException as e:
      self.printException("[{0}] Can't edit nickname. Admin's nick can't be changed by Bot: {1}".format(self.topic, e))
      return False
    return True

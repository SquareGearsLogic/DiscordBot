import discord


class ReactionRoles():
  client: discord.Client = None

  discordEventBusEvents = {'on_ready': '_onReady',
                           'on_message': '_onMessage',
                           'on_raw_reaction': '_onReaction'}
  def __init__(self, client: discord.Client, topic, welcomeMsg, welcomeMsgId, channelId, emojiRolesDict):
    """clien          - instance of discord.Client\n
       topic          - topik of this Reaction Roles processor
       welcomeMsg     - welcome text that will be posted to explain purpose of all this stuff\n
       welcomeMsgId   - optional, If you already posted a welcome message and don't want a duplicate\n
       channelId      - optional. Lock functionality to a specific one\n
       emojiRolesDict - Dictionary of emoji and role ID that it is assigned to.
                        Emoji can be a character or discord.PartialEmoji object.
                        If characters present - run ReactionRoles.normalizeEmoji(emojiRolesDict) first.
                        Also, the position of icon represents where it's gonna be inserted in nickname among other emojies.

      NOTE: Admin's nickname can't be changed by bot!!!"""
    self.client = client
    self.topic = topic
    self.welcomeMsg = welcomeMsg
    self.welcomeMsgId = welcomeMsgId
    self.channelId = channelId
    self.emojiRolesDict = emojiRolesDict[topic]
    self._collectEmojiPriority(emojiRolesDict)

  def _collectEmojiPriority(self, emojiRolesDict):
    self.emojiPriority = []
    for topic in emojiRolesDict:
      for emoji in emojiRolesDict[topic]:
        self.emojiPriority.append(emoji.name)

  @staticmethod
  def normalizeEmoji(emojiRolesDict):
    result = {}
    for name in emojiRolesDict:
      result[name] = {}
      for e in emojiRolesDict[name]:
        emoji = e if type(e) == discord.PartialEmoji else discord.PartialEmoji(name=e)
        result[name][emoji] = emojiRolesDict[name][e]
    return result

  async def _onReady(self):
    self.channel: discord.TextChannel = (await self.client.fetch_channel(self.channelId)) if self.channelId else None
    print('RR[{0}] Connected.'.format(self.topic))

  async def _onMessage(self, message: discord.Message):
    if message.author == self.client.user : return
    if message.content.lower().startswith('!rr_welcome'):
      try:
        rrName = message.content.replace('!rr_welcome', '', 1).strip()
        if rrName == self.topic:
          await message.delete()
          await self._postWelconeMsg(message.channel, message.author)
      except Exception as e:
        print("RR[{0}] Can't add role: {1}".format(self.topic, e))

  async def _postWelconeMsg(self, channel: discord.TextChannel, author: discord.Member):
    if self.channel and self.channel != channel:
      await author.send("That's not the channel you looking for, try at <#{1}>.".format(self.channel.name, self.channel.id))
      return
    if self.welcomeMsgId:
      msg: discord.Message = await channel.fetch_message(self.welcomeMsgId)
      await author.send("It already exists in this channel: {0}".format(msg.jump_url))
    else:
      msg = await channel.send(self.welcomeMsg)
      self.welcomeMsgId = msg.id
      await msg.pin()
      for emoji in self.emojiRolesDict:
        await msg.add_reaction(emoji)
      print("RR[{0}] Welcome posted #{1} @ channel #{2}: {3}".format(self.topic, msg.id, channel.id, msg.jump_url))

  async def _onReaction(self, payload: discord.RawReactionActionEvent):
    if payload.member == self.client.user : return
    guild = await self.client.fetch_guild(payload.guild_id)
    member = payload.member if payload.member else await guild.fetch_member(payload.user_id)
    name = member.nick if member.nick is not None else member.name
    roleId = self.emojiRolesDict.get(payload.emoji, None)
    role = discord.Guild = guild.get_role(roleId) if roleId else None
    if role is None: return
    newName = name.replace(payload.emoji.name, '', 1)
    if payload.event_type == 'REACTION_ADD':
      newName = await self._insertEmoji(payload.emoji.name, name.replace(payload.emoji.name, ''))
    await self._setUserRoleAndName(payload.event_type, member, role, newName)

  async def _insertEmoji(self, emoji, name):
    newEmojiPriority = self.emojiPriority.index(emoji)
    namePosId = 0
    for c in name:
      if c not in self.emojiPriority:
        break
      else:
        if self.emojiPriority.index(c) < newEmojiPriority:
          namePosId += 1
        else:
          break
    return name[:namePosId] + emoji + name[namePosId:]

  async def _setUserRoleAndName(self, event, member, role, newName):
    if (not event in ['REACTION_ADD', 'REACTION_REMOVE']):
      print('RR[{0}] Unexpected reaction event {1}'.format(self.topic, event))
      return False

    if event == 'REACTION_ADD':
      print("RR[{0}] Adding role '{1.name}' #{1.id} for '{2}' #{3.id}".format(self.topic, role, newName, member))
      try:
        await member.add_roles(role)
      except discord.HTTPException as e:
        print("RR[{0}] Can't add role: {1}".format(self.topic, e))
        return False

    if event == 'REACTION_REMOVE':
      print("RR[{0}] Removing role '{1.name}' #{1.id} for '{2}' #{3.id}".format(self.topic, role, newName, member))
      try:
        await member.remove_roles(role)
      except discord.HTTPException as e:
        print("RR[{0}] Can't remove role: {1}".format(self.topic, e))
        return False

    try:
      await member.edit(nick=newName) # or discord.Client.change_nickname(payload.member, 'new name')
    except discord.HTTPException as e:
      print("RR[{0}] Can't edit nickname. Admin's nick can't be changed by Bot: {1}".format(self.topic, e))
      return False
    return True

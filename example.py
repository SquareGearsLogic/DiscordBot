import discord
from sgl.discord.plugins.ReactionRoles import ReactionRoles as RR
from sgl.discord.DiscordEventBus import DiscordEventBus as DEB

rrTopic = "faction activities"
rrWelcomeMsg = "Please pick you roles in faction:\n🚜 - Miner\n🚛 - Courier"
rrWelcomeMsgId = None # optional. leave None if not posted yet
rrChannelId = 1234567890  # optional. Locks to a specific channel
rrEmojiRoles = RR.normalizeEmoji({
                                  rrTopic: {'🚜':                            972313210550104094,   # Miner role.
                                            discord.PartialEmoji(name='🚛'): 972313456923537429,   # Courier role.
                                            #discord.PartialEmoji(name='green', id=0): 0,          # ID of the role associated with a partial emoji's ID.
                                            }
                                  })

client = discord.Client()
deb = DEB(client)
rr = RR(client, rrTopic, rrWelcomeMsg, rrWelcomeMsgId, rrChannelId, rrEmojiRoles)
deb.add(rr)

print("Running:\n{0}".format(deb.list()))
client.run('YOUR_BOT_TOKEN')
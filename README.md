# DiscordBot
Discord bot shell with single connection and multiple pluggable modules listening to events

## Setup
- Create 2 Discord accounts - one guild admin and one regular user, because bot can't perform some operations on admin
- Use admin account to create a new guild and invite regular user
- Login to https://discord.com/developers/applications with admin creds. Go to "Applications" left hand tab and click "New Application". This should switch to a new application view with new tabs on left hand side.
- Go to "Bot" left hand tab, click "Add Bot". This will create a Bot that is "Public" by default, that means eny Guild can invite your bot and your local bot server will process them all. If you want to process only your guild requests uncheck "Publick Bot"
- Go to "OAuth2" left hand tab, then "URL Generator", select "bot" checkbox and permissions section will showup. 
- Select permissions that you need, copy URL below and run on another tab. Login with your guild Admin account and complete setup.
- Now bot appears in you guild chat with a role of its own name.
- go back to "Bot" left hand tab and copy "Token" that is next to Bot avatar, or generate a new one if it's not on the screen.

## Python setup:
- download and install Python3
- clone and cd to repo, then create a python virtual evnironment ```virtualenv -p python3 venv``` then switch to it ```venv\Scripts\activate``` then install discord ```pip install discord.py```
- edit and run example.py.

## Discord bot shell
Discord provides a single connection to discord server, that we wrap into a DiscordEventBus class that represents "Listener Pattern". 
Basically all you need to do is to feed an instance of discord.Client to its constructor and then add pluging that will be notified upon discord event.
Plugins should have discordEventBusEvents dictionary field that maps discord.py events to local callbacks.

## Reaction Roles Plugin
Reaction roles plugin helps to manage user roles that they pick themselfe by reacting to bot's welcome message with specific emoji mapped to a role.

```python
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
```

Now go to that channel and message ```!rr_welcome faction activities```. 
Bot will remove your message, add a pinned welcome message with 2 reaction.
Use your regular user account and click those emojies under the message to get new roles and correcponding emojies in your nickname


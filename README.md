# DiscordBot
Discord bot based on "discord.py" with custom plugins listening/responding to events. Bot establishes a single connection to Discord server that is shared by multiple plugins.

## Discord Setup
- Create 2 Discord accounts - one guild admin and one regular user, because bot can't perform some operations on admin account.
- Use admin account to create a new guild and invite regular user.
- Login to https://discord.com/developers/applications with admin creds. Go to "Applications" left hand menu and click "New Application". This should switch to a new application view with new tabs on left hand side.
- Go to "Bot" left hand menu, click "Add Bot". This will create a Bot that is "Public" by default, that means eny Guild can invite your bot and your local bot server will process them all. If you want to process only your guild requests uncheck "Public Bot"
- Go to "OAuth2" left hand menu, then "URL Generator", select "bot" checkbox and permissions section will show up. 
- Select permissions that you need, copy URL below and run on another browser tab. Login with your guild Admin account and complete setup.
- Now bot appears in you guild chat with a role of its own name.
- go back to "Bot" left hand menu and copy "Token" that is next to Bot avatar, or generate a new one if it's not on the screen.

## Python setup:
- download and install Python3
- clone and cd to repo, then create a python virtual environment ```virtualenv -p python3 venv``` then switch to it ```venv\Scripts\activate``` then install discord ```pip install discord.py```
- edit and run example.py.

## Discord bot shell
Discord provides a single connection to discord server, that we wrap into a DiscordEventBus class that represents "Listener Pattern", where plugins subscribe using discordEventBusCallbacks mapping of discord event names to local callbacks. For the first run plugins will spawn config files and and prit description of how they work into console.
Simply edit the config file and restart the bot.

```python
import os
import discord
from sgl.discord.Conf import Conf
from sgl.discord.DiscordEventBus import DiscordEventBus
from sgl.discord import PluginLoader

Conf.loadConfigFile(os.path.realpath('./conf/settings.json'))
client = discord.Client()
deb = DiscordEventBus(client)
plugins = PluginLoader.loadAll(client, deb)
client.run('YOUR_BOT_TOKEN')
```

## Reaction Roles Plugin
Reaction roles plugin helps to manage user roles that they pick themselves by reacting to bot's welcome message with specific emoji mapped to a role.
Once you setup config, go to discord channel and message ```!rr_welcome yourtopicname```. 
Bot will remove your message, add a pinned welcome message with reaction emojis.
Use your regular user account and click those emojis under the message to get new roles and corresponding emojis in your nickname. The order of emojis in nickname will match your config, not the Discord role priority order.


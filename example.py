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
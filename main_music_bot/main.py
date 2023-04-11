import disnake
from disnake.ext import commands
from config import TOKEN, PREFIX

bot = commands.Bot(command_prefix=PREFIX, help_command=None, intents=disnake.Intents.all())
def start_bot():
    bot.load_extension("cogs.music_core")
    bot.load_extension("cogs.help_info")
    bot.loop.create_task(bot.run(TOKEN))
    
@bot.event
async def on_ready():
    print("bot is started!")

start_bot()


















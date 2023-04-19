import disnake
from disnake.ext import commands
import music_core
from music_core import *

class SongView(disnake.ui.view, commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
        
    @disnake.ui.button(label="Next!", style=disnake.ButtonStyle.green, custom_id="next_song_button")
    async def next_song(self, button: disnake.ui.Button, interaction: disnake.Interaction): 
        music_core.nextt(interaction)
        
    @disnake.ui.button(label="Stop!", style=disnake.ButtonStyle.blurple, custom_id="stop_song_button") 
    async def stop_song(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        music_core.stop_mus(interaction)
        
    @disnake.ui.button(label="Disconnect!", style=disnake.ButtonStyle.red, custom_id="disconnect_bot_button")
    async def turn_off(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        music_core.stop_bot(interaction)

def setup(bot: commands.Bot):
    bot.add_cog(music_core(bot))
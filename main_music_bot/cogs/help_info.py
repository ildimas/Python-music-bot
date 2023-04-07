import disnake
from disnake.ext import commands
class help_info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = """
```
General commands:
/help - displays all the available commands
/show <number> - show pages of songs by the given number
/show_random - show page with a random songs
/join - make bot join your room
/pages - show number of pages 
```
"""
    @commands.slash_command(name="help", description="Use this command if you have a problem using Rhytmi")
    async def execute(self, interaction: disnake.CommandInteraction):
        await interaction.send(self.help_message)
        
def setup(bot: commands.Bot):
    bot.add_cog(help_info(bot))
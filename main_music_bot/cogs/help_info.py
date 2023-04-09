import disnake
from disnake.ext import commands
class help_info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = """
```
General play commands:
/p-***** ### commands of this type connected with "play" functions
/p-play ### this command will make bot play a single song by INDEX
/p-play-random ### this command will make bot continious play random songs
/p-play-continious ### this command will make bot continious play a single song by INDEX
/p-play-queue ### this command will make bot start playing songs from your queue

General action commands:
/a-***** ### commands of this type connected with "action" functions 
/a-next ### this command will make bot switch to the next track 
/a-show ### this command will make bot show list of avaliable songs argument=INDEX
/a-show-random ### this command will make bot show a random avaliable songs
/a-start ### this command will make bot startup and join your chanel
/a-stop ### this command will make bot leave your chanel
/a-stop-music ### this command will make bot completly stop music
/a-gdrive-add ### this command will make bot add songs from your google drive to library argument=GOOGLE-DRIVE-URL

General queue commands:
/q-***** ### commands of this type connected with "queue" functions
/q-add ### this command will add song or songs to your gueue argument=INDEX or argument=INDEX1 INDEX2 INDEX3 (separated with space)
/q-queue ### this command will show you your current queue 
/q-remove ### this command will remove song or songs from you queue argument=INDEX or argument=INDEX1 INDEX2 INDEX3 (separated with space)

General playlist commands:
/l-***** ### commands of this type connected with "playlist" functions 
/l-playlist-create ### this command will create playlist based on your current queue argument=NAME-OF-PLAYLIST
/l-playlist-delete ### this command will delete playlist from bot argument=NAME-OF-PLAYLIST
/l-playlist-pick ### this command will get your playlist to the queue argument=NAME-OF-PLAYLIST 
/l-playlist-info ### this command  will show you all avaliable playlists 
```
"""
    @commands.slash_command(name="help", description="Use this command if you have a problem using Rhytmi")
    async def execute(self, interaction: disnake.CommandInteraction):
        await interaction.send(self.help_message)
        
def setup(bot: commands.Bot):
    bot.add_cog(help_info(bot))
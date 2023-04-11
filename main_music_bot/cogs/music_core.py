import disnake
import sqlite3
from disnake import Message, File
from disnake.ext import commands
import random
import os
import asyncio
import config
from disnake import Button, ButtonStyle, SelectMenu, SelectOption
from disnake import ui
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from utilities import *
from pydrive.auth import * 
import sys
import signal
import subprocess

class music_core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.db_list = []
        self.is_started = False
        self.is_canceled = False
        self.stop_continious_music = False
        self.q = []
        self.playlist = []
        self.users = []
        self.master = None
    
    @commands.slash_command(name="a-start", description="Use this command to start bot")
    async def start(self, interaction: disnake.CommandInteraction):
        await interaction.response.defer()
        refactor_sqlite_db(interaction.author.id)
        if self.master == None:
            self.master = interaction.author.id
        self.db_list = update_self_db(interaction.author.id)
        self.num_of_avaliable_pages = round(len(self.db_list) / 30)
        self.is_started = True
        self.is_canceled = False
        #! Voice_client init
        await interaction.send("Bot has succesfuly started!")
        try:    
            channel = interaction.author.voice.channel        
            self.voice_client = await channel.connect()
        except (AttributeError):
            await interaction.send(f"You are not in chanel")
            return  
        #!Buttons init
        self.next_button = ui.Button(style=ButtonStyle.green, label="Next song!")
        self.next_button.callback = self.next
        self.stop_button = ui.Button(style=ButtonStyle.green, label="Stop music")
        self.stop_button.callback = self.stop_mus
        self.leave_button = ui.Button(style=ButtonStyle.danger, label="Disconnect Bot")
        self.leave_button.callback = self.stop
        self.queue_button = ui.Button(style=ButtonStyle.blurple, label="Show a queue")
        self.queue_button.callback = self.queue
        #!Base views
        base_song_view = ui.View()
        base_song_view.add_item(self.next_button)
        base_song_view.add_item(self.stop_button)
        base_song_view.add_item(self.leave_button)
        self.song_view = base_song_view
        queue_view = ui.View()
        queue_view.add_item(self.next_button)
        queue_view.add_item(self.stop_button)
        queue_view.add_item(self.leave_button)
        queue_view.add_item(self.queue_button)
        self.queue_view = queue_view
        self.directory = "main_music_bot\music_storage" + "\\" + f"{interaction.author.id}" 
        
        if not os.path.exists(self.directory):
            await interaction.send("It seems that you are not autorized, I will create a folder for you, fill it with a comand /gdrive")
            os.makedirs(self.directory)
        else: await interaction.send(f"Welcome back {interaction.author}, You are my master today!")
            
    @commands.slash_command(name="a-next", description="Make bot stop music")
    async def next(self, interaction: disnake.CommandInteraction):
        await interaction.response.defer()
        if ((self.is_started) and (self.master == interaction.author.id)):
            if self.voice_client.is_playing():
                self.voice_client.stop()
                await interaction.send("Bot have succesfuly skipped a song!")
                return
            else:
                await interaction.send("Something went wrong!")
                return
        else: await interaction.send("You can't use this command")
                
    @commands.slash_command(name="a-show", description="Show list of avaliable songs")
    async def show(self, interaction: disnake.CommandInteraction, number):
        await interaction.response.defer()
        if (self.is_started):
            if int(number) in range(1, self.num_of_avaliable_pages + 1):
                db = self.db_list; fin_stroke = f"You are on the {number}/{self.num_of_avaliable_pages} page \n"
                for i in range((int(number) - 1) * 30, len(db)):
                    fin_stroke = fin_stroke + str((db[i])[0]) + "  " + str((db[i])[1]) + "\n" 
                    if len(fin_stroke) > 1900:
                        break    
                await interaction.send(fin_stroke)
            else: await interaction.send("Wrong number...")
        else: await interaction.send("You can't use this command use /start")  
        
    @commands.slash_command(name="a-restart-server", description="Use this command if you want to stop the music")   
    async def restart_bot(self, interaction: disnake.ApplicationCommandInteraction):
        await interaction.response.defer()
        if (interaction.author.id in config.ADMINISTRATORS):
            await interaction.send("Restarting bot...")
            try:
                await self.voice_client.disconnect()
            except:
                pass
            process = subprocess.Popen(["python", "main_music_bot\main.py"])
            
            pid = process.pid
            
            os.kill(pid, signal.SIGTERM)
            
            
            os.execv(sys.executable, ['python'] + ["main_music_bot\main.py"]) 
        else:
            await interaction.send("You can't use this command use /start") 
            
    @commands.slash_command(name="a-show-random", description="Show list of random avaliable songs")
    async def exectue(self, interaction: disnake.CommandInteraction):
        await interaction.response.defer()
        if (self.is_started):
            db = self.db_list
            fin_stroke = ""
            while True:
                y = random.randint(0, len(db)-1)
                fin_stroke = fin_stroke + str((db[y])[0]) + "  " + str((db[y])[1]) + "\n" 
                if len(fin_stroke) > 1800:
                    break    
            await interaction.response.send_message(fin_stroke) 
        else:
            await interaction.send("You can't use this command use /start") 
    
    @commands.slash_command(name="p-play", description="Play the single song, choose it using the index")
    async def play(self, interaction: disnake.CommandInteraction, index):
        await interaction.response.defer()
        if ((self.is_started) and (self.master == interaction.author.id)):
            try:
                audio_file_path = (self.db_list[int(index) - 1])[2]
                n_name = ((self.db_list[int(index) - 1])[1])
            except(IndexError):
                await interaction.send("Wrong index")
                return
            audio_sourse = disnake.FFmpegPCMAudio(audio_file_path)
            await interaction.send(f"Now playing: {n_name}")
            try:
                view = self.song_view
                await interaction.send(f"Now playing: {n_name}", view=view)
                self.voice_client.play(audio_sourse)
                while self.voice_client.is_playing():
                    if self.stop_continious_music == True:
                        self.voice_client.stop()
                        self.stop_continious_music = False
                        return
                    else:
                        await asyncio.sleep(1)
                self.voice_client.stop()
            except (BaseException):
                pass
        else:
            await interaction.send("You can't use this command")            
        
            
    @commands.slash_command(name="p-play-random", description="Bot will play random songs from your song list continiously")
    async def play_random(self, interaction: disnake.CommandInteraction):
        await interaction.response.defer()
        while True:
            if ((self.is_started) and (self.master == interaction.author.id)):
                index = random.randint(0, len(self.db_list) - 1)
                audio_file_path = (self.db_list[index])[2]
                audio_sourse = disnake.FFmpegPCMAudio(audio_file_path)
                self.voice_client.play(audio_sourse)
                n_name = ((self.db_list[index])[1])
                view = self.song_view
                await interaction.send(f"Now playing: {n_name}", view=view)
                try:
                    while self.voice_client.is_playing():
                        if self.stop_continious_music == True:
                            self.voice_client.stop()
                            self.stop_continious_music = False
                            return
                        else:
                            await asyncio.sleep(1)
                    self.voice_client.stop()
                except (AttributeError):
                    return
            else:
                await interaction.send("You can't use this command")  
                    
    @commands.slash_command(name="p-play-continious", description="Bot will play the song with the entered index on repeat")
    async def play_cont(self, interaction: disnake.CommandInteraction, index):
        await interaction.response.defer()
        if ((self.is_started) and (self.master == interaction.author.id)):
            try:
                n_name = ((self.db_list[int(index) - 1])[1])
                await interaction.send(f"Now playing continious: {n_name}")
                view = self.song_view
                await interaction.send(f"Now playing: {n_name}", view=view)
                while True:
                    audio_file_path = (self.db_list[int(index) - 1])[2]
                    audio_sourse = disnake.FFmpegPCMAudio(audio_file_path)
                    self.voice_client.play(audio_sourse)
                    try:
                        while self.voice_client.is_playing():
                            if self.stop_continious_music == True:
                                self.voice_client.stop()
                                self.stop_continious_music = False
                                return
                            else:
                                await asyncio.sleep(1)
                        self.voice_client.stop()
                    except (AttributeError):
                        return
            except(IndexError):
                await interaction.send("Wrong index")
                return
        else:
            await interaction.send("You can't use this command")
            
    @commands.slash_command(name="p-play-queue", description="With this command you can listen to your msic queue")
    async def execute(self, interaction: disnake.CommandInteraction):
        await interaction.response.defer()
        if ((self.is_started) and (self.master == interaction.author.id)):
            view = self.queue_view 
            while len(self.q) != 0:
                url, name = self.q[0][1], self.q[0][2]
                audio_sourse = disnake.FFmpegPCMAudio(url)
                await interaction.send(f"Now playing: {name}, songs remaining: {len(self.q) - 1}", view=view)
                try:
                    self.voice_client.play(audio_sourse)
                    while self.voice_client.is_playing():
                        if self.stop_continious_music == True:
                            self.voice_client.stop()
                            self.stop_continious_music = False
                            return
                        else:
                            await asyncio.sleep(1)
                    self.voice_client.stop()
                    self.q.remove(self.q[0])
                except (BaseException):
                    pass
            await interaction.send("Your queue is empty, add songs with a command /add-to-queue")
        else:
            await interaction.send("You can't use this command")     
            
    @commands.slash_command(name="a-stop", description="Use this command if you want to turn off bot")
    async def stop(self, interaction: disnake.CommandInteraction):
        await interaction.response.defer()
        if ((self.is_started) and (self.master == interaction.author.id)):
            await self.voice_client.disconnect()
            self.voice_client = None
            self.db_list = []
            self.is_started = False
            self.is_canceled = False
            self.stop_continious_music = False
            self.q = []
            self.playlist = []
            self.users = []
            self.master = None
            await interaction.send("Bot left")
        else:
            await interaction.send("You can't use this command")  
        
    @commands.slash_command(name="a-stop-music", description="Use this command if you want to stop the music")
    async def stop_mus(self, interaction: disnake.CommandInteraction):
        await interaction.response.defer()
        if ((self.is_started) and (self.master == interaction.author.id)):
            self.stop_continious_music = True
            await interaction.send("Music succesfully stopped!")
        else:
            await interaction.send("You can't use this command")             
            
    @commands.slash_command(name="q-add", description="Add songs to queue (Works only with /play-queue command)")
    async def add_to(self, interaction: disnake.CommandInteraction, index_or_indexes):
        await interaction.response.defer()
        if ((self.is_started) and (self.master == interaction.author.id)):
            try:
                ind_list = list(map(int, index_or_indexes.split(" ")))
                for index in ind_list:
                    db_index = (self.db_list[int(index) - 1])[0]  
                    audio_file_path = (self.db_list[int(index) - 1])[2]            
                    n_name = ((self.db_list[int(index) - 1])[1])
                    self.q.append([db_index, audio_file_path, n_name])
                await interaction.send("Queue updated")  
                return
            except(Exception):
                await interaction.send("Wrong index")
                return
        else:
            await interaction.send("You can't use this command")  
        
    @commands.slash_command(name="q-queue", description="Show a queue of songs")
    async def queue(self, interaction:disnake.CommandInteraction):
        await interaction.response.defer()
        if ((self.is_started) and (self.master == interaction.author.id)):
            fin_stroke = ""
            if len(self.q) == 0:
                await interaction.send("Your songs queue is empty")
                return
            for i in range(0, len(self.q)):
                fin_stroke = fin_stroke + str(self.q[i][0]) + " " + self.q[i][2] + "\n"
            await interaction.send("Your songs queue:" + "\n" + fin_stroke)
        else:
            await interaction.send("You can't use this command")   
            
    @commands.slash_command(name="q-remove", description="Remove song (or songs) from your queue")
    async def queue_remove(self, interaction:disnake.CommandInteraction, index_or_indexes):
        if ((self.is_started) and (self.master == interaction.author.id)):
            await interaction.response.defer()
            ind_list = list(map(int, index_or_indexes.split(" ")))
            new_q = []
            for row in self.q:
                if row[0] in ind_list:
                    continue
                else:
                    new_q.append(row)
                self.q = new_q
            await interaction.send("Selected indexes deleted")
        else:
            await interaction.send("You can't use this command")
            
    @commands.slash_command(name="l-playlist-pick", description="Pick one of your playlist to your queue")
    async def playlist_picker_main(self, interaction:disnake.CommandInteraction, name_for_your_playlist):
        if ((self.is_started) and (self.master == interaction.author.id)):
            await interaction.response.defer()
            try:
                self.q = playlist_picker(interaction.author.id, name_for_your_playlist)
                await interaction.send(f"Your playlst {name_for_your_playlist} have successfully picked! check your queue via /q-queue")
            except BaseException:
                await interaction.send("You have entered wrong name of playlist!")
        else:
            await interaction.send("You can't use this command")  
                
    @commands.slash_command(name="l-playlist-create", description="Create playlist based on your current queue")
    async def playlist_creator_main(self, interaction:disnake.CommandInteraction, name_for_your_playlist):
        if ((self.is_started) and (self.master == interaction.author.id)):
            await interaction.response.defer()
            
            playlist_creator(self.q, interaction.author.id, name_for_your_playlist)
            await interaction.send(f"Your playlist {name_for_your_playlist} have successfully created!")
            
        else:
            await interaction.send("You can't use this command")
            
    @commands.slash_command(name="l-playlists-info", description="Show all avaliable playlists")
    async def playlist_counter_main(self, interaction:disnake.CommandInteraction):
        if ((self.is_started) and (self.master == interaction.author.id)):
            await interaction.response.defer()
            
            try:
                num_of_avaliable_playlists, names_of_avaliable_playlists = playlist_counter(interaction.author.id)
                await interaction.send(f"You have {num_of_avaliable_playlists} active playlists\nNames of avaliable playlists: {', '.join(names_of_avaliable_playlists)}")
            except BaseException:
                await interaction.send("You have no playlists, create one using following command")
              
        else:
            await interaction.send("You can't use this command") 
              
    @commands.slash_command(name="l-playlist-delete", description="Delete one playlist")
    async def playlist_ereser_main(self, interaction:disnake.CommandInteraction, name_of_your_playlist):
        if ((self.is_started) and (self.master == interaction.author.id)):
            await interaction.response.defer()
            
            try:
                playlist_eraser(interaction.author.id, name_of_your_playlist)
                await interaction.send("Playlist was successfully deleted!")
            except BaseException:  
                await interaction.send("Playlist wasn't deleted, you entered a wrong name")      
        else:
            await interaction.send("You can't use this command")   
                
    @commands.slash_command(name="a-gdrive-add", description="Add your songs from Google drive. Pay attention !")
    async def gdrive(self, interaction:disnake.CommandInteraction, google_drive_url):
        if ((self.is_started) and (self.master == interaction.author.id)):
            await interaction.response.defer()
            
            gauth = GoogleAuth()
            scope = ['https://www.googleapis.com/auth/drive']
            gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name("main_music_bot\python-music-bot-382317-08c466190370.json", scope)
            drive = GoogleDrive(gauth)
            
            google_drive_id = str(google_drive_url).split("/")[-1]
            if google_drive_id.find("?") != -1:
                google_drive_id = str(google_drive_id)[0:str(google_drive_id).find("?")]           

            file_list = drive.ListFile({'q': f"'{google_drive_id}' in parents and trashed=false"}).GetList()
            url_l = []; name_l = []
            try:
                for file in file_list:
                    name_l.append(file['title'])
                    url_l.append(file['alternateLink'])
                url_l = list(map(id_extractor, url_l))
                download_urls = d_cheker(name_l, url_l, interaction.author.id)
                if download_urls == []:
                    await interaction.send("Everything is up to date")
                    return
                progress_bar = "[" + "░" * 50 + "]" + " " + f"{0}%"
                
                await interaction.edit_original_message(f"Download starting...\n I need to download {len(download_urls)} files, it will last around {len(download_urls) / 60} minutes \
                                      \nProgress bar:\n{progress_bar}" )
                 
                connection = sqlite3.connect("db.sqlite3")
                downloaded_files_counter = 0; step = (len(download_urls) // 50)
                if step == 0: step = (len(download_urls) / 50)
                for dl in download_urls:
                    file_id = f"{dl[1]}"
                    output_folder = self.directory
                    file = drive.CreateFile({'id': file_id})
                    file.GetContentFile(os.path.join(output_folder, file['title']))
                    connection.execute('INSERT INTO music (ID, Music_name, Music_url, Music_google_id, User_id) VALUES (?, ?, ?, ?, ?)',(0, dl[0][0:-4], f"{output_folder}/{file['title']}", dl[1], interaction.author.id))
                    connection.commit()
                    downloaded_files_counter += 1
                    progress_bar = "[" + "▓" * int(downloaded_files_counter // step) + "░" * int(50 - (downloaded_files_counter // step)) + "]" + " "+  f"{round((downloaded_files_counter / len(download_urls)) * 100)}%"
                    await interaction.edit_original_message(content=f"Download starting...\n I need to download {len(download_urls)} files, it will last around {len(download_urls) // 60} minutes \
                            \nProgress bar:\n{progress_bar}")
                    if downloaded_files_counter == len(download_urls):
                        await interaction.edit_original_message("Download finished!")
                       
                connection.close()
                refactor_sqlite_db(interaction.author.id)
                self.db_list = update_self_db(interaction.author.id)
                self.num_of_avaliable_pages = round(len(self.db_list) / 30)
                await interaction.edit_original_message("Download finished!")
            except Exception as e:
                await interaction.send(f"Something went wrong! {e}")
                return
        else:
            await interaction.send("You can't use this command")     
            
def setup(bot: commands.Bot):
    bot.add_cog(music_core(bot))
    
import sqlite3
import disnake
from disnake import ui
def id_extractor(url):
    url = url.split("/")[-2]
    return url
def d_cheker(name_l, url_l, user_id):
    download_list = []
    connection = sqlite3.connect("db.sqlite3")
    cursor = connection.cursor()
    rows = cursor.execute("SELECT * FROM music WHERE User_id = ?", (user_id,))
    db_id = []; db_user_id = []
    for row in rows:
        db_id.append(row[3])
        db_user_id.append(row[4]) #! Баг здесь в db_user_id пофиксить его следует тем что для каждого клиенте делать его отдельный тейбл
    cursor.close()
    connection.close()
    for i in range(len(url_l)):
        if (url_l[i] in db_id):
            continue
        else:
            download_list.append([name_l[i], url_l[i]])
    return download_list

def update_self_db(user_id):
    res_l = []
    connection = sqlite3.connect("db.sqlite3")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM music WHERE User_id = ?", (user_id,))
    rows = cursor.fetchall()
    for row in rows:
        res_l.append(row)
    cursor.close()        
    connection.close()
    return res_l

def refactor_sqlite_db(user_id):
    connection = sqlite3.connect("db.sqlite3")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM music WHERE User_id = ?", (user_id,))
    counter = 0
    res_l = []
    for row in cursor.fetchall():
        counter +=1
        row = list(row)
        row[0] = counter
        res_l.append(row)
    cursor.execute("DELETE FROM music WHERE User_id = ?", (user_id,))
    connection.commit()
    for row in res_l:
        cursor.execute("INSERT INTO music (ID, Music_name, Music_url, Music_google_id, User_id) VALUES (?, ?, ?, ?, ?)", row)
        connection.commit()
    cursor.close()
    connection.close()
    return res_l
def playlist_creator(q, master, name_of_playlist):
    connection = sqlite3.connect("playlist_db.sqlite3")
    cursor = connection.cursor()
    for row in q:
        cursor.execute("INSERT INTO playlists (ID, Music_name, Music_url, User_id, Playlist_name) VALUES (?, ?, ?, ?, ?)", (row[0], row[1], row[2], master, name_of_playlist))
        connection.commit()
    cursor.close()
    connection.close()    
def playlist_picker(master, name_of_playlist):
    playlist_list = []
    connection = sqlite3.connect("playlist_db.sqlite3")  
    cursor = connection.cursor()
    rows = cursor.execute("SELECT * FROM playlists WHERE User_id = ? AND Playlist_name = ?", (master, name_of_playlist))
    for row in rows:
        playlist_list.append(list(row))
    cursor.close()
    connection.close() 
    if playlist_list == []:
        raise BaseException
    return playlist_list

def playlist_counter(master):
    ll = []
    connection = sqlite3.connect("playlist_db.sqlite3")  
    cursor = connection.cursor()
    rows = cursor.execute("SELECT * FROM playlists WHERE User_id = ?", (master,))
    for row in rows:
        ll.append(list(row)[4])
    cursor.close()
    connection.close()
    if (len(set(ll)) == 0) or (list(set(ll)) == 0):
        raise BaseException
    return len(set(ll)), list(set(ll))

def playlist_eraser(master, name_of_playlist):
    connection = sqlite3.connect("playlist_db.sqlite3")  
    cursor = connection.cursor()
    db_before = cursor.execute("SELECT * FROM playlists WHERE User_id = ?", (master,))
    cursor.execute("DELETE FROM playlists WHERE Playlist_name = ? AND User_id = ?", (name_of_playlist, master))
    connection.commit()
    db_after = cursor.execute("SELECT * FROM playlists WHERE User_id = ?", (master,))
    cursor.close()
    connection.close() 
    if len(db_after) == len(db_before):
        raise BaseException
    
if __name__ == "__main__":
    pass
        
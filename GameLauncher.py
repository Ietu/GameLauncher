import tkinter as tk
import requests
import win32api
import winreg
import os
import platform
from io import BytesIO
from PIL import ImageShow, Image, ImageTk
from tkscrolledframe import ScrolledFrame
from tkinter.ttk import OptionMenu
from tkinter import *
from tkinter import ttk, messagebox, filedialog

#Steam API key
api_key = ''

#SteamID64
steamid = ''

current_gameid = ''

url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steamid}&format=json&include_appinfo=true'

#TODO get images for each game and display image inside launch button
#url_hero = f'https://cdn.cloudflare.steamstatic.com/steam/apps/{current_gameid}/library_hero.jpg'

root = tk.Tk()
root.title("Steam Game Launcher")
root.minsize(791, 600)
root.maxsize(791, 600)
root.configure(background="black")

response = requests.get(url)
data = response.json()

#TODO: Add other gamelaunchers games

#extract the appid of each game
appids = [game['appid'] for game in data['response']['games']]
all_gamenames = [game['name'] for game in data['response']['games']] #GAME PICKER WINDOW 

main_window_games = []

gamenames = []
gamenames_main = []

added_gameid = []
added_gamenames = []

def load_games_from_file():
    main_window_games.clear()
    print("LOADING GAMES FROM FILE")
    with open(r'C:/temp/games.txt', 'r') as fp:
        lines = fp.readlines()
        for i, line in enumerate(lines):
            if i == len(lines) - 1:
                x = line
            else:
                x = line[:-1]
            main_window_games.append(x)
    print("MAIN WINDOW GAMES NOW TEST TEST: ", main_window_games)

load_games_from_file()

def add_games_to_main():
    gamenames.extend([item for item in all_gamenames if item not in main_window_games])

add_games_to_main()

gamenames_main = gamenames


#Saving games locally TODO: automate using steam api
def write_games_to_file(games_list):
    print("PRINTING INTO FILE")
    with open(r'C:/temp/games.txt', 'w') as fp:
        fp.writelines('\n'.join(games_list))

print("PRINTING main_window_games: ", main_window_games)
print("PRINTING gamenames: ", gamenames)
print("PRINTING added_gameid: ", added_gameid)
print("PRINTING added_gamenames: ", added_gamenames)

def reset_games():
    print("GAMENAMES BEFORE: ", added_gamenames)
    added_gamenames.clear()
    print("GAMENAMES AFTER: ", added_gamenames)


class ScrollFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.canvas = tk.Canvas(self, borderwidth=0, background="#555555", height=600, width=788) 
        self.viewPort = tk.Frame(self.canvas, background="#555555")                 
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview) 
        self.canvas.configure(yscrollcommand=self.vsb.set)                        

        self.vsb.pack(side="right", fill="y")                                   
        self.canvas.pack(side="left", fill="both", expand=True)                   
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw",            
                                  tags="self.viewPort")

        self.viewPort.bind("<Configure>", self.onFrameConfigure)                 
        self.canvas.bind("<Configure>", self.onCanvasConfigure)                   
            
        self.viewPort.bind('<Enter>', self.onEnter)                            
        self.viewPort.bind('<Leave>', self.onLeave)                                

        self.onFrameConfigure(None)                                            

    def onFrameConfigure(self, event):                                              
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))               

    def onCanvasConfigure(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)         

    def onMouseWheel(self, event):                                             
        if platform.system() == 'Windows':
            self.canvas.yview_scroll(int(-1* (event.delta/120)), "units")
        elif platform.system() == 'Darwin':
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll( -1, "units" )
            elif event.num == 5:
                self.canvas.yview_scroll( 1, "units" )
    
    def onEnter(self, event):                                                    
        if platform.system() == 'Linux':
            self.canvas.bind_all("<Button-4>", self.onMouseWheel)
            self.canvas.bind_all("<Button-5>", self.onMouseWheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):                                          
        if platform.system() == 'Linux':
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")

def get_steam_path():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\Valve\Steam")
        return winreg.QueryValueEx(key, "SteamPath")[0]
    except:
        return None

steam_path = get_steam_path()
if steam_path:
    print(f'Main Steam is installed at: {steam_path}')
else:
    print('Steam is not installed')

def center_window(w_width, w_height, window_name):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x_coordinate = (screen_width/2) - (w_width/2)
    y_coordinate = (screen_height/2) - (w_height/2)

    window_name.geometry("{}x{}+{}+{}".format(w_width, w_height, int(x_coordinate), int(y_coordinate)))

def format_steam_folders(steam_folders):
    steam_folders = [folder.replace('\\steamapps', '') for folder in steam_folders]
    steam_folders = '\n - '.join(steam_folders)
    return f'\n - {steam_folders}'

def get_all_drives():
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    return drives


def search_steam_folders():
    drives = get_all_drives()
    steam_folders = []
    for drive in drives:
        path = os.path.join(drive, 'Steam\steamapps')
        if os.path.isdir(path):
            steam_folders.append(path)
    return steam_folders

def on_find_steam_folders_click():
    steam_folders = search_steam_folders()
    steam_folders_formatted = format_steam_folders(steam_folders)
    if steam_folders:
        message = f'Steam game folders found on: {steam_folders_formatted}\nDo you want to manually add another Steam location?'
        result = messagebox.askyesno(title='Steam Folders Found', message=message)
        if result:
            manual_add_steam_location()
    else:
        messagebox.showinfo('Steam Folders Not Found', 'No Steam game folders found')

def selected_game_color():
    print("CHANGING COLOR")

def manual_add_steam_location():
    print("TRYING TO ADD DRIVE1")
    global steam_folders
    print("TRYING TO ADD DRIVE2")
    folder_path = filedialog.askdirectory(title = "Select Steam Folder")
    print("TRYING TO ADD DRIVE3")
    if os.path.isdir(os.path.join(folder_path,'steamapps')):
        steam_folders.append(folder_path)
        messagebox.showinfo("Steam Folder added", f'{folder_path} added as Steam Folder')
    else:
        messagebox.showerror("Invalid Steam folder!", "The selected folder is not a valid Steam folder.")

steam_folders = search_steam_folders()
steam_folders_formatted = format_steam_folders(steam_folders)
if steam_folders:
    print(f'Steam game folders found on: {steam_folders_formatted}')
else:
    print('Steam game folders not found')


def search():
    print("Searching for:")


def show_about_info():
    messagebox.showinfo(
        title="About",
        message="Hello!"
    )

def quit_app():
    root.destroy()

def name_into_id(game_name):
    index = all_gamenames.index(game_name)
    print("INDEX: ", index)
    game_id = appids[index]
    return game_id


def add_games(game_name):
    print("CURRENT GAME: ", game_name)
    handle_added_games(game_name)
    print("ADDED GAMES TOTAL: ", added_gamenames)

def handle_added_games(game_name):
    print("ADDED GAME: ", game_name)
    if game_name in added_gamenames:
        print("REMOVED | {} | FROM SELECTED".format(game_name))
        added_gamenames.remove(game_name)
    else:
        print("ADDED | {} | TO SELECTED".format(game_name))
        added_gamenames.append(game_name)

def toggle_bg_color(button):
    current_color = button.cget("background")
    if current_color == "#333333":
        button.configure(background="green")
    else:
        button.configure(background="#333333")

def get_games():
    new_window = tk.Toplevel(root)
    new_window.iconphoto(False, photo)
    new_window.config(background="#555555")
    menubar = tk.Menu(root)

    file_menu = tk.Menu(menubar)
    help_menu = tk.Menu(menubar)

    menubar.add_cascade(menu=file_menu, label="Settings")
    menubar.add_cascade(menu=help_menu, label="Help")

    file_menu.add_command(label="Games", command=get_games)
    file_menu.add_command(label="Drives", command=add_drive)

    file_menu.add_command(label="Exit", command=quit_app)

    help_menu.add_command(label="About", command=show_about_info)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = 791
    window_height = 750

    x_coordinate = (screen_width/2) - (window_width/2)
    y_coordinate = (screen_height/2) - (window_height/2)

    new_window.geometry("{}x{}+{}+{}".format(window_width, window_height, int(x_coordinate), int(y_coordinate)))

    new_window.title("Add Games")
    default_bg = "#333333"

    class Example(tk.Frame):
        def __init__(self, root):
            tk.Frame.__init__(self, root)
            self.scrollFrame = ScrollFrame(self)
            self.scrollFrame.config(borderwidth="1", relief="solid")
            for i, game in enumerate(gamenames):
                button = tk.Button(self.scrollFrame.viewPort, text=game, fg="white", bg=default_bg, command=lambda game=game: add_games(game), width=34, height=7, borderwidth="1", relief="solid")
                button.grid(row=i // 3, column=i % 3, padx=8, pady=8)
            self.scrollFrame.pack(side="top", fill="both", expand=True)
        def printMsg(self, msg):
            print(msg)
        

    add_games_button = tk.Button(new_window, text="Add Games", height= 2, width=12, command=lambda : add_into_main(main_window_games))
    add_games_button.place(relx=.07, rely=0.96, anchor="center")

    exit_button = tk.Button(new_window, text="Exit", height= 2, width=12, command=lambda : new_window.destroy())
    exit_button.place(relx=.2, rely=0.96, anchor="center")
    new_window.resizable(False,False)
    Example(new_window).grid(row=0, column=0, sticky="nsew")



def add_drive():
    new_window = tk.Toplevel(root)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = 250
    window_height = 200

    x_coordinate = (screen_width/2) - (window_width/2)
    y_coordinate = (screen_height/2) - (window_height/2)

    new_window.geometry("{}x{}+{}+{}".format(window_width, window_height, int(x_coordinate), int(y_coordinate)))

    new_window.title("Drives")
    new_window.minsize(250, 200)
    new_window.resizable(False,False)

    get_drives_button = tk.Button(new_window, text="Get Steam Folders", height= 1, width=14, command=on_find_steam_folders_click)
    get_drives_button.place(x=20, y=160)

    exit_button = tk.Button(new_window, text="Exit", height= 1, width=8, command=new_window.destroy)
    exit_button.place(x=140, y=160)
    
    drives_list = search_steam_folders()
    drives_text = format_steam_folders(drives_list)
    print(drives_text)

    label_text = tk.Label(new_window, text="Current drives read:", font=(15))
    label_text.place(relx=.4, rely=.1, anchor="center")

    label_drives = tk.Label(new_window, text=drives_text, font=(8))
    label_drives.place(relx=.4, rely=.4, anchor="center")


def remove_games(game_name):
    print("REMOVING GAME: ", game_name)

def launch_game(game_name):
    print("LAUNCHING GAME: ", game_name)
    game_id = str(name_into_id(game_name))
    print("GAME_ID: ", game_id)
    print("GAME ID FROM LAUNCH: ", game_id)
    print("ALL GAMES CURRENTLY: ", main_window_games)
    os.startfile("steam://rungameid/" + game_id)

class Example(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.scrollFrame = ScrollFrame(self)
        for i, game in enumerate(main_window_games):
            button = tk.Button(self.scrollFrame.viewPort, text=game, fg="white", bg='#333333', command=lambda game=game: launch_game(game), width=34, height=7, borderwidth="1", relief="solid")
            button.grid(row=i // 3, column=i % 3, padx=8, pady=8)
        self.scrollFrame.pack(side="top", fill="both", expand=True)
    
    def printMsg(self, msg):
        print(msg)

def add_into_main(main_window_games):
    print("ADDED GAMES TO MAIN WINDOW")
    set_to_add = set(added_gamenames)
    originial_set = set(main_window_games)

    originial_set.update(set_to_add)
    main_window_games = list(originial_set)
    print("GAMES ON MAIN WINDOW: ", main_window_games)
    write_games_to_file(main_window_games)
    
    
root.option_add("*tearOff", False)

main = ttk.Frame(root)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

window_width = 791
window_height = 600

x_coordinate = (screen_width/2) - (window_width/2)
y_coordinate = (screen_height/2) - (window_height/2)

root.geometry("{}x{}+{}+{}".format(window_width, window_height, int(x_coordinate), int(y_coordinate)))

menubar = tk.Menu()
root.config(menu=menubar)

file_menu = tk.Menu(menubar)
help_menu = tk.Menu(menubar)

menubar.add_cascade(menu=file_menu, label="Settings", font=(22))                               
menubar.add_cascade(menu=help_menu, label="Help")

file_menu.add_command(label="Games", command=get_games)
file_menu.add_command(label="Drives", command=add_drive)
file_menu.add_command(label="Refresh", command=lambda : refresh())
file_menu.add_command(label="Exit", command=quit_app)

help_menu.add_command(label="About", command=show_about_info)

notebook = ttk.Notebook(main)
notebook.pack(fill="both", expand=True)


root.iconphoto(False, photo)

if __name__ == "__main__":
    def refresh():
        print("TRYING TO REFRESH")
        root.mainloop()
        load_games_from_file()

    Example(root).grid(row=0, column=0, sticky="nsew")
    root.mainloop()
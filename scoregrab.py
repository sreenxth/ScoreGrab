import tkinter
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime,timedelta
import json
import time
import requests
import tzlocal
import pytz

#GETTING DATE RANGE FOR QUERY
datetodayt = time.strftime("%Y-%m-%d")
datetoday = datetime.strptime(datetodayt, "%Y-%m-%d")
preday=(datetoday - timedelta(days=1)).strftime("%Y-%m-%d")
daterange=[preday,datetoday]


#UTC TO SYSTEM'S TIME
def timeconversion(utctime):
    local_timezone = tzlocal.get_localzone()
    try:
        if datetime.strptime(utctime, "%Y-%m-%dT%H:%M:%SZ") is not ValueError():
            utc_time = datetime.strptime(utctime, "%Y-%m-%dT%H:%M:%SZ")
            new_time = pytz.utc.localize(utc_time).astimezone(local_timezone)
            new_time_str = new_time.strftime("%d %b\n%H:%M\n%Z")
            return new_time_str
    except ValueError:
        utc_time = datetime.strptime(utctime, "%Y-%m-%dT%H:%M:%S.%fZ")
        new_time = pytz.utc.localize(utc_time).astimezone(local_timezone)
        new_time_str = new_time.strftime("%d %b")
        return new_time_str

#DATA RETRIEVAL BEGINS HERE


#MATCH DETAILS SCREEN
def matchdetails(matchid):
    req_game=requests.get(f"https://www.balldontlie.io/api/v1/games/{matchid}")
    req_playersonpaint=requests.get(f"https://balldontlie.io/api/v1/stats?game_ids[]={matchid}&per_page=30")
    with open("matchdetails.json","w") as f:
            json.dump(req_game.json(),f,indent=2)
    with open("matchplayers.json","w") as f:
        json.dump(req_playersonpaint.json(),f,indent=2)
#DISPLAY PLAYER NAMES AND POSITIONS



#TODAY SCREEN
def refreshhome():
    for widgets in scrollframe.winfo_children():
          widgets.destroy()
    homescreentoday()
    
def scroll_y(*args):
    canvas.yview(*args)
    

def homescreentoday():
        #loading data ffrom api
        req_gamestoday=requests.get(f"https://www.balldontlie.io/api/v1/games?start_date={daterange[0]}&end_date={daterange[1]}") #actual function line
        #req_gamestoday=requests.get(f"https://www.balldontlie.io/api/v1/games?start_date=2023-05-25&end_date=2023-10-25") #testing line
        games=req_gamestoday.json()

        #screen when no games are played
        if games["data"]==[]:
            #displaying current time
            now=time.localtime()
            strnow = time.strftime("%b %d, %Y  %H:%M:%S",now)
            timeupdate=tkinter.Label(window, text=f"Last Updated on:\n{strnow}",font=("Kanit Thin", "14"),bg="black",fg="#949494")
            
            #notice
            no_matches=tkinter.Label(window, text="No NBA Games are being\nplayed at the moment :/",font=("Kanit Thin", "28"),bg="black",fg="#ffffff")
            
            #update
            update=tkinter.Label(window,text="The 23-24 NBA season begins on Oct 25, 2023. See you then!",bg="black",fg="#949494",font=("Kanit Thin", "12"))
            
            toptitle.grid(row=0)
            
            #placing widgets
            no_matches.place(relx=0.5, rely=0.5, anchor='center')
            update.place(relx=0.5,rely=0.58,anchor='center')
            timeupdate.place(relx=0.5, anchor='center',rely=0.15)
            
            #balldontlie credits
            credits=tkinter.Label(window,text="Data provided by balldontlie.io API.",bg="black",fg="#3d3d3d",font=("Kanit Thin", "12"))
            credits.place(relx=0.5,rely=0.987,anchor="center")
            
            #refresh
            refreshbutton=tkinter.Label(window, image=ref, bg="black")
            refreshbutton.place(anchor="center",relx=0.495,rely=0.8)
            refreshbutton.bind("<Button-1>", lambda event: refreshhome())
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        #screen when games are in the vicinity
        else:
            #balldontlie credits
            credits=tkinter.Label(window,text="Data provided by balldontlie.io API.",bg="black",fg="#3d3d3d",font=("Kanit Thin", "12"))
            credits.place(relx=0.5,rely=0.987,anchor="center")
            
            #writing and retrieving games
            with open("gamestoday.json","w") as f:
                json.dump(games,f,indent=2)
            with open("gamestoday.json") as f:
                games_today=json.load(f)
                
            #segregation
            completed_games=[]
            ongoing_games=[]
            upcoming_games=[]
            
            for game in games_today["data"]:
                if game["period"]==4:
                    completed_games.insert(0,game)
                elif game["period"]==0:
                    upcoming_games.append(game)
                else:
                    ongoing_games.append(game)
            completed_games.sort(key=lambda x: x['date'])
            
            #fixtures and results heading
            fixres=tkinter.Label(scrollframe, text=f"  Fixtures & Results", font=("Kanit Thin", "18"),bg="#303030",fg="#ebebeb", height="1",width="39",anchor="w",padx=10)
            toptitle.grid(row=0,columnspan=3,sticky="w")
            fixres.grid(row=1,columnspan=3,sticky="ew")
            i=0
            
            #placing completed games
            if completed_games!=[]:
                for game in completed_games:
                    #reqd data
                    matchid=game['id']
                    home=game['home_team']['name']
                    away=game['visitor_team']['name']
                    homescore=game['home_team_score']
                    awayscore=game['visitor_team_score']
                    status=game['status'].upper()
                    dateextract=game['date']
                    date=timeconversion(dateextract)
                    
                    #team lead indicator
                    if homescore > awayscore:
                        homescore="  "+str(homescore)+" ◂"
                        awayscore="  "+str(awayscore)+"  "
                    elif awayscore>homescore:
                        awayscore="  "+str(awayscore)+" ◂"
                        homescore="  "+str(homescore)+"  "
                    
                    #status
                    statuslabel = tkinter.Label(scrollframe, text=f"{status}\n{date}", width=8, fg="white", bg="#171717", font=("Kanit Thin", 12), height=3)
                    statuslabel.grid(row=i+2, column=0, sticky="w")
                    
                    #teams disp
                    teams = tkinter.Label(scrollframe, text=f"       {home}\n       {away}", fg="white", bg="black", font=("Kanit Thin", 18), width=28, anchor="w", justify="left")
                    teams.grid(row=i+2, column=1, sticky="w")
                    
                    #livescore
                    scores = tkinter.Label(scrollframe, text=f"{homescore}\n{awayscore}", width=5, fg="white", bg="#171717", font=("Kanit Thin", 18),height=2,anchor="w", justify="left")
                    
                    scores.grid(row=i+2, column=2, sticky="e")
                    scores.bind("<Button-1>", lambda event, matchid=matchid: matchdetails(matchid))
                    i=i+2
                    
            #placing ongoing games
            if ongoing_games!=[]:
                for game in ongoing_games:
                    #retrieving reqd data
                    matchid=game['id']
                    home=game['home_team']['name']
                    away=game['visitor_team']['name']
                    homescore=game['home_team_score']
                    awayscore=game['visitor_team_score']
                    status=game['status']
                    timeinperiod=game['time']
                    
                    #team lead indicator
                    if homescore > awayscore:
                        homescore="  "+str(homescore)+" ◂"
                        awayscore="  "+str(awayscore)+"  "
                    elif awayscore>homescore:
                        awayscore="  "+str(awayscore)+" ◂"
                        homescore="  "+str(homescore)+"  "
                    
                    #status of game
                    statuslabel = tkinter.Label(scrollframe, textvariable=f"{status}\n{timeinperiod}", width=8, fg="white", bg="#171717", font=("Kanit Thin", 12), height=3)
                    statuslabel.grid(row=i+2, column=0, sticky="w")
                    
                    #teams disp
                    teams = tkinter.Label(scrollframe, text=f"       {home}\n       {away}", fg="white", bg="black", font=("Kanit Thin", 18), width=28, anchor="w", justify="left")
                    teams.grid(row=i+2, column=1, sticky="w")
                    
                    #livescore
                    scores = tkinter.Label(scrollframe, textvariable=f"{homescore}\n{awayscore}", width=5, fg="white", bg="#171717", font=("Kanit Thin", 18),height=2,anchor="w", justify="left")
                    scores.grid(row=i+2, column=2, sticky="e")
                    i=i+2
                    
            #placing upcoming games
            if upcoming_games!=[]:
                for game in upcoming_games:
                    #retrieving reqd data
                    matchid=game['id']
                    home=game['home_team']['name']
                    away=game['visitor_team']['name']
                    homescore="-"
                    awayscore="-"
                    statusextract=game['status']
                    status=timeconversion(statusextract)
                    
                    #status of game
                    statuslabel = tkinter.Label(scrollframe, text=f"{status}", width=8, fg="white", bg="#171717", font=("Kanit Thin", 12), height=3)
                    statuslabel.grid(row=i+2, column=0, sticky="w")
                    
                    #teams disp
                    teams = tkinter.Label(scrollframe, text=f"       {home}\n       {away}", fg="white", bg="black", font=("Kanit Thin", 18), width=28, anchor="w", justify="left")
                    teams.grid(row=i+2, column=1, sticky="w")
                    
                    #livescore
                    scores = tkinter.Label(scrollframe, text=f"{homescore}\n{awayscore}", width=5, fg="white", bg="#171717", font=("Kanit Thin", 18),height=2)
                    scores.grid(row=i+2, column=2, sticky="e")
                    i=i+2
            
            #update time disp
            now=time.localtime()
            strnow = time.strftime("   %b %d, %Y  %H:%M:%S",now)
            timeupdate=tkinter.Label(scrollframe, text=f"   Last Updated on:\n{strnow}",font=("Kanit Thin", "14"),bg="#303030",fg="white",anchor='center',width=50,padx=16)
            timeupdate.grid(row=i+2,columnspan=3,sticky="w")
            
            #refresh button
            refreshbutton=tkinter.Label(scrollframe,image=ref, bg="black",height=70)
            refreshbutton.grid(row=i+2+2,columnspan=3,sticky="wnes")
            refreshbutton.bind("<Button-1>", lambda event: refreshhome())
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            


#HOME SCREEN
window=tkinter.Tk()
window.title("ScoreGrab")
window.geometry("555x850")
window.configure(bg="black")
window.resizable(False, False)

#app icon image
icon=Image.open("images/icon.png")
icon=icon.convert('RGBA')
icondisp=ImageTk.PhotoImage(icon)
window.iconphoto(True,icondisp)

#statgrab iamge
timage = Image.open("images/homeheader.jpg")
nimage=timage.resize((555,81),resample=Image.LANCZOS)
image=ImageTk.PhotoImage(nimage)
toptitle = tkinter.Label(window,image=image,highlightthickness=0,borderwidth=0,width=555)

#scroll implemnetation
canvas = tkinter.Canvas(window, bg="black", highlightthickness=0)
canvas.place(x=0, y=71, width=537, height=750)

scrollbar = tkinter.Scrollbar(window, orient="vertical", command=scroll_y)
scrollbar.place(x=537, y=71, height=750)

canvas.configure(yscrollcommand=scrollbar.set)
scrollframe = tkinter.Frame(canvas, bg="black")
canvas.create_window((0, 0), window=scrollframe, anchor="nw")

#refresh icon image
tref = Image.open("images/refresh.png")
nref=tref.resize((50,50),resample=Image.LANCZOS)
ref=ImageTk.PhotoImage(nref)

#home screen called
homescreentoday()

window.mainloop()

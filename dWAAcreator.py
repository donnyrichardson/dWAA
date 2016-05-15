import csv
import datetime as dt
import os
import string
import eventlist as el
import statistics as stat
import time

pnset = [['',0]]

class league(object):
    def __init__(self, pdb):
        self.pdb = pdb
        self.idists = []
        self.odists = []
        self.iangs = []
        self.oangs = []
        self.ispeeds = []
        self.ospeeds = []
        for lplay in pdb:
            if not lplay.pball.dist == 'null':
                if lplay.outfield:
                    self.odists.append(lplay.pball.dist)
                else:
                    self.idists.append(lplay.pball.dist)
            if not lplay.pball.angle == 'null':
                if lplay.outfield:
                    self.oangs.append(lplay.pball.angle)
                else:
                    self.iangs.append(lplay.pball.angle)
            if not lplay.pball.speed == 'null':
                if lplay.outfield:
                    self.ospeeds.append(lplay.pball.speed)
                else:
                    self.ispeeds.append(lplay.pball.speed)
        self.odistsd = stat.pstdev(self.odists)
        self.oangsd = stat.pstdev(self.oangs)
        self.ospeedsd = stat.pstdev(self.ospeeds)
        self.idistsd = stat.pstdev(self.idists)
        self.iangsd = stat.pstdev(self.iangs)
        self.ispeedsd = stat.pstdev(self.ispeeds)
    def write(self):
        filename = "D:\mlb data\League\MLB_Play_Data.csv"
        teamfile = open(filename, 'w', newline='')
        teamcsv = csv.writer(teamfile)
        teamcsv.writerow(['date','fielder','prebase','preout','postbase','postout','runs','RE24', 'Avg RE24','RAA', 'dist','angle', 'speed','loc','btype'])
           # ['Fielder','PreBase','PostBase','Runs Scored','Distance','Angle','Speed','Location','Event','Team','PostOut','PreOut','Date'])

        for row in self.pdb:
            teamcsv.writerow(row.playcsv())
        teamfile.close()
                

class play(object):
    def __init__(self, fielder, loc, prebase, postbase, runs, dist, angle, speed, date, team, bevent, batter, postout,preout, bbtype, beventtype):
        self.fielder = fielder
        self.prebase = prebase
        self.postbase = postbase
        self.runs = int(runs)
        self.pball = ball(dist, angle, speed, loc, bbtype)
        self.outfield = self.pball.loc in [7,8,9]
        self.team = team
        self.bevent = bevent
        self.postout = int(postout)
        if self.postout > 3: self.postout = 3
        self.preout = int(preout)
        if self.preout == 3: self.preout = 2
        self.date = date
        self.beventtype = beventtype
        self.RE24 = self.RE24Gen()
    def playcsv(self):
        return [self.date,self.fielder,self.prebase,self.preout,self.postbase,self.postout,self.runs,self.RE24, self.simballs, self.avgRE, self.RAA, self.pball.dist,self.pball.angle, self.pball.speed,self.pball.loc,self.pball.btype]
        #[self.fielder, self.prebase, self.postbase, self.runs, self.pball.dist, self.pball.angle, self.pball.speed, self.pball.loc, self.bevent, self.team, self.postout, self.preout, self.date]
    def RE24Gen(self):
        for item in el.runchart:
            if item[0] == self.prebase:
                startstate = item[1][self.preout]
        if self.postout == 3:
            endstate = 0
        else:
            for item in el.runchart:
                if item[0] == self.postbase:
                    endstate = item[1][self.postout]
        re = startstate - endstate - self.runs
        return re
    def RAAgen(self):
        global mlb
        resum = 0
        recnt = 0
        for p in mlb.pdb:
            if not self.pball.bclass == p.pball.bclass or not self.outfield == p.outfield:
                continue
            if self.pball.bclass == p.pball.bclass == 1 and self.outfield and p.outfield:
                similar = (abs(self.pball.dist - p.pball.dist) < mlb.odistsd) and (abs(self.pball.angle - p.pball.angle) < mlb.oangsd) and (abs(self.pball.speed - p.pball.speed) < mlb.ospeedsd)
            elif self.pball.bclass == p.pball.bclass == 1 and not self.outfield and not p.outfield :
                similar = (abs(self.pball.dist - p.pball.dist) < mlb.idistsd) and (abs(self.pball.angle - p.pball.angle) < mlb.iangsd) and (abs(self.pball.speed - p.pball.speed) < mlb.ispeedsd)
            if self.pball.bclass == p.pball.bclass == 2 and self.outfield  and p.outfield:
                similar = (self.pball.loc == p.pball.loc) and (abs(self.pball.angle - p.pball.angle) < mlb.oangsd) and (abs(self.pball.speed - p.pball.speed) < mlb.ospeedsd)
            elif self.pball.bclass == p.pball.bclass == 2 and not self.outfield and not p.outfield:
                similar = (self.pball.loc == p.pball.loc) and (abs(self.pball.angle - p.pball.angle) < mlb.iangsd) and (abs(self.pball.speed - p.pball.speed) < mlb.ispeedsd)
            if self.pball.bclass == p.pball.bclass == 3:
                similar = (self.pball.loc == p.pball.loc) and (self.pball.btype == p.pball.btype)  
            similar = similar and self.prebase == p.prebase and self.preout == p.preout
            if similar:
                resum += p.RE24
                recnt += 1
        self.simballs = recnt
        self.avgRE = resum / recnt
        self.RAA = self.RE24 - self.avgRE
        

class team(object):
    def __init__(self, name, plays, league):
        self.name = name
        self.plays = plays
        self.league = league
    def write(self):
        filename = "D:\mlb data\Team\{}_Play_Data.csv".format(self.name)
        teamfile = open(filename, 'w', newline='')
        teamcsv = csv.writer(teamfile)
        teamcsv.writerow(['date','fielder','prebase','preout','postbase','postout','runs','RE24','Similar Balls','Avg RE24', 'RAA', 'dist','angle', 'speed','loc','btype'])
           # ['Fielder','PreBase','PostBase','Runs Scored','Distance','Angle','Speed','Location','Event','Team','PostOut','PreOut','Date'])
        for row in self.plays:
            teamcsv.writerow(row.playcsv())
        teamfile.close()

class player(object):
    def __init__(self, name, team, plays, idcount = 1):
        self.name = name
        self.team = team
        self.plays = plays
        self.idcount = idcount
        self.playerid = self.playeridgen()
        loc = self.plays[0].pball.loc
        if loc == 1: self.position = 'P'
        elif loc == 2: self.position = 'C'
        elif loc == 3: self.position = '1B'
        elif loc == 4: self.position = '2B'
        elif loc == 5: self.position = '3B'
        elif loc == 6: self.position = 'SS'
        elif loc == 7: self.position = 'LF'
        elif loc == 8: self.position = 'CF'
        elif loc == 9: self.position = 'RF'
        else: self.position = 'OF'

    def playeridgen(self):
        first, last = self.name.split()
        pid = "{}{}00{}".format(last[:3], first[:2],self.idcount)
        return pid
    def write(self):
        filename = "D:\mlb data\Players\{}_Play_Data.csv".format(self.playerid)
        playerfile = open(filename, 'w', newline='')
        playercsv = csv.writer(playerfile)
        playercsv.writerow(['date','fielder','prebase','preout','postbase','postout','runs','RE24','Avg RE24', 'RAA', 'dist','angle', 'speed','loc','btype'])
        for row in self.plays:
            playercsv.writerow(row.playcsv())
        playerfile.close()
    def total(self, file, idx, avgWins):
        totalcsv = file
        if idx == 0:
            totalcsv.writerow(['Fielder', 'Pos', 'Team', 'Play Total', 'Total RE24', 'Total RAA', 'defWins', 'dWAA'])
        totalcsv.writerow(self.totalcalc(avgWins))
    def totalcalc(self, avg):
        self.totalRE24 = 0
        self.totalRAA = 0
        for p in self.plays:
            self.totalRE24 += p.RE24
            self.totalRAA += p.RAA
        self.defWins = self.totalRAA / el.rpw
        self.dWAA = self.defWins - avg
        return [self.name, self.position, self.team, len(self.plays),round(self.totalRE24,3), round(self.totalRAA, 3), round(self.defWins,3), round(self.dWAA, 3)]
            
        
            

class ball(object):
    def __init__(self, dist, angle, speed, loc, btype):
        self.dist = dist
        self.angle = angle
        self.speed = speed
        self.loc = loc
        self.btype = btype
        if self.dist == 'null':
            if self.angle == 'null':
                self.bclass = 3
            else:
                self.bclass = 2
                self.angle = 90 - float(self.angle)
                self.speed = float(self.speed)
        else:
            self.bclass = 1
            self.angle = float(90 - float(self.angle))
            self.dist = float(self.dist)
            self.speed = float(self.speed)



def teamdbcreator(leagueplays):
    teamdb = []
    for teamname in el.teamlist:
        teamplays = []
        for play in leagueplays:
            if teamname == play.team:
                teamplays.append(play)
        teamobj = team(teamname, teamplays, leagueplays)
        teamdb.append(teamobj)
    return teamdb

def playerdbcreator(team):
    playerlist = set()
    playerdb = []
    playlist = []
    for teamplay in team.plays:
        playerlist.add(teamplay.fielder)
    #playerlist.remove('')
    for name in playerlist:
        playlist = []
        for playerplay in team.plays:
            if name == playerplay.fielder:
                playlist.append(playerplay)
        pid = idcntgen(team.league, name, team.name)
        playerobj = player(name, team, playlist, pid)
        playerdb.append(playerobj)
    return playerdb
    
def idcntgen(plays, name, team):
    global pnset
    for idx, item in enumerate(pnset):
        if name == item[0]:
            pnset[idx][1] += 1
            return item[1] + 1
    pnset.append([name,1])
    return 1
    
            
            
##    teamlist = [team]
##    for play in plays:
##        if name == play.fielder and not play.team in teamlist:
##            teamlist.append(play.team)
##            idcnt += 1
##            return idcnt
    return idcnt                

def PlayCreator(data):
    date = DateCreator(data[2])
    des = data[16]
    home = data[20]
    away = data[21]
    loc = int(data[23])
    prebase = BaseCreator(data[34], data[33], data[32])
    inntype = data[37]
    dist = data[53]
    speed = data[54]
    angle = data[55]
##    print(data[9])
    bevent = BEventCreator(data[9])
    beventtype = data[9]
    preout = data[35]
    bbtype, loc = bbtypegen(int(data[24]), des, loc)
    if inntype == 'bot':
        team = away
    else: team = home
    batter, fielder, postout, postbase, runs = DesScraper(des, prebase, preout, bevent)
    return(play(fielder, loc, prebase, postbase, runs, dist, angle, speed, date, team, bevent, batter, postout, preout,bbtype,beventtype))

def bbtypegen(bb, des, loc):
    if bb == 0:
        bb = bbgen(des)
        loc = posgen(des)
    if bb == 1:
        btype = 'fly ball'
    elif bb == 2:
        btype = 'pop fly'
    elif bb == 3:
        btype = 'line drive'
    elif bb == 4:
        btype = 'ground ball'
    else:
        btype = 'dummy'
    return btype, loc

def bbgen(des):
    if 'ground' in des:
        bbtype = 4
    elif 'line' in des:
        bbtype = 3
    elif 'pop' in des:
        bbtype = 2
    elif 'fly' in des or 'flies' in des:
        bbtype = 1
    else:
        bbtype = 4
    return bbtype

def posgen(des):
    for idx, word in enumerate(des.split()):
        if word in ['baseman', 'fielder']:
            posword = des.split()[idx-1]
            if posword == 'first':
                return 3
            elif posword == 'second':
                return 4
            elif posword == 'third':
                return 5
            elif posword == 'left':
                return 7
            elif posword == 'right':
                return 9
            elif posword == 'center':
                return 8
            else:
                print(posword)
                x = input()
        elif word  == 'catcher':
            return 2
        elif word == 'pitcher':
            return 1
        elif word == 'shortstop':
            return 6

def DateCreator(date):
    try:
        if '/' in date:
            date = date.split('/')
            r = 1
        elif '-' in date:
            date = date.split('-')
            r = 2
        for idx, item in enumerate(date):
            date[idx] = int(item)
        if r == 1:
            return dt.date(date[2],date[0], date[1])
        else:
            return dt.date(date[0],date[1],date[2])
    except:
        print(date)
        x = input()
    




        
def BaseCreator(first, second, third):
    base = [0,0,0]
    for idx, runner in enumerate([first, second, third]):
        if runner == 'null':
            base[idx]=0
        else:
            base[idx]=1
    return base

def DesScraper(des, prebase, out, bevent):
##    try:
    deslist = []
    for idx, item in enumerate(des.strip().split(sep='.')):
        if not item == '':
            deslist.append(item.strip())
    bf = deslist[0].split()
    batter = "{} {}".format(bf[0], bf[1])
    fielder = ''
    #print(bf)
    for idx, word in enumerate(des.split()):
        if word in ['baseman', 'fielder', 'catcher', 'pitcher', 'shortstop']:
##                print(bf)
##                print(idx)
            fielder = "{} {}".format(des.split()[idx +  1], des.split()[idx+2])
            if fielder[-1] in string.punctuation:
                fielder = fielder[:-1]
            break
    postbase, postout, runs = PostBaseCreator(deslist[1:], out, prebase, batter, bevent)
    if fielder == '':
        print(deslist)
        fielder = '{} {}'.format(deslist[-1].split()[-2],deslist[-1].split()[-1])
        print(fielder)
        x=input()
    return batter, fielder, postout, postbase, runs
##    except:
##        print(des)
##        print(bf)
##        print(batter)
##        print(fielder)
##        print(idx)
##        print(deslist)
##        x = input()

def PostBaseCreator(play, out, prebase, batter,bevent):
    out = int(out)
    br = sum(prebase)
##    print(bevent)
    bbase, bout = bevent
    runs = 0
    brs = 0
    nout = bout + out
    nbase = [0,0,0]
    nbase[bbase] = 1
    if nout == 3:
        return nbase, nout, runs
    for event in play:
        words = event.split(sep=' ')
        if 'score' in event:
            runs += 1
        elif 'out' in event:
            nout += 1
            if nout + out > 2: break
        elif 'error' in event:
            runner = "{} {}".format(words[0], words[1])
            if runner == batter or runner == "advances to":
                extrabase = True
            else:
                extrabase = False
            if '2nd' in event:
                nbase[1]=1
                if extrabase: bbase = 1
            elif '3rd' in event:
                nbase[2]=1
                if extrabase: bbase = 2
        elif '2nd' in event:
            nbase[1] = 1
        elif '3rd' in event:
            nbase[2] = 1
    if bbase >= 0:
        nbase[bbase] = 1
    return nbase, nout, runs
            
                
def BEventCreator(event):
    for play in el.eventlist:
        if event == play[0]:
            bevent = (play[1], play[2])
            return bevent

def GetData():
    league = open("D:\mlb data\League\league_data.csv")
    leaguecsv = csv.reader(league)
    rawplays = []
    plays = []
    header = 0
    for row in leaguecsv:
        if header == 0:
            header = 1
            continue
        rawplay = row
        rawplays.append(rawplay)
    for rplay in rawplays:
        if rplay[9].lower() in ['home run','catcher interference','fan interference','batter interference']: continue
        if 'ground-rule double' in rplay[16].lower() or 'hit by batted ball' in rplay[16].lower(): continue
        
        play = PlayCreator(rplay)
        plays.append(play)
    return plays
        
    
    
mlb = league(GetData())

teamdb = teamdbcreator(mlb.pdb)

playerdb = []

print("Calculating RAA....")

starttime = time.time()

RAAsum = 0

for idx, pl in enumerate(mlb.pdb):
    pl.RAAgen()
    RAAsum += pl.RAA
    if idx > 1:
        if idx == 1000:
            endtime = time.time() - starttime
            timeper = endtime / 1000
        if idx % 1000 == 0:
            remaining = len(mlb.pdb) - idx
            print('{:.3f}% Done [{}:{} Remaining]'.format(idx / len(mlb.pdb) * 100, int((remaining * timeper) // 60), round((remaining * timeper) % 60)))

mlb.RAAavg = RAAsum / len(mlb.pdb)
mlb.Winsavg = mlb.RAAavg / el.rpw

print("Writing league file...")
mlb.write()

print("Writing team files...")
for teamobj in teamdb:
    playerdb.extend(playerdbcreator(teamobj))
    teamobj.write()

playertotaldb = []

playtotalfile = open('D:\mlb data\League\Player_Total_Data.csv', 'w', newline='')

playtotalcsv = csv.writer(playtotalfile)


print("Writing player files...")
for idx, playerobj in enumerate(playerdb):
    playerobj.write()
    if idx > 0:
        playerobj.team = playerdb[idx].team.name
    playerobj.total(playtotalcsv, idx, mlb.Winsavg)

playtotalfile.close()
                       
print("Done!")

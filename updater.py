import os
import csv
import datetime
import string

def JrFixer(des):

    words = des.strip().split()
    for idx, word in enumerate(words):
        if word == 'Jr.' and not idx == len(words) - 1:
            if idx == 2:
                words[2] = 'Jr'
            elif words[idx+1] in string.punctuation:
                words[idx] = 'Jr'
            elif words[idx+1] in ['to', 'to.', 'advances', 'advances.', 'scores.', 'scores']:
                words[idx] = 'Jr'
        elif len(word) > 1 and word[1] == '.' and not idx == len(words) - 1:
            if len(words[idx+1]) > len('x.'):
                words[idx] = word[0] + 'J'
            else:
                words[idx] = word[0] + words[idx+1][0]
                words[idx+1] = ''
    return ' '.join(words)

def ChallengeRemover(des):
    if 'challenge' in des:
        words = des.split(sep=':')
        return words[1].strip()
    else: return des

def leaguecreator(league, day):
    leaguecsv = csv.writer(league)
    teamfile = open(day)
    teamcsv = csv.reader(teamfile)
    for idx, row in enumerate(teamcsv):
        if idx == 0:
            continue
        elif 'sacrifice bunt.' in row[16] and not 'baseman' in row[16] and not 'catcher' in row[16] and not 'pitcher' in row[16]:
            continue
        else:
            try:
                row[16] = JrFixer(row[16])
                row[16] = ChallengeRemover(row[16])
                leaguecsv.writerow(row)
            except:
                print(row[16])
                x = input()
    return None
            
                
                
    



file = 'D:\mlb data\Daily Update\{}.csv'.format(datetime.date.today())

leaguefile = open("D:\mlb data\League\League_Data.csv", 'a', newline='')

leaguecreator(leaguefile, file)

leaguefile.close()


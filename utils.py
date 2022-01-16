import datetime
import requests

# Returns an iterable that gives two elements of an array at a time.
def pairs(arr):
    p = iter(arr)
    return zip(p,p)

# Gets the time difference between two sequences.
# Format: yyyy-mm-dd, hr:mn:sc, yyyy-mm-dd, hr:mn:sc
def getTimeDiff(s1, s2, e1, e2):
    date = [int(i) for i in s1.split('-')]
    time = [int(i) for i in s2.split(':')]
    start_dt = datetime.datetime(*date, *time)

    date = [int(i) for i in e1.split('-')]
    time = [int(i) for i in e2.split(':')]
    end_dt = datetime.datetime(*date, *time)

    return (end_dt - start_dt).total_seconds()

def getSteamAppList():
    url = 'https://api.steampowered.com/ISteamApps/GetAppList/v0002/'
    r = requests.get(url)
    applist = r.json()['applist']['apps']
    return applist
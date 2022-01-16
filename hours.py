import matplotlib.pyplot as plt
import argparse
import datetime
import requests
import pandas as pd
import calplot
import numpy as np

def pairs(arr):
    p = iter(arr)
    return zip(p,p)

def getTime(s1, s2, e1, e2):
        date = [int(i) for i in s1.split('-')]
        time = [int(i) for i in s2.split(':')]
        start_dt = datetime.datetime(*date, *time)

        date = [int(i) for i in e1.split('-')]
        time = [int(i) for i in e2.split(':')]
        end_dt = datetime.datetime(*date, *time)

        return (end_dt - start_dt).total_seconds()

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="Path to the log file")
    args = parser.parse_args()

    # On Windows, you can generally find this file at C:\Program Files (x86)\Steam\logs
    filename = 'controller_ui.txt' # https://gaming.stackexchange.com/a/382162
    if args.path:
        filename = args.path
    
    f = open(filename, 'r')

    oldest_time = -1
    newest_time = -1
    apps = {}
    for l in f.readlines():
        if l == '\n':
            continue
        
        spl = l.split()

        if len(spl) != 5:
            continue
        
        if spl[2] == 'Starting':
            if oldest_time == -1:
                oldest_time = (spl[0][1:], spl[1][:-1])
            steamid = spl[-1]
            time = (0, spl[0][1:], spl[1][:-1])
            if steamid in apps:
                apps[steamid].append(time)
            else:
                apps[steamid] = [time]
        
        elif spl[2] == 'Exiting':
            steamid = spl[-1]
            newest_time = (spl[0][1:], spl[1][:-1])
            time = (1, spl[0][1:], spl[1][:-1])
            if steamid in apps:
                apps[steamid].append(time)
            else:
                apps[steamid] = [time]


    counts = {}  # time in seconds

    for steamid in apps:
        if steamid not in time:
            counts[steamid] = 0

        for time0, time1 in pairs(apps[steamid]):
            if time0[0] != 0:
                print("Error: unexpected log entry:", *time0[1:])
            if time1[0] != 1:
                print("Error: unexpected log entry:", *time1[1:])

            counts[steamid] += getTime(*time0[1:], *time1[1:])

    names = {}
    url = 'https://api.steampowered.com/ISteamApps/GetAppList/v0002/'
    r = requests.get(url)
    applist = r.json()['applist']['apps']
    
    for app in applist:
        appid = str(app['appid'])
        if appid in apps:
            names[appid] = app['name']

    longest = 0
    for steamid in names:
        longest = max(longest, len(names[steamid]))
    longest += 2

    print("\nHours are taken between {} and {}.".format(oldest_time[0], newest_time[0]))
    print("For games listed as 'ID: ...', lookup the ID on steamdb.info.")
    print(f"{'Name':<{longest}}", 'Hours')
    print('-' * (longest + 10))
    for steamid in counts:
        if steamid in names:
            print(f"{names[steamid]:<{longest}}", f"{counts[steamid]/3600:<.2f}")
        else:
            print(f"{'ID: ' + steamid:<{longest}}", f"{counts[steamid]/3600:<.2f}")


    # all_days = pd.date_range('1/1/2019', periods=730, freq='D')
    # days = np.random.choice(all_days, 500)
    # events = pd.Series(np.random.randn(len(days)), index=days)


    # calplot.calplot(events, cmap='YlGn', colorbar=False)



if __name__ == "__main__":
    main()
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import calplot
import argparse
import datetime
import os
import re
from utils import pairs, getTimeDiff, getSteamAppList

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

    # Get all start and end times
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
            newest_time = (spl[0][1:], spl[1][:-1])
            steamid = spl[-1]
            time = (1, spl[0][1:], spl[1][:-1])
            if steamid in apps:
                apps[steamid].append(time)
            else:
                apps[steamid] = [time]

    f.close()

    counts = {}  # time in seconds

    # Get total hour counts
    for steamid in apps:
        counts[steamid] = 0
        for time0, time1 in pairs(apps[steamid]):
            if time0[0] != 0:
                print("Error: unexpected log entry:", *time0[1:])
            if time1[0] != 1:
                print("Error: unexpected log entry:", *time1[1:])
            counts[steamid] += getTimeDiff(*time0[1:], *time1[1:])

    # Get names from steam IDs
    names = {}
    applist = getSteamAppList()

    for app in applist:
        appid = str(app['appid'])
        if appid in apps:
            names[appid] = app['name']

    # Print table of games and hours
    longest = 0
    for steamid in names:
        longest = max(longest, len(names[steamid]))
    longest += 2

    print("\nHours are taken between {} and {}.".format(oldest_time[0], newest_time[0]))
    print("For games listed as 'ID: ...', you can lookup the ID on steamdb.info.")
    print(f"{'Name':<{longest}}", 'Hours')
    print('-' * (longest + 10))
    for steamid in counts:
        if steamid in names:
            print(f"{names[steamid]:<{longest}}", f"{counts[steamid]/3600:<.2f}")
        else:
            print(f"{'ID: ' + steamid:<{longest}}", f"{counts[steamid]/3600:<.2f}")


    # Create calendar heatmaps (in hours)
    old_split = oldest_time[0].split('-')
    new_split = newest_time[0].split('-')
    old_date = old_split[1] + '/' + old_split[2] + '/' + old_split[0]
    new_date = new_split[1] + '/' + new_split[2] + '/' + new_split[0]

    all_days = pd.date_range(start=old_date, end=new_date)
    day_counts = np.zeros(len(all_days)) # For heatmap across all games

    game_counts = {} # For individual game heatmaps
    timestart = datetime.datetime.strptime(oldest_time[0], "%Y-%m-%d").date()

    # NOTE: uses starting time to determine the day. Does not handle cross-day sessions.
    for steamid in apps:
        game_counts[steamid] = np.zeros(len(all_days))
        for time0, time1 in pairs(apps[steamid]):
            timediff = getTimeDiff(*time0[1:], *time1[1:])            
            current = datetime.datetime.strptime(time0[1], "%Y-%m-%d").date()
            delta = (current - timestart).days
            hours = timediff / 3600.0
            day_counts[delta] += hours
            game_counts[steamid][delta] += hours

    if not os.path.exists('plots'):
        os.makedirs('plots')

    # Plot overall heatmap
    events = pd.Series(day_counts, index=all_days)
    calplot.calplot(events, cmap='YlGn')#, colorbar=False)
    plt.savefig('plots/heatmap.png')
    plt.close()

    # Plot individual heatmaps
    for steamid in game_counts:
        game_days = pd.date_range(start=apps[steamid][0][1], end=apps[steamid][-1][1])
        start = (datetime.datetime.strptime(apps[steamid][0][1], "%Y-%m-%d").date() - timestart).days
        end = (datetime.datetime.strptime(apps[steamid][-1][1], "%Y-%m-%d").date() - timestart).days

        events = pd.Series(game_counts[steamid][start:end+1], index=game_days)
        calplot.calplot(events, cmap='YlGn')
        if steamid in names: # Use regular expressions to strip non-alphanumeric characters
            plt.savefig('plots/{}.png'.format(re.sub(r'\W+', '', names[steamid])))
        else:
            plt.savefig('plots/{}.png'.format(re.sub(r'\W+', '', steamid)))
        plt.close()


if __name__ == "__main__":
    main()
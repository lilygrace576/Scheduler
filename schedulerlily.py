#!/usr/bin/env python3

import os
import ephem
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date, time, timezone
from matplotlib.dates import HourLocator, DateFormatter
import pandas as pd
import logging
import subprocess
from matplotlib.patches import Patch
# Configure logging
os.chdir('/data/TrinityLabComputer/scheduling/')

logging.basicConfig(filename='scheduler.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


latitude = 38.5202  # Latitude of Frisco Peak
longitude = -113.2883  # Longitude Frisco Peak
elevation = 3048  # Elevation of Frisco Peak
#start_date = datetime(2024, 4, 17).replace(tzinfo=timezone.utc, hour=0, minute=0, second=0, microsecond=0) # Current UTC time

# Get the current UTC date
current_utc_date = datetime.now(timezone.utc) #datetime.utcnow().date() deprecated
# Set the time to 00:00:00
start_date = datetime.combine(current_utc_date, time())

# Add one day so that the website will see the next day posting
start_date += timedelta(days=1)

interval_minutes = 1  # Adjust the interval as needed


def moon_position_over_time(latitude, longitude, start_date, interval_minutes):
    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.lon = str(longitude)
    observer.elevation = elevation

    moon_times = []
    moon_altitudes = []

    for hour in range(27):
        current_time = start_date + timedelta(hours=hour)

        for minute in range(0, 60, interval_minutes):
            current_time_with_minute = current_time + timedelta(minutes=minute)
            observer.date = current_time_with_minute
            moon = ephem.Moon(observer)
            m_altitude = float(moon.alt) * 180 / ephem.pi  # Convert altitude to degrees
            moon_times.append(current_time_with_minute)
            moon_altitudes.append(m_altitude)

    # Find the time at which the maximum altitude is reached
    max_altitude_index = moon_altitudes.index(max(moon_altitudes))
    time_of_max_altitude = moon_times[max_altitude_index]

    # Find the time of Moonrise (positive slope crossing y=0)
    moonrise_index = next(
        (i for i in range(1, len(moon_altitudes)) if moon_altitudes[i] > 0 and moon_altitudes[i - 1] <= 0), None)
    time_of_moonrise = moon_times[moonrise_index] if moonrise_index is not None else None

    # Find the time of Moonset (negative slope crossing y=0)
    moonset_index = next(
        (i for i in range(1, len(moon_altitudes)) if moon_altitudes[i] < -3 and moon_altitudes[i - 1] >= -3), None)
    time_of_moonset = moon_times[moonset_index] if moonset_index is not None else None

    return moon_times, moon_altitudes, time_of_max_altitude, time_of_moonrise, time_of_moonset

#Intitalizing Moon
moon_times, moon_altitudes, time_of_max_altitude, time_of_moonrise, time_of_moonset = moon_position_over_time(latitude, longitude, start_date, interval_minutes)


def sun_position_over_time(latitude, longitude, start_date, interval_minutes):
    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.lon = str(longitude)
    observer.elevation = elevation

    sun_times = []
    sun_altitudes = []

    for hour in range(27):
        current_time = start_date + timedelta(hours=hour)

        for minute in range(0, 60, interval_minutes):
            current_time_with_minute = current_time + timedelta(minutes=minute)
            observer.date = current_time_with_minute
            sun = ephem.Sun(observer)
            s_altitude = float(sun.alt) * 180 / ephem.pi
            sun_altitudes.append(s_altitude)
            sun_times.append(current_time_with_minute)

    # Find the time of sunrise (positive slope crossing y=0)
    sunrise_index = next((i for i in range(1, len(sun_times)) if sun_altitudes[i] > 0 and sun_altitudes[i - 1] <= 0), None)
    time_of_sunrise = sun_times[sunrise_index] if sunrise_index is not None else None

    # Finding the time of critical sunrise time (positive slope crossing y=-15)
    sunrise_crit_index = next((i for i in range(1, len(sun_times)) if sun_altitudes[i] > -15 and sun_altitudes[i - 1] <= -15), None)
    time_of_sunrise_crit = sun_times[sunrise_crit_index] if sunrise_crit_index is not None else None

    # Find the time of sunset (negative slope crossing y=0)
    sunset_index = next((i for i in range(1, len(sun_times)) if sun_altitudes[i] < 0 and sun_altitudes[i - 1] >= 0), None)
    time_of_sunset = sun_times[sunset_index] if sunset_index is not None else None

    # Finding the time of critical sunset time (negative slope crossing y=-15)
    sunset_crit_index = next((i for i in range(1, len(sun_times)) if sun_altitudes[i] < -18 and sun_altitudes[i - 1] >= -18), None)
    time_of_sunset_crit = sun_times[sunset_crit_index] if sunset_crit_index is not None else None

    return sun_times, sun_altitudes, time_of_sunrise, time_of_sunset, time_of_sunrise_crit, time_of_sunset_crit


# Initializing Sun
sun_times, sun_altitudes, time_of_sunrise, time_of_sunset, time_of_sunrise_crit, time_of_sunset_crit = sun_position_over_time(latitude, longitude, start_date, interval_minutes)


# Creating plot
fig, ax = plt.subplots()

sun_color = (1.0, 0.8, 0.6)
moon_color = (0.7, 0.7, 0.7)




# Plotting Moon and Sun altitude line
ax.plot(moon_times, moon_altitudes, label='Moon Altitude', color=moon_color, marker='o', markersize=3, linewidth=0.8,
        zorder=1)
ax.plot(sun_times, sun_altitudes, label='Sun Altitude', color=sun_color, marker='o', markersize=3, linewidth=0.8,
        zorder=1)

time_list = []
# Highlight points with dangerous light levels
for i in range(len(moon_altitudes) - 1):
    if moon_altitudes[i] < moon_altitudes[i - 1] and moon_altitudes[i] > -3:
        '''
        ax.axvspan(sun_times[i], sun_times[i + 1], color='grey', alpha=0.05)
        '''
        time_list.append(sun_times[i])

for i in range(len(sun_altitudes) - 1):
   if sun_altitudes[i] > -18 and not ((moon_altitudes[i] < moon_altitudes[i - 1] and moon_altitudes[i] > -3) and sun_times[i] < time_of_sunset_crit):
        '''
        ax.axvspan(sun_times[i], sun_times[i + 1], color='grey', alpha=0.05)
        '''
        time_list.append(sun_times[i])




# Plot more pronounced horizon line
ax.axhline(y=0, color='black', linestyle='--', linewidth=1.5, label='', zorder=5)


# Plot when midnight is
'''
start_date_date = start_date.date()
next_date = start_date_date + timedelta(days=1)
nextday_time = datetime.combine(next_date, time(0, 00))
plt.axvline(x=nextday_time, color='black', linestyle='--')
'''

# Find start and end times (90 minutes after/before sunset/sunrise) **NOT USING ALTITUDE Y=-15**
start_time = None
end_time = None
start_time_2 = None
end_time_2 = None

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
data = {'Moonrise Time': time_of_moonrise, 'Moonset Time': time_of_moonset, 'Moonmax Time': time_of_max_altitude, 'Sunrise Crit Time': (time_of_sunrise_crit), 'Sunset Crit Time': (time_of_sunset_crit)}
index = ['Times']
df = pd.DataFrame(data, index=index)
df_sorted = df.apply(lambda x: pd.to_datetime(x).sort_values(), axis=1)

if not ((time_of_sunset_crit) < time_of_moonset < (time_of_sunrise_crit)): #if sun doesn't set before moon
    start_time = (time_of_sunset_crit) #start time is sunset + 1.5hr
else:
    start_time = (time_of_sunset_crit)

if not ((time_of_sunset_crit) < time_of_max_altitude < (time_of_sunrise_crit)): #if moon peak not between sunrise and sunset
    end_time = (time_of_sunrise_crit) #end at sunrise - 1.5hr
    #print(3)
else:
    if start_time > time_of_max_altitude: #if ending at sunrise - 1.5hr
        end_time = time_of_sunrise_crit
    else:
        end_time = time_of_max_altitude #otherwise, end at moon peak
        #print(4)
        #print(end_time)

# DATA QUALITY START = 32 MIN BEFORE START TIME
data_quality_start = start_time - (timedelta(minutes=32)) #Added -32 min for data quality check start time


if start_time == (time_of_sunset_crit) and end_time == time_of_max_altitude: #start = sunset + 1.5hr, end = moon peak: this is the block we should fix
    if (time_of_sunset_crit) < time_of_moonset < (time_of_sunrise_crit): #if moon sets between sunset and  sunrise
        start_time_2 = time_of_moonset
        end_time = (time_of_sunrise_crit)
        end_time_2 = time_of_max_altitude
        if (end_time_2 - start_time_2) < timedelta(minutes=95):
            print("Observation window too short.")

    # IF MOON SETS AFTER SUNRISE CRIT
    elif time_of_moonset > time_of_sunrise_crit:
        start_time_2 = time_of_sunset_crit
        end_time_2 = time_of_max_altitude
        end_time = time_of_sunrise_crit
        # IF PEAK TIME - SUNSET CRIT TIME LESS THAN 95MIN (MOON PEAKS 95 MIN AFTER SUNSET)
        if (end_time_2 - start_time) < timedelta(minutes=95):
            # WINDOW TOO SHORT
            print("Observation window too short.")
        for i in range(len(moon_altitudes) - 1):
            if end_time_2 < sun_times[i] < end_time:
                # SHADE TIME REGION -> SHADED = CLOSED DOOR OBS PERIOD
                ax.axvspan(sun_times[i], sun_times[i + 1], facecolor='white', alpha=0.25, hatch = 'xx')

# IF START AT SUNSET CRIT AND END AT SUNSRISE CRIT
elif start_time == (time_of_sunset_crit) and end_time == time_of_sunrise_crit:
    # IF MOON SETS B/T SUNSET AND SUNRISE
    if (time_of_sunset_crit) < time_of_moonset < (time_of_sunrise_crit):
        # OBS TIME STARTS AT MOONSET
        start_time_2 = time_of_moonset
        # OBS TIME ENDS AT SUNRISE CRIT
        end_time_2 = time_of_sunrise_crit
        # IF CRIT SUNRISE TIME - MOONSET TIME LESS THAN 95MIN (MOON SETS 95 MIN BEFORE SUNRISE)
        if (end_time - start_time_2) < timedelta(minutes=95):
            # WINDOW TOO SHORT
            print("Observation window too short.")


# Adding sources of interest

def ngc_position_over_time(latitude, longitude, start_date, interval_minutes):
    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.lon = str(longitude)
    observer.elevation = elevation

    ngc = ephem.FixedBody()
    ngc.name = 'NGC 1068'
    ngc._ra = '02:42:40.7091669408'
    ngc._dec = '-00:00:47.859690204'
    ngc._epoch = '2000'

    ngc_times = []
    ngc_altitudes = []

    for hour in range(24):
        current_time = start_date + timedelta(hours=hour)

        for minute in range(0, 60, interval_minutes):
            current_time_with_minute = current_time + timedelta(minutes=minute)
            observer.date = current_time_with_minute
            ngc.compute(observer)
            ngc_altitude = float(ngc.alt) * 180 / ephem.pi
            ngc_altitudes.append(ngc_altitude)
            ngc_times.append(current_time_with_minute)

    return ngc_times, ngc_altitudes

ngc_times, ngc_altitudes = ngc_position_over_time(latitude, longitude, start_date, interval_minutes)

def txs_position_over_time(latitude, longitude, start_date, interval_minutes):
    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.lon = str(longitude)
    observer.elevation = elevation

    txs = ephem.FixedBody()
    txs.name = 'TXS 0506'
    txs._ra = '05:09:25.9644373872'
    txs._dec = '05:41:35.333820420'
    txs._epoch = '2000'

    txs_times = []
    txs_altitudes = []

    for hour in range(24):
        current_time = start_date + timedelta(hours=hour)

        for minute in range(0, 60, interval_minutes):
            current_time_with_minute = current_time + timedelta(minutes=minute)
            observer.date = current_time_with_minute
            txs.compute(observer)
            txs_altitude = float(txs.alt) * 180 / ephem.pi
            txs_altitudes.append(txs_altitude)
            txs_times.append(current_time_with_minute)

    return txs_times, txs_altitudes

txs_times, txs_altitudes = txs_position_over_time(latitude, longitude, start_date, interval_minutes)


ngc_observing = []
for i in range(len(ngc_times) - 1):
    if ((0 > ngc_altitudes[i] > -10) or (0 > ngc_altitudes[i+1] > -10)) and (ngc_altitudes[i] > ngc_altitudes[i+1]):
        ngc_observing.append(ngc_times[i])
for i in range(len(ngc_observing) - 1):
    ax.axvspan(ngc_observing[i], ngc_observing[i + 1], color='blue', alpha=0.05)
#text = ax.text(0.02, 0.97, 'NGC 1068 observing window', color='blue', fontsize=7, ha='left', va='top', transform=ax.transAxes, bbox=dict(facecolor='white', alpha=1, edgecolor='grey'))
#text2 = ax.text(0.02, 0.9094, 'TXS 0506+056 observing window', color='purple', fontsize=7, ha='left', va='top', transform=ax.transAxes, bbox=dict(facecolor='white', alpha=1, edgecolor='grey'))
txs_observing = []
for i in range(len(txs_times) - 1):
    if ((0 > txs_altitudes[i] > -10) or (0 > txs_altitudes[i+1] > -10)) and (txs_altitudes[i] > txs_altitudes[i+1]):
        txs_observing.append(txs_times[i])
for i in range(len(txs_observing) - 1):
    ax.axvspan(txs_observing[i], txs_observing[i + 1], color='purple', alpha=0.05)


# Print the times of interest

logging.info(f"Moonrise Time: {time_of_moonrise.strftime('%m-%d %H:%M')}")
logging.info(f"Moonset Time: {time_of_moonset.strftime('%m-%d %H:%M')}")
logging.info(f"Sunrise Time: {time_of_sunrise.strftime('%m-%d %H:%M')}")
logging.info(f"Sunset Time: {time_of_sunset.strftime('%m-%d %H:%M')}")

logging.info(f"\033[1mStart Time: {start_time.strftime('%m-%d %H:%M')}\033[0m")   # "\033[1m" and "\033[0m" make the text bold
logging.info(f"\033[1mEnd Time: {end_time.strftime('%m-%d %H:%M')}\033[0m")   # "\033[1m" and "\033[0m" make the text bold

if not (start_time_2 == None and end_time_2 == None):
   logging.info(f"\033[1mStart Time 2: {start_time_2.strftime('%m-%d %H:%M')}\033[0m")   # "\033[1m" and "\033[0m" make the text bold
   logging.info(f"\033[1mEnd Time 2: {end_time_2.strftime('%m-%d %H:%M')}\033[0m")   # "\033[1m" and "\033[0m" make the text bold


# Write to text file for trinity.py
with open("eon_times.txt", "w") as file: #Changed
    file.write(f"Moonrise Time: {time_of_moonrise}\n")
    file.write(f"Moonset Time: {time_of_moonset}\n")
    file.write(f"Sunrise Time: {time_of_sunrise}\n")
    file.write(f"Sunset Time: {time_of_sunset}\n")
    
    if not (start_time_2 == None and end_time_2 == None):
        if start_date < end_time:
            file.write(f"Start Time: {start_time.strftime}\n")
            file.write(f"End Time: {end_time}\n")
        elif start_time_2 < (time_of_sunrise_crit) and start_time_2 > (time_of_sunset_crit):
            file.write(f"Start Time 2: {start_time_2}\n")
            file.write(f"End Time 2: {end_time_2}\n")  

    file.write(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n") #Changed
    file.write(f"End Time: {end_time}\n")

print("Times have been written to eon_times.txt") #Changed



plt.xlim(min(sun_times), min(sun_times) + timedelta(hours=24))


def moon_illumination(latitude, longitude, start_date):
    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.lon = str(longitude)
    observer.elevation = elevation
    observer.date = start_date
    moon = ephem.Moon()
    moon.compute(observer)
    illumination = moon.moon_phase
    return round((illumination * 100))

illumination = moon_illumination(latitude, longitude, start_date)

#CHART LABELS
# Improve chart labels
start_date_str = start_date.strftime("%m-%d-%Y")
fig.patch.set_facecolor('white')
ax.set_facecolor('white')
ax.set_xlabel('Time (UTC)', fontsize=10)
ax.set_ylabel('Elevation (degrees)', fontsize=10)
ax.set_title('Demonstrator Operation Schedule ' + start_date_str + ' UTC', fontsize=14)
# ax.set_title('Demonstrator Operation Schedule ' + start_date_str + f' UTC\nMoonphase: {illumination}%', fontsize=14)
ax.xaxis.set_major_locator(HourLocator(interval=3))
ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
ax.xaxis.set_minor_locator(HourLocator(interval=1))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.grid(True)

# PLOT AND LEGEND
 
# PLOT OBS START TIME LINE, OBS END TIME LINE, AND EXTRIGS DATA QUALITY START TIME LINE
plt.axvline(x=start_time, color='green', linestyle='--', linewidth=2, alpha=1)
plt.axvline(x=data_quality_start, color='darkslateblue', linestyle='--', linewidth=1, alpha=1)
plt.axvline(x=end_time, color='red', linestyle='--', linewidth=2, alpha=1)


# IF START/END 2 EXIST PLOT PALE GREEN/RED LINE
if not (start_time_2 == None and end_time_2 == None):
    plt.axvline(x=start_time_2, color='green', linestyle='--', linewidth=2, alpha=0.5)
    # IF 2 ENDS 1 START
    if not (end_time == end_time_2) and (start_time == start_time_2):
        plt.axvline(x=end_time_2, color='red', linestyle='--', linewidth=2, alpha=0.5)



# SHADED/HASHED REGIONS

# ENTIRE OBS PERIOD
for i in range(len(moon_altitudes) - 1):
    # IF SUN TIME ATFER START TIME
    if start_time < sun_times[i] < end_time:
        # SHADE REGION -> GREY SHADED = OBS PERIOD
        ax.axvspan(sun_times[i], sun_times[i + 1], color='grey', alpha=0.05)

# DOOR UP OBS PERIOD 
for i in range(len(moon_altitudes) - 1):
    # IF START/END 2 EXIST
    if not (start_time_2 == None and end_time_2 ==None):
        # IF 2 STARTS AND ENDS
        if not (end_time == end_time_2 and start_time == start_time_2):
            # IF TIME SAFE AND AFTER START 2
            if not (sun_times[i] in time_list) and sun_times[i] > start_time_2:
                ax.axvspan(sun_times[i], sun_times[i + 1], color='grey', alpha=0.1)
        # IF 2 STARTS 1 END
        elif not (start_time == start_time_2) and (end_time == end_time_2):
            # IF SUN TIME SAFE (NOT IN DANGEROUS LIGHT LEVELS TIME_LIST) AND AFTER START TIME 2
            if not (sun_times[i] in time_list) and sun_times[i] > start_time_2:
                # HASH THAT TIME REGION -> // = SAFE OBS PERIOD W DOOR UP
                ax.axvspan(sun_times[i], sun_times[i + 1], color='grey', alpha=0.1)
        # IF 2 ENDS 1 START
        elif not (end_time == end_time_2) and (start_time == start_time_2):
            # IF TIME SAFE AND B/T START AND END 2
            if not (sun_times[i] in time_list) and start_time < sun_times[i] < end_time_2:
                ax.axvspan(sun_times[i], sun_times[i + 1], color='grey', alpha=0.1)

    # IF NO START 2
    else:
        # IF SUN TIME SAFE (NOT IN DANGEROUS LIGHT LEVELS TIME_LIST) AND AFTER START TIME
        if not (sun_times[i] in time_list) and sun_times[i] > start_time:
            # HASH THAT TIME REGION -> // = SAFE OBS PERIOD W DOOR UP
            ax.axvspan(sun_times[i], sun_times[i + 1], color='grey', alpha=0.05)

# // DOOR CLOSED OBS PEROIOD 
for i in range(len(moon_altitudes) - 1):
    # IF TIME AFTER NOISE START AND BEFORE START TIME
    if data_quality_start < sun_times[i] < start_time:
        # HASH TIME REGION -> \\ = CLOSED DOOR OBS PERIOD
        ax.axvspan(sun_times[i], sun_times[i + 1], facecolor='none', edgecolor='grey', hatch = 'xx', alpha=0.7, linewidth=0.0)
for i in range(len(moon_altitudes) - 1):
    # IF START/END 2 EXIST
    if not (start_time_2 == None and end_time_2 == None):
        # IF 2 STARTS AND ENDS
        if not (end_time == end_time_2 and start_time == start_time_2):
            # IF TIME B/T START AND END 2
            if start_time < sun_times[i] < start_time_2:
                # HASH TIME REGION -> \\ = CLOSED DOOR OBS PERIOD
                ax.axvspan(sun_times[i], sun_times[i + 1], facecolor='none', edgecolor='grey', hatch = 'xx', alpha=0.7, linewidth=0.0)
        # IF 2 STARTS 1 END
        elif not (start_time == start_time_2) and (end_time == end_time_2):
            # IF TIME B/T START AND START 2
            if start_time < sun_times[i] < start_time_2:
                ax.axvspan(sun_times[i], sun_times[i + 1], facecolor='none', edgecolor='grey', hatch = 'xx', alpha=0.7, linewidth=0.0)
        # IF 2 ENDS 1 START
        elif (not (end_time == end_time_2)) and (start_time == start_time_2):
            if end_time_2 < sun_times[i] < end_time:
                ax.axvspan(sun_times[i], sun_times[i + 1], facecolor='none', edgecolor='grey', hatch = 'xx', alpha=0.7, linewidth=0.0)


# # CREATE LEGEND
# legend_elements_2 = [
#     Patch(color='white', label = f'Moonphase: {illumination}%'),
# ]

# IF START/END 2 EXIST
if not (start_time_2 == None and end_time_2 == None):
    legend_elements = [
        Patch(color='blue', alpha = 0.5, label='NGC 1068 Obs. Window'),
        Patch(color='purple', alpha=0.5, label='TXS 0506 Obs. Window'),
        Patch(facecolor='darkslateblue', label = f'Extrigs Start: {data_quality_start.strftime("%H:%M")} UTC'),
        Patch(facecolor='green', label = f'Obs. Start: {start_time.strftime("%H:%M")} UTC'),
        Patch(facecolor='red', label = f'Obs. End: {end_time.strftime("%H:%M")} UTC'),
        # PALE LINES
        Patch(facecolor='green', alpha = 0.5, label = f'Transition: {start_time_2.strftime("%H:%M")} UTC'),
        Patch(facecolor='red', alpha = 0.5, label = f'Transition: {end_time_2.strftime("%H:%M")} UTC'),
        # DOOR CLOSED/OPEN OBS PERIODS
        Patch(facecolor='grey', alpha = 1, label = 'Door Open Obs'),
        Patch(facecolor='white', alpha = .75, hatch='xx', label = 'Door Closed Obs'),
        Patch(color='grey', alpha = 0.5, label = 'Moon Position Relative'),
        Patch(color='orange', alpha=0.5, label = 'Sun Position Relative'),
        Patch(color='white', label = f'Moonphase: {illumination}%'),
    ]
# NO START 2
else: 
    legend_elements = [
        Patch(color='blue', alpha = 0.5, label='NGC 1068 Obs. Window'),
        Patch(color='purple', alpha=0.5, label='TXS 0506 Obs. Window'),
        Patch(facecolor='darkslateblue', label = f'Extrigs Start: {data_quality_start.strftime("%H:%M")} UTC'),
        Patch(facecolor='green', label = f'Obs. Start: {start_time.strftime("%H:%M")} UTC'),
        Patch(facecolor='red', label = f'Obs. End: {end_time.strftime("%H:%M")} UTC'),
        # DOOR CLOSED/OPEN OBS PERIODS
        Patch(facecolor='grey', alpha = 1, label = 'Door Open Obs'),
        Patch(facecolor='white', alpha = .75, hatch='xx', label = 'Door Closed Obs'),
        Patch(color='grey', alpha = 0.5, label = 'Moon Position Relative'),
        Patch(color='orange', alpha=0.5, label = 'Sun Position Relative'),
        Patch(color='white', label = f'Moonphase: {illumination}%'),
    ]

# Adding legend with custom legend entrie
legend = ax.legend(fontsize=8, loc='lower right',handles=legend_elements)
legend.get_frame().set_facecolor('white')
legend.get_frame().set_alpha(0.8)

# legend_2 = plt.legend(fontsize=8, loc='upper right',handles=legend_elements_2)
# legend_2.get_frame().set_facecolor('white')
# legend_2.get_frame().set_alpha(0.8)

ax.add_artist(legend)


if illumination >= 90:
    # MAKE MOONPHASE LABEL IN LEGEND RED
    for text in legend.get_texts():
        label = text.get_text()
        if 'Moonphase' in label:
            text.set_color('red')


os.chdir('/data/TrinityLabComputer/scheduling/')
formated_date=current_utc_date.strftime('%Y%m%d')
plt.savefig(f'schedule.png', format='png', transparent=True, dpi=600, facecolor=fig.get_facecolor())

os.chdir('/data/TrinityLabComputer/scheduling/schedule_pdf/')
next_day_utc = current_utc_date + timedelta(days=1)
#print(next_day_utc)
file_date=next_day_utc.strftime('%Y%m%d')

plt.savefig(f'schedule_{file_date}.pdf', format='pdf')
#plt.savefig(f'schedule_20240418.pdf',format='pdf')

try:
    os.chdir('/data/TrinityLabComputer/scheduling/')
    # Run the program
    result = subprocess.run(["sudo", "./update_site.exp"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Log the output if the program runs successfully
    logging.info("Output: %s", result.stdout)
except subprocess.CalledProcessError as e:
    # Log the error if the program exits with a non-zero status code
    logging.error("Error: %s", e)
    logging.error("Program output (if available): %s", e.output)
except Exception as e:
    # Log other exceptions
    logging.error("An error occurred: %s", e)


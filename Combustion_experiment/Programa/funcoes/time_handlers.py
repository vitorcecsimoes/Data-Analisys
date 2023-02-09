
def timeToSeconds(timeString,delimiter):
    siplitTime=timeString.split(delimiter)
    seconds=int(siplitTime[0])*3600+int(siplitTime[1])*60+int(siplitTime[2])
    return seconds

def secondsToTime(time):
    hour=int(time/3600)
    minutes=int((time%3600)/60)
    seconds=int(time%60)
    if minutes<10:
        minutes=f"0{minutes}"
    if seconds<10:
        seconds=f"0{seconds}"    
    timeText=f"{hour}:{minutes}:{seconds}"
    return timeText
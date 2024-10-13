import csv
import datetime
import discord
import asyncio

AUTH_KEY = ''
TIMEDIFF = 1

MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

RTDAYS = [MONDAY, WEDNESDAY, SATURDAY]

GUILD_ID = 164062782881398793
CHANNEL_ID = 989221264143048834
PIN_ID = 991733635575197757
PIN_NEXT_RAID = 1275458504554971136

DEBUG_GUILD_ID = 720392289855340638
DEBUG_CHANNEL_ID = 964233249616453703
DEBUG_PIN_ID = 1275132882003820606
DEBUG_PIN_NEXT_RAID = 1275136128391057420

LOGFILE = "/home/tene/Discord/logs/logtimer.log"

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents = intents)
tree = discord.app_commands.CommandTree(client)

def add_timezone(msktime):
    msktimeobj = datetime.datetime.strptime(msktime, '%d.%m.%Y - %H:%M')
    amstimeobj = msktimeobj - datetime.timedelta(hours=TIMEDIFF)
    stamp = datetime.datetime.timestamp(amstimeobj)
    msg = '<t:' + str(int(stamp)) + ':f>'
   # amstime = datetime.datetime.strftime(amstimeobj, '%d.%m.%Y - %H:%M')
   # skydestimeobj = msktimeobj + datetime.timedelta(hours=2)
   # skydestime = datetime.datetime.strftime(skydestimeobj, '%d.%m.%Y - %H:%M')
   # reply = msktime + " (МСК)\n" + amstime + " (АМС)\n" + skydestime + " (СкудecTZ)"
    reply = msktime + " (МСК)\n" + msg
    return reply

def writelog (msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d|%H:%M:%S")
    with open(LOGFILE, "a") as myfile:
        myfile.write(timestamp + ": " + msg + "\n")

async def updateRaidTimeMessage(time):
    channel = client.get_channel(CHANNEL_ID)
    msg = await channel.fetch_message(PIN_NEXT_RAID)
    newcontent = "СЛЕДУЮЩИЙ РЕЙД:\n" + time
    await msg.edit(content=newcontent)


def nextraid(msg):
    changes = []
    raiddates = []
    raidtimes = []
    now = datetime.datetime.now()
    today = datetime.date.today()

    for i in [0,7,14]:
        for day_int in RTDAYS:
            day = today + datetime.timedelta((day_int - today.weekday()) % 7 + i )
            if day_int == 5:
                raidtime = "19:00"
            else:
                raidtime = "20:00"

            raidtimes.append(raidtime)
            raiddates.append(day)

    msg = msg.replace("Переносы:\n", "")
    msg = msg.replace(" -> ", ",")
    msg = msg.replace(" - ", ",")

    changes = []
    reader = csv.reader(msg.splitlines(), delimiter=',')
    for row in reader: # each row is a list
        changes.append(row)

    for change in changes:
        oldDate = datetime.datetime.strptime(change[0] , '%d.%m.%Y').date()
        if oldDate in raiddates:
            index = raiddates.index(oldDate)
            raiddates.pop(index)
            raidtimes.pop(index)
        if change[1].lower() != "отмена":
            newDate = datetime.datetime.strptime(change[1] , '%d.%m.%Y').date()
            if newDate >= today:
                raiddates.append(newDate)
                raidtimes.append(change[2])

    raiddates, raidtimes = (list(t) for t in zip(*sorted(zip(raiddates, raidtimes))))

    while True:
        try:
            nextraidstart = raidtimes[0].split(" - ")[0]
        except:
            return "No valid time found"

        nextraidstart = datetime.datetime.strptime(nextraidstart , '%H:%M')
        nextraidstart = nextraidstart.replace(year = raiddates[0].year)
        nextraidstart = nextraidstart.replace(month = raiddates[0].month)
        nextraidstart = nextraidstart.replace(day = raiddates[0].day)

        if now > nextraidstart:
            raidtimes.pop(0)
            raiddates.pop(0)
        else:
            break

    message = nextraidstart.strftime("%d.%m.%Y - %H:%M")
    return message

@client.event
async def on_ready():
    with open(LOGFILE, "a") as myfile:
        myfile.write("==================================================\n")
    writelog("logged in")
    channel = client.get_channel(CHANNEL_ID)
    msg = await channel.fetch_message(PIN_ID)
    reply = nextraid(msg.content)
    oldraid = await channel.fetch_message(PIN_NEXT_RAID)
    oldraid = oldraid.content.split("\n")[1].replace(" (МСК)","")
    writelog ("oldraid="+oldraid)
    writelog ("newraid="+reply)
    if oldraid != reply:
        reply_withtimezone = add_timezone(reply)
        writelog("different, updating message")
        await updateRaidTimeMessage(reply_withtimezone)

    now = datetime.datetime.now() + datetime.timedelta(hours=TIMEDIFF)
    raidtime = datetime.datetime.strptime(reply, "%d.%m.%Y - %H:%M")
    timediff = raidtime - now
    writelog("till raid in s =" + str(timediff.total_seconds()))
    hours = timediff.total_seconds() / 3600
    writelog("till raid in h =" + str(hours))
    if 1800 < timediff.total_seconds() < 5400:
       writelog("Sending reminder")
       await channel.send("<@&989220836554711051> KIND REMINDER: НАЧАЛО РЕЙДА ЧЕРЕЗ ЧАС\n" + reply)
    writelog("done, close")
    await client.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(client.start(AUTH_KEY))
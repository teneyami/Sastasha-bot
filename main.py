import csv
import datetime
import discord
import logging
import socket
import time

AUTH_KEY = ''
LOGFILE = "/home/tene/Discord/logs/main.log"
TIMEDIFF = 1

MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

RTDAYS = [MONDAY, WEDNESDAY, SATURDAY]

VERBS = ["когда","када","кода","кагда", "коды"]
NOUNS = ["рейд","рэйд", "рт"]

GUILD_ID = 164062782881398793
CHANNEL_ID = 989221264143048834
PIN_ID = 991733635575197757
PIN_NEXT_RAID = 1275458504554971136

DEBUG_GUILD_ID = 720392289855340638
DEBUG_CHANNEL_ID = 964233249616453703
DEBUG_PIN_ID = 1275132882003820606
DEBUG_PIN_NEXT_RAID = 1275136128391057420

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents = intents)
tree = discord.app_commands.CommandTree(client)

def check_internet_connection():
    remote_server = "www.google.com"
    port = 80
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect((remote_server, port))
        return True
    except socket.error:
        return False
    finally:
        sock.close()

async def updateRaidTimeMessage(time):
    channel = client.get_channel(CHANNEL_ID)
    msg = await channel.fetch_message(PIN_NEXT_RAID)
    newcontent = "СЛЕДУЮЩИЙ РЕЙД:\n" + time
    await msg.edit(content=newcontent)

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

@tree.command(
    name="when_raid",
    description="Время следующегой рейда",
    guild=discord.Object(id=GUILD_ID)
)
async def when_raid(interaction):
    channel = client.get_channel(CHANNEL_ID)
    msg = await channel.fetch_message(PIN_ID)
    reply = nextraid(msg.content)
    reply = add_timezone(reply)
    await interaction.response.send_message(reply)
    await updateRaidTimeMessage(reply)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await tree.sync(guild=discord.Object(id=GUILD_ID))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    channel = client.get_channel(message.channel.id)
    if channel.id != CHANNEL_ID:
        return
    msgcontent = message.content.lower()
    for verb in VERBS:
        for noun in NOUNS:
            query = verb + " " + noun
            if query in msgcontent:
                channel = client.get_channel(CHANNEL_ID)
                msg = await channel.fetch_message(PIN_ID)
                reply = nextraid(msg.content)
                reply_withtimezone = add_timezone(reply)
                await message.channel.send(reply_withtimezone)

while not check_internet_connection():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d|%H:%M:%S")
    with open(LOGFILE, "a") as myfile:
        myfile.write(timestamp + ": No internet\n")
    time.sleep(60)
    continue

handler = logging.FileHandler(filename=LOGFILE, encoding='utf-8', mode='w')
client.run(AUTH_KEY, log_handler=handler)
import datetime
import discord
import asyncio

AUTH_KEY = ''
GUILD_ID = 164062782881398793
CHANNEL_ID = 989221264143048834

BDDICT = {
  "Настя":      "21.01",
  "Паша":       "8.07",
  "Дима":       "25.07",
  "Tene":       "22.08",
  "Morgaza":    "6.10",
  "Skydes":     "26.12",
  "Mikoto":     "3.9",
  "Raikou":     "9.7",
  "Fenny":      "24.08"
}

LOGFILE = "/home/tene/Discord/logs/BD.log"

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents = intents)

def writelog (msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d|%H:%M:%S")
    with open(LOGFILE, "a") as myfile:
        myfile.write(timestamp + ": " + msg + "\n")

@client.event
async def on_ready():
    writelog("logged in")
    channel = client.get_channel(CHANNEL_ID)
    today = datetime.date.today()
    for name,date in BDDICT.items():
        if date == "":
            continue
        bd = datetime.datetime.strptime(date, '%d.%m').date()
        if today.month == bd.month and today.day == bd.day:
            writelog ("BD: " + name + " " + date)
            await channel.send("<@&989220836554711051> " + name + " с днем рождения!!!")

    writelog("Done")
    await client.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(client.start(AUTH_KEY))

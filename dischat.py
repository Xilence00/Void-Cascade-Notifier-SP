import discord
import aiohttp
import asyncio
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
YOUR_USER_ID = int(os.getenv("DISCORD_USER_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def get_steel_path_fissures():
    url = 'https://api.warframestat.us/pc/fissures'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"Accept": "application/json"}) as response:
            if response.status != 200:
                return None, f"❌ Failed to fetch data. Status: {response.status}"
            try:
                data = await response.json()
            except Exception as e:
                return None, f"⚠️ Failed to parse JSON: {e}"

            filtered = [
                f"⚔️ **{fissure['tier']}** - {fissure['missionType']} on "
                f"{fissure['node']} ({fissure['enemy']}) - {fissure['eta']} remaining"
                for fissure in data
                if fissure.get('isHard') and
                   fissure.get('tier', '').lower() == 'omnia' and
                   fissure.get('missionType', '').lower() == 'void cascade'
            ]

            if filtered:
                return "\n".join(filtered), None
            return None, None

async def send_fissures_periodically():
    await client.wait_until_ready()
    user = await client.fetch_user(YOUR_USER_ID)

    while not client.is_closed():
        try:
            message, error = await get_steel_path_fissures()
            if error:
                print(error)
            elif message:
                for i in range(0, len(message), 2000):
                    await user.send(message[i:i+2000])
                print("✅ DM sent.")
            else:
                print("ℹ️ No Void Cascade Steel Path Omnia fissures at this time.")
        except discord.Forbidden:
            print("❌ Cannot send DM. Check if DMs are enabled from server members.")
        except Exception as e:
            print(f"⚠️ Error sending DM: {e}")

        await asyncio.sleep(30 * 60)

@client.event
async def on_ready():
    print(f"🤖 Logged in as {client.user}")
    client.loop.create_task(send_fissures_periodically())

client.run(TOKEN)

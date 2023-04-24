import discord


class Mimic(discord.Bot):
    async def on_ready(self):
        print(f"{self.user} is ready and connected to Discord!")

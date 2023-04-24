import os

import dotenv
import gspread

from src import Mimic

dotenv.load_dotenv()
sa = gspread.service_account(filename=os.getenv("SERVICE_ACCOUNT"))
sh = sa.open_by_url(os.getenv("SHEET_URL"))

swk = sh.get_worksheet(0)

bot = Mimic()

cogs_list = [
    "panda"
]

for cog in cogs_list:
    bot.load_extension(f"cogs.{cog}")

bot.run(str(os.getenv("DISCORD_TOKEN")))

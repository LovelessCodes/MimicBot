import os
from urllib import parse

import aiohttp
import discord
import gspread
from discord.ext import commands
from gspread.utils import ValueInputOption

from utils.embed import MimicEmbed
from utils.panda import PandaBuy


class Panda(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.sa = gspread.service_account(
            filename=os.getenv("SERVICE_ACCOUNT"))
        self.sh = self.sa.open_by_url(os.getenv("SHEET_URL"))
        self.swk = self.sh.get_worksheet(0)
        self.sess = aiohttp.ClientSession()
        self.sess.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0)" +
            " Gecko/20100101 Firefox/112.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "deflate",
            "Content-Type": "application/json;charset=utf-8",
            "Authorization": f"Bearer {os.getenv('PANDABUY_AUTH')}",
            "Cookie": os.getenv("PANDABUY_COOKIES"),
        })
        self.pb = PandaBuy()
        print("PandaBuy cog loaded")

    @discord.slash_command(
        name="sheets",
        description="Get a link to the rep Google Sheets"
    )
    async def sheets(self, ctx):
        embed = MimicEmbed(
            title="BTCPanda Reps",
            description="Here is a link to the Google Sheets with all the best reps" +
            "\nand the best sellers for each item," +
            " as well as quality check photos for the items.",
            url=os.getenv("SHEET_URL"),
            color=0x38f8f8
        )
        await ctx.respond(embed=embed)
        return

    @discord.slash_command(
        name="add",
        description="Add a PandaBuy product to the Google Sheets"
    )
    async def add_sheet(
        self,
        ctx,
        category: discord.Option(
            str,
            description="The Category the product should be placed under",
            required=True
        ),
        product: discord.Option(
            str,
            description="The name of the product",
            required=True
        ),
        link: discord.Option(
            str,
            description="The PandaBuy link to the product",
            required=True
        ),
        qc: discord.Option(
            str,
            description="The link to the QC photo(s) for the product",
            required=True
        ),
    ):
        await ctx.respond(embed=MimicEmbed(
            title="PandaBuy Info",
            description="Getting info from the PandaBuy link you provided ..."
        ))
        prod = self.swk.find(product)

        if prod is not None:
            await ctx.edit(embed=MimicEmbed(
                title="Sheets Error",
                description="Error: Product already exists"
            ))
            return

        cat = self.swk.find(category)

        if cat is None:
            await ctx.edit(embed=MimicEmbed(
                title="Sheets Error",
                description="Error: Invalid Category"
            ))
            return

        qc = qc.split("?")[0]
        qc = await self.pb.upload_qc(qc)
        if type(qc) == str:
            await ctx.edit(MimicEmbed(
                title="Internal Error",
                description=qc
            ))
            return
        qc = qc["files"][0]

        if "pandabuy.page.link" in link:
            real_url = await self.pb.get_real_panda_link(link)
        else:
            real_url = link

        url = parse.parse_qs(parse.urlparse(real_url).query)["url"][0]

        info = await self.pb.get_panda_info(url)

        if type(info) == str:
            await ctx.edit(embed=MimicEmbed(
                title="Internal Error",
                description=info
            ))
            return

        embed = MimicEmbed(
            title="PandaBuy Info",
            description="Here is the info from the PandaBuy link you provided\n" +
            "I've gone ahead and added it to the Google Sheets for you",
            fields=[
                discord.EmbedField(
                    name="Product",
                    value=product,
                    inline=True,
                ),
                discord.EmbedField(
                    name="Category",
                    value=category,
                    inline=True,
                ),
                discord.EmbedField(
                    name="Item Price",
                    value=f'¥ {info["data"]["item"]["price"]} |' +
                    f' $ {round(float(info["data"]["item"]["price"]) / 6.5, 2)}',
                    inline=True,
                ),
            ],
            image=qc
        )
        await ctx.edit(embed=embed)

        self.swk.insert_row(
            [
                product,
                f'=LINK("{link}";"CLICK HERE")',
                f'¥ {info["data"]["item"]["price"]}',
                f'$ {round(float(info["data"]["item"]["price"]) / 6.5, 2)}',
                f'=IMAGE("{qc}")'
            ],
            cat.row + 1,
            value_input_option=ValueInputOption.user_entered
        )
        self.swk.format(f"A{str(cat.row+1)}:E{str(cat.row+1)}", {
            "backgroundColor": {
                "red": 0.62,
                "green": 0.77,
                "blue": 0.91,
            },
            "horizontalAlignment": "CENTER",
            "textFormat": {
                "foregroundColor": {
                    "red": 1.0,
                    "green": 1.0,
                    "blue": 1.0,
                },
                "fontSize": 16,
            },
        })
        self.swk.format(f"B{str(cat.row+1)}", {
            "textFormat": {
                "foregroundColor": {
                    "red": 0.25,
                    "green": 0.25,
                    "blue": 1.0,
                },
                "fontSize": 16,
            }
        })
        return

    @discord.slash_command(name="panda", description="Get info from a PandaBuy link")
    async def panda(
        self,
        ctx,
        url: discord.Option(
            str, description="The PandaBuy link to get info from", required=True)
    ):
        if "pandabuy.page.link" in url:
            real_url = await self.pb.get_real_panda_link(url)
        else:
            real_url = url

        taobao = parse.parse_qs(parse.urlparse(real_url).query)["url"][0]

        info = await self.pb.get_panda_info(taobao)

        if type(info) == str:
            await ctx.respond(info)
            return

        embed = MimicEmbed(
            title=info["data"]["item"]["titleCn"],
            description=f'Sold by {info["data"]["item"]["nick"]}',
            url=url,
            color=discord.Colour.dark_gold(),
            fields=[
                discord.EmbedField(
                    name="Item Price",
                    value=f'¥ {info["data"]["item"]["price"]} |' +
                    f' $ {round(float(info["data"]["item"]["price"]) / 6.5, 2)}',
                    inline=True
                ),
                discord.EmbedField(
                    name="Weight (g)",
                    value=f'{info["data"]["item"]["timeInfo"]["weight"]}g',
                    inline=True
                ),
                discord.EmbedField(
                    name="Sales",
                    value=info["data"]["item"]["total_sold"],
                    inline=True
                )
            ],
            image='https:'+info["data"]["item"]["pic_url"]
        )
        await ctx.respond(embed=embed)
        return


def setup(bot):
    bot.add_cog(Panda(bot))

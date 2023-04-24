import os

import aiohttp


class PandaBuy:

    def __init__(self):
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

    async def get_panda_info(self, url):
        async with self.sess.get(
            f"https://www.pandabuy.com/gateway/order/itemGet?url={url}&userId={os.getenv('PANDABUY_USERID')}"
        ) as resp:
            if resp.status != 200:
                return "Error: Invalid PandaBuy link"
            else:
                return await resp.json()

    async def get_real_panda_link(self, url):
        async with self.sess.get(
            url
        ) as resp:
            if resp.status != 200:
                return "Error: Invalid PandaBuy link"
            else:
                return str(resp.url)

    async def load_qc(self, url):
        async with self.sess.get(
            url
        ) as resp:
            if resp.status != 200:
                return "Error: Invalid QC link"
            else:
                return await resp.read()

    async def upload_qc(self, url):
        r = await self.load_qc(url)
        if type(r) == str:
            return r
        formdata = aiohttp.FormData()
        formdata.add_field("file", r, filename="qc.jpg",
                           content_type="image/jpeg")
        async with aiohttp.ClientSession() as sess:
            async with sess.post(
                "https://lvls.boo/api/upload",
                headers={
                    "Authorization": "uxWSLYNRMr87XImqzZa8frcq.MTY3NzcwODQzMzg5OQ"
                },
                data=formdata,
            ) as resp:
                if resp.status != 200:
                    return f"Error: {resp.status} - {await resp.text()}"
                else:
                    return await resp.json()

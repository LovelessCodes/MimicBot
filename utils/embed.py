from discord import Embed, EmbedField


class MimicEmbed(Embed):

    def __init__(
        self,
        title: str = None,
        description: str = None,
        color: int = 0x36F3F6,
        url: str = None,
        author: str = None,
        footer: str = "BTCReps Team",
        image: str = None,
        thumbnail: str = None,
        icon_url: str = "https://lvls.boo/u/XOpS0B.png",
        fields: list[EmbedField] = []
    ):
        super().__init__(
            title=title,
            description=description,
            url=url,
            color=color,
            fields=fields,
        )
        if author:
            self.set_author(
                name=author,
                icon_url=icon_url
            )
        self.set_footer(
            text=footer,
            icon_url=icon_url
        )
        if image:
            self.set_image(
                url=image
            )
        if thumbnail:
            self.set_thumbnail(
                url=thumbnail
            )
        return

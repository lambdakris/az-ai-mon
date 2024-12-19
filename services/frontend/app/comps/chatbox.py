import mesop as me

@me.component
def chatbox():
    with me.box(
        style=me.Style(
            display="flex",
            width="100%",
            padding=me.Padding.all(2),
            background="white",
        )
    ):
        with me.box(
            style=me.Style(
                flex_grow=1,
            )
        ):
            me.native_textarea(
                autosize=True,
                min_rows=4,
                placeholder="Subtle chat input",
                style=me.Style(
                    width="100%",
                    padding=me.Padding(top=8, left=8),
                    outline="none",
                    overflow_y="auto",
                    border=me.Border.all(
                        me.BorderSide(style="none"),
                    ),
                ),
            )
        with me.content_button(type="icon"):
            me.icon("upload")
        with me.content_button(type="icon"):
            me.icon("send")
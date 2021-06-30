import math
import yaml

import plotly.graph_objs as go


def millify(n):
    millnames = ["", " mil", " mi", " bi"]
    n = float(n)
    millidx = max(
        0,
        min(
            len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))
        ),
    )

    if millnames[millidx] == " mi":
        return "{:.0f}{}".format(n / 10 ** (3 * millidx), millnames[millidx])
    elif millnames[millidx] == " bi":
        return "{:.2f}{}".format(n / 10 ** (3 * millidx), millnames[millidx])


def get_px_values(df, x_col="ano", y_cols=[], color_names=[]):
    x_values = len(y_cols) * df[x_col].tolist()

    lenght = len(df)
    y_values = []
    colors = []
    for col, color in zip(y_cols, color_names):
        y_values += df[col].tolist()
        colors += [color.title() for i in range(lenght)]

    return x_values, y_values, colors


def update_layout(fig):
    themes = yaml.load(open("../../themes/themes.yaml", "r"), Loader=yaml.FullLoader)
    themes = themes["bar"]

    return fig.update_layout(
        hovermode=themes["hovermode"],
        margin=dict(
            l=themes["margin"]["l"],
            r=themes["margin"]["r"],
            t=themes["margin"]["t"],
            b=themes["margin"]["b"],
        ),
        barmode=themes["barmode"],
        autosize=True,
        title_font_family=themes["title"]["family"],
        title_font_color=themes["title"]["color"],
        title=dict(
            x=themes["title"]["position"]["x"],
            y=themes["title"]["position"]["y"],
        ),
        xaxis=dict(
            tickfont=dict(
                size=themes["axis_legend"]["size"],
                color=themes["axis_legend"]["color"],
            ),
            gridcolor=themes["paper_bgcolor"],
            zerolinecolor=themes["axis_legend"]["gridcolor"],
            linecolor=themes["axis_legend"]["gridcolor"],
            # linewidth=2,
            # mirror=True,
            tickformat=themes["axis_legend"]["scale"]["linear"]["x"]["tickformat"],
            type=themes["axis_legend"]["scale"]["linear"]["x"]["type"],
        ),
        yaxis=dict(
            tickfont=dict(
                size=themes["axis_legend"]["size"],
                color=themes["axis_legend"]["color"],
            ),
            gridcolor=themes["axis_legend"]["gridcolor"],
            zerolinecolor=themes["axis_legend"]["gridcolor"],
            # linecolor=themes['axis_legend']['gridcolor'],
            # linewidth=2,
            tickformat=themes["axis_legend"]["scale"]["linear"]["y"]["tickformat"],
            type=themes["axis_legend"]["scale"]["linear"]["y"]["type"],
        ),
        font=dict(
            size=themes["axis_tilte"]["size"], color=themes["axis_tilte"]["color"]
        ),
        legend=go.layout.Legend(
            x=themes["legend"]["position"]["x"],
            y=themes["legend"]["position"]["y"],
            xanchor=themes["legend"]["position"]["xanchor"],
            yanchor=themes["legend"]["position"]["yanchor"],
            traceorder=themes["legend"]["traceorder"],
            orientation=themes["legend"]["orientation"],
            font=dict(
                family=themes["legend"]["family"],
                size=themes["legend"]["size"],
                color=themes["legend"]["color"],
            ),
            bgcolor=themes["legend"]["bgcolor"],
            bordercolor=themes["legend"]["bordercolor"],
            borderwidth=themes["legend"]["borderwidth"],
        ),
        height=themes["altura"],
        width=themes["largura"],
        paper_bgcolor=themes["paper_bgcolor"],
        plot_bgcolor=themes["plot_bgcolor"],
        # annotations=[
        #     dict(
        #         showarrow=False,
        #         text=f"<b>{themes['source']['text']}<b>",
        #         x=themes["source"]["position"]["x"],
        #         y=themes["source"]["position"]["y"],
        #         xref="paper",
        #         yref="paper",
        #         align="left",
        #         # xanchor='right',
        #         xshift=0,
        #         yshift=0,
        #         font=dict(
        #             family=themes["source"]["family"],
        #             size=themes["source"]["size"],
        #             color=themes["source"]["color"],
        #         ),
        #     )
        # ],
    )
import marimo

__generated_with = "0.15.0"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(r"""Hello This is the dashboard!""")
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()

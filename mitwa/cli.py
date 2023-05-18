import typer

cliapp = typer.Typer()


@cliapp.command()
def serve():
    import uvicorn

    from mitwa.web import webapp

    uvicorn.run(webapp, host="localhost", port=8000)


@cliapp.command()
def initdb():
    from mitwa.db import db
    from mitwa.models import Base

    db.create_all(Base.metadata)

from bot.MigranIABot import MigranIABot
import os
import typer  # pip install "typer[all]"
from rich import print  # pip install rich
from rich.table import Table

if __name__ == "__main__":

    botConMigranIA = MigranIABot(os.getenv("OPENAI_API_KEY"))
    

    print("🤖 [bold green]Migracion asistida por ChatGPT[/bold green]")

    working = botConMigranIA.context("Eres un developer senior.")

    while working:
        origin_path =  typer.prompt("\nIngrese ruta de fuentes a migrar :")
        origin_tech =  typer.prompt("\nIngrese tecnologia de Origen  :")
        destiny_tech = typer.prompt("\nIngrese tecnologia de Destino :")
        status = botConMigranIA.migrar(origin_path, origin_tech, destiny_tech)
        if status:
            print("Migracion exitosa")
            working=False
        else:
            print("Error")
            working=True

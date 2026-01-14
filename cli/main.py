import typer

from cli.seed import seed_app
from cli.app_structure import app_structure

# Импорт под-команд
app = typer.Typer(help="CLI управление проектом")

# Регистрируем команды
app.add_typer(seed_app, name="seed")
app.add_typer(app_structure, name="structure")

if __name__ == "__main__":
    app()

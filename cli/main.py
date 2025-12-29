import typer

from cli.seed import seed_app

# Импорт под-команд
app = typer.Typer(help="CLI управление проектом")

# Регистрируем команды
app.add_typer(seed_app, name="seed")

if __name__ == "__main__":
    app()

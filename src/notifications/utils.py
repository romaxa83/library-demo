from src.config import Config

config = Config()

PATH_VERIFY_EMAIL = "auth/verify-email"
PATH_RESET_PASSWORD = "auth/reset-password"

def email_verify_link(token: str)->str:
    # todo здесь должен быть линк на фронт, а уже он в свою очередь перенаправляет на этот линк
    url = config.app.url
    return f"{url}/{PATH_VERIFY_EMAIL}?token={token}"

def reset_password_link(token: str)->str:
    # todo здесь должен быть линк на фронт, а уже он в свою очередь перенаправляет на этот линк
    url = config.app.url
    return f"{url}/{PATH_RESET_PASSWORD}?token={token}"


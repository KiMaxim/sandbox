import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "super_puper_secret_key"

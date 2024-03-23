import os
from pydantic_settings import BaseSettings

def return_full_path(filename: str = ".env") -> str:
    """Uses os to return the correct path of the `.env` file."""
    # Mendapatkan direktori dari skrip saat ini
    script_directory = os.path.dirname(os.path.abspath(__file__))
    # Bergabung dengan path skrip dan nama file
    full_path = os.path.join(script_directory, filename)
    return full_path

class Settings(BaseSettings):
    sheet_id: str
    sheet_transaksi: str
    sheet_produk: str

    class Config:
        # Menggunakan fungsi return_full_path untuk mendapatkan path .env
        env_file = return_full_path(".env")

settings = Settings()

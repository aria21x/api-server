import os

API_PORT = os.getenv('API_PORT', '8000')


if API_PORT == '':
    API_PORT = '8000'
else:
    API_PORT = os.getenv('PORT', API_PORT)

load_dotenv()

class Settings:
    """Dynamic settings loader"""
    def __getattr__(self, name):
        return os.getenv(name)
settings = Settings()

# Use the API_PORT in your application as needed

import yaml

class Config:
    def __init__(self, path: str = 'docker-compose.yaml'):
        with open(path, 'r') as fh:
            config = yaml.safe_load(fh)
            user = config['services']['db']['environment']['POSTGRES_USER']
            pwd = config['services']['db']['environment']['POSTGRES_PASSWORD']
            db = config['services']['db']['environment']['POSTGRES_DB']
            port = config['services']['db']['ports'][0].split(':')[0]
        self.DB_URL = f"postgresql+asyncpg://{user}:{pwd}@localhost:{port}/{db}"

config = Config()

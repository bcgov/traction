import os

class Config(): 
    PSQL_HOST = os.environ.get('POSTGRESQL_HOST')
    PSQL_PORT = os.environ.get('POSTGRESQL_PORT')
    PSQL_USER = os.environ.get('POSTGRESQL_USER')
    PSQL_PASS = os.environ.get('POSTGRESQL_PASSWORD')
    PSQL_DB = os.environ.get('POSTGRESQL_DB')

    SQLALCHEMY_DATABASE_URI = f"postgresql://{PSQL_USER}:{PSQL_PASS}@{PSQL_HOST}:{PSQL_PORT}/{PSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


from xsbs.settings import PluginConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from elixir import metadata

config = PluginConfig('db')
uri = config.getOption('Config', 'uri', 'sqlite:///xsbs.db')
metadata.bind = uri
del config


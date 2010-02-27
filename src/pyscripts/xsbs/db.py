from xsbs.settings import PluginConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from elixir import metadata, setup_all, create_all

config = PluginConfig('db')
uri = config.getOption('Config', 'uri', 'sqlite:///xsbs.db')
metadata.bind = uri
setup_all()
create_all()
del config


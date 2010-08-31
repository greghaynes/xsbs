from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from elixir import metadata, setup_all, create_all
import sbserver
import xsbs.settings

uri = sbserver.dbUri()
metadata.bind = uri
setup_all()
create_all()


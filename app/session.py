from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

from .models import Base

load_dotenv()

engine = create_engine(os.getenv('DB_CONNECTION'), echo=False)
session = Session(engine)
# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

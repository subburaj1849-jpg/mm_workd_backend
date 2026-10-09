from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./mm_works.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class Staff(Base):
    __tablename__ = "staffs"
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(String, unique=True, index=True)
    name = Column(String)
    phone = Column(String)
    role = Column(String)
    pin = Column(String)

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(String, index=True)
    date = Column(String)
    punch_in_time = Column(DateTime)
    punch_in_location = Column(String)
    punch_out_time = Column(DateTime, nullable=True)
    punch_out_location = Column(String, nullable=True)
    work_photo_url = Column(String, nullable=True)
    status = Column(String, default="ON")

Base.metadata.create_all(bind=engine)
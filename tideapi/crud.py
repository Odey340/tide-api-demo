from sqlalchemy.orm import Session
from tideapi import models, schemas

# -------- USER CRUD --------

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=user.password  # Note: hash before saving in production
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# -------- TIDE CRUD --------

def get_tide(db: Session, tide_id: int):
    return db.query(models.Tide).filter(models.Tide.id == tide_id).first()

def get_tides(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Tide).offset(skip).limit(limit).all()

def create_tide(db: Session, tide: schemas.TideCreate):
    db_tide = models.Tide(
        city=tide.city,
        date=tide.date,
        height=tide.height,
    )
    db.add(db_tide)
    db.commit()
    db.refresh(db_tide)
    return db_tide

def get_tides_by_city(db: Session, city: str):
    return db.query(models.Tide).filter(models.Tide.city == city).all()
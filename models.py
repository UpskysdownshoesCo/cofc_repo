from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean,Text
from sqlalchemy.orm import validates

from app import db
class Users(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(200), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    name = Column(String(200))
    company = Column(String(200), unique=True, nullable=False)
    
class SendCertificatesModel(db.Model):
    __tablename__ = 'send_certificates'
    id = Column(Integer, primary_key=True)
    sender = Column(String(200), nullable=True)
    recipient = Column(String(200), nullable=False)
    po_number = Column(String(50), nullable=False)
    batch_number = Column(String(50), nullable=True)
    part_number = Column(String(50), nullable=True)
    assembly_number = Column(String(50), nullable=True)
    manufacturing_country = Column(String(50), nullable=True)
    reach_compliant = Column(Boolean, nullable=True)
    hazardous = Column(Boolean, nullable=True)
    material_expiry_date = Column(String(50), nullable=True)
    additional_notes = Column(Text, nullable=True)

class Restaurant(db.Model):
    __tablename__ = 'restaurant'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    street_address = Column(String(50))
    description = Column(String(250))

    def __str__(self):
        return self.name

class Review(db.Model):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True)
    restaurant = Column(Integer, ForeignKey('restaurant.id', ondelete="CASCADE"))
    user_name = Column(String(30))
    rating = Column(Integer)
    review_text = Column(String(500))
    review_date = Column(DateTime)

    @validates('rating')
    def validate_rating(self, key, value):
        assert value is None or (1 <= value <= 5)
        return value

    def __str__(self):
        return f"{self.user_name}: {self.review_date:%x}"

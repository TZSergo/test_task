from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Building(Base):
    __tablename__ = "buildings"
    id = Column(Integer, primary_key=True)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    organizations = relationship("Organization", back_populates="building")


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    building = relationship("Building", back_populates="organizations")
    phones = relationship("OrganizationPhone", back_populates="organization", cascade="all, delete-orphan")
    activities = relationship("OrganizationActivity", back_populates="organization", cascade="all, delete-orphan")
    @property
    def activity_list(self):
        return [oa.activity for oa in self.activities]

class OrganizationPhone(Base):
    __tablename__ = "organization_phones"
    id = Column(Integer, primary_key=True)
    phone_number = Column(String, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="phones")


class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("activities.id"), nullable=True)
    parent = relationship("Activity", remote_side=[id], backref="children")


class OrganizationActivity(Base):
    __tablename__ = "organization_activities"
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    organization = relationship("Organization", back_populates="activities")
    activity = relationship("Activity")

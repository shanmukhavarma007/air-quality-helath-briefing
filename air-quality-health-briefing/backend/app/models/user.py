import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, DECIMAL, ARRAY, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    health_profile = relationship("HealthProfile", back_populates="user", uselist=False)
    locations = relationship("UserLocation", back_populates="user")
    briefings = relationship("Briefing", back_populates="user")


class HealthProfile(Base):
    __tablename__ = "health_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    age_bracket = Column(String(20), default="adult")
    conditions = Column(ARRAY(Text), default={})
    activity_level = Column(String(20), default="moderate")
    briefing_time = Column(String(10), default="07:00")
    timezone = Column(String(60), default="UTC")
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("User", back_populates="health_profile")


class UserLocation(Base):
    __tablename__ = "user_locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    label = Column(String(100), nullable=False)
    latitude = Column(DECIMAL(9, 6), nullable=False)
    longitude = Column(DECIMAL(9, 6), nullable=False)
    address = Column(String(255), nullable=True)
    openaq_location_id = Column(Integer, nullable=True)
    is_primary = Column(Boolean, default=False)
    alert_threshold = Column(Integer, default=150)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("User", back_populates="locations")


class AQIReading(Base):
    __tablename__ = "aqi_readings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    openaq_location_id = Column(Integer, nullable=False)
    parameter = Column(String(20), nullable=False)
    value = Column(DECIMAL(10, 2), nullable=False)
    unit = Column(String(20), nullable=False)
    aqi_value = Column(Integer, nullable=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    fetched_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("idx_aqi_readings_location_time", "openaq_location_id", "recorded_at"),
    )


class Briefing(Base):
    __tablename__ = "briefings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    location_id = Column(UUID(as_uuid=True), ForeignKey("user_locations.id", ondelete="SET NULL"))
    aqi_at_generation = Column(Integer, nullable=True)
    outdoor_safety = Column(String(20), nullable=True)
    brief_text = Column(Text, nullable=False)
    brief_metadata = Column(JSONB, nullable=True)
    model_used = Column(String(100), nullable=True)
    is_cached_result = Column(Boolean, default=False)
    generated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    delivered_email = Column(Boolean, default=False)
    delivered_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="briefings")


class EmailVerification(Base):
    __tablename__ = "email_verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)


class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(100), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

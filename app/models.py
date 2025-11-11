from __future__ import annotations

from datetime import datetime, date, time
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    dob = db.Column(db.Date)
    journey_completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    reminders = db.relationship(
        "Reminder",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    projects = db.relationship(
        "Project",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    health_stats = db.relationship(
        "HealthStat",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    health_logs = db.relationship(
        "HealthLog",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    energy_logs = db.relationship(
        "EnergyLog",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(140), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    detail = db.Column(db.Text)
    due_date = db.Column(db.Date, nullable=False)
    due_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "detail": self.detail or "",
            "due_date": self.due_date.isoformat() if isinstance(self.due_date, date) else "",
            "due_time": self.due_time.strftime("%H:%M") if isinstance(self.due_time, time) else "",
        }


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(160), nullable=False)
    installer = db.Column(db.String(160))
    detail = db.Column(db.Text)
    system_type = db.Column(db.String(80))
    installation_date = db.Column(db.Date)
    image_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class HealthStat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    label = db.Column(db.String(120), nullable=False)
    value = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class HealthLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    note = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class EnergyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    entry_type = db.Column(db.String(40), nullable=False)
    kwh = db.Column(db.Numeric(10, 2), nullable=False)
    revenue = db.Column(db.Numeric(12, 2))
    panel_id = db.Column(db.String(120))
    date = db.Column(db.Date, nullable=False)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


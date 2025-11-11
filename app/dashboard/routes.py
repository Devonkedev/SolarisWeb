from __future__ import annotations

from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Project, EnergyLog

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.before_request
def require_journey():
    if not current_user.is_authenticated:
        return
    if not current_user.journey_completed:
        return redirect(url_for("subsidy.eligibility"))


@dashboard_bp.route("/", methods=["GET"])
@login_required
def index():
    recent_projects = (
        Project.query.filter_by(user_id=current_user.id)
        .order_by(Project.created_at.desc())
        .limit(3)
        .all()
    )
    total_generation = (
        EnergyLog.query.filter_by(user_id=current_user.id, entry_type="generation")
        .with_entities(db.func.coalesce(db.func.sum(EnergyLog.kwh), 0))
        .scalar()
    )
    recent_energy = (
        EnergyLog.query.filter_by(user_id=current_user.id)
        .order_by(EnergyLog.date.desc(), EnergyLog.created_at.desc())
        .limit(3)
        .all()
    )

    return render_template(
        "dashboard/index.html",
        title="Dashboard",
        recent_projects=recent_projects,
        total_generation=total_generation,
        recent_energy=recent_energy,
        show_tracker_cta=True,
    )


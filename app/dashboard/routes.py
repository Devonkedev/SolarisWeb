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

    estimate_summary = {
        "system_kw": current_user.last_system_kw,
        "net_cost": current_user.last_net_cost_inr,
        "savings": current_user.last_estimated_savings_inr,
        "updated_at": current_user.last_estimate_updated_at,
    }
    estimate_stats = None
    if estimate_summary["system_kw"]:
        estimate_stats = {
            "monthly_savings": 8200,
            "lifetime_savings": 152000,
            "co2_offset": 1.8,
        }

    return render_template(
        "dashboard/index.html",
        title="Dashboard",
        recent_projects=recent_projects,
        total_generation=total_generation,
        recent_energy=recent_energy,
        estimate_summary=estimate_summary,
        estimate_stats=estimate_stats,
        show_tracker_cta=True,
    )


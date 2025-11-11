from __future__ import annotations

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from datetime import date

from ..extensions import db
from ..forms import TrackerEntryForm
from ..models import EnergyLog

tracker_bp = Blueprint("tracker", __name__, url_prefix="/tracker")


@tracker_bp.before_request
def require_journey():
    if not current_user.is_authenticated:
        return
    if not current_user.journey_completed:
        return redirect(url_for("subsidy.eligibility"))


@tracker_bp.route("/", methods=["GET"])
@login_required
def index():
    logs = (
        EnergyLog.query.filter_by(user_id=current_user.id)
        .order_by(EnergyLog.date.desc(), EnergyLog.created_at.desc())
        .all()
    )
    total_generation = sum(log.kwh for log in logs if log.entry_type == "generation")
    total_export = sum(log.kwh for log in logs if log.entry_type == "export")
    total_revenue = sum((log.revenue or 0) for log in logs)
    return render_template(
        "tracker/index.html",
        title="Energy Tracker",
        logs=logs,
        total_generation=total_generation,
        total_export=total_export,
        total_revenue=total_revenue,
    )


@tracker_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_entry():
    form = TrackerEntryForm()
    if not form.date.data:
        form.date.data = date.today()
    if form.validate_on_submit():
        log = EnergyLog(
            user_id=current_user.id,
            entry_type=form.entry_type.data,
            kwh=form.kwh.data,
            revenue=form.revenue.data,
            panel_id=form.panel_id.data or None,
            date=form.date.data,
            note=form.note.data,
        )
        db.session.add(log)
        db.session.commit()
        flash("Tracker entry saved!", "success")
        return redirect(url_for("tracker.index"))
    return render_template(
        "tracker/add.html",
        title="Add Tracker Entry",
        form=form,
    )

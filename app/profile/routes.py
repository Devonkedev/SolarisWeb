from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..forms import HealthLogForm, HealthStatForm, ProfileForm
from ..models import HealthLog, HealthStat

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.before_request
def require_journey():
    if not current_user.is_authenticated:
        return
    if not current_user.journey_completed:
        return redirect(url_for("subsidy.eligibility"))


@profile_bp.route("/", methods=["GET"])
@login_required
def view_profile():
    stats = (
        HealthStat.query.filter_by(user_id=current_user.id)
        .order_by(HealthStat.created_at.desc())
        .all()
    )
    logs = (
        HealthLog.query.filter_by(user_id=current_user.id)
        .order_by(HealthLog.created_at.desc())
        .all()
    )
    stat_form = HealthStatForm()
    log_form = HealthLogForm()
    return render_template(
        "profile/view.html",
        title="Profile",
        stats=stats,
        logs=logs,
        stat_form=stat_form,
        log_form=log_form,
    )


@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data.lower().strip()
        current_user.phone = form.phone.data
        current_user.dob = form.dob.data
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile.view_profile"))

    return render_template("profile/edit.html", title="Edit Profile", form=form)


@profile_bp.route("/health/stat", methods=["POST"])
@login_required
def add_health_stat():
    form = HealthStatForm()
    if form.validate_on_submit():
        stat = HealthStat(
            user_id=current_user.id,
            label=form.label.data.strip(),
            value=form.value.data.strip(),
        )
        db.session.add(stat)
        db.session.commit()
        flash("Health metric saved.", "success")
    else:
        flash("Please correct the health metric form.", "error")
    return redirect(url_for("profile.view_profile"))


@profile_bp.route("/health/log", methods=["POST"])
@login_required
def add_health_log():
    form = HealthLogForm()
    if form.validate_on_submit():
        log = HealthLog(user_id=current_user.id, note=form.note.data.strip())
        db.session.add(log)
        db.session.commit()
        flash("Health note recorded.", "success")
    else:
        flash("Please correct the health log form.", "error")
    return redirect(url_for("profile.view_profile"))


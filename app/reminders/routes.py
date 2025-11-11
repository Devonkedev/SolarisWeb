from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..forms import ReminderForm
from ..models import Reminder

reminders_bp = Blueprint("reminders", __name__, url_prefix="/reminders")


@reminders_bp.before_request
def require_journey():
    if not current_user.is_authenticated:
        return
    if not current_user.journey_completed:
        return redirect(url_for("subsidy.eligibility"))


@reminders_bp.route("/", methods=["GET", "POST"])
@login_required
def list_reminders():
    form = ReminderForm()
    reminders = (
        Reminder.query.filter_by(user_id=current_user.id)
        .order_by(Reminder.due_date, Reminder.due_time)
        .all()
    )

    if form.validate_on_submit():
        reminder = Reminder(
            user_id=current_user.id,
            name=form.name.data.strip(),
            category=form.category.data,
            detail=form.detail.data.strip() if form.detail.data else None,
            due_date=form.due_date.data,
            due_time=form.due_time.data,
        )
        db.session.add(reminder)
        db.session.commit()
        flash("Reminder saved and scheduled.", "success")
        return redirect(url_for("reminders.list_reminders"))

    return render_template(
        "reminders/index.html",
        title="Reminders",
        reminders=reminders,
        form=form,
    )


@reminders_bp.route("/<int:reminder_id>/delete", methods=["POST"])
@login_required
def delete_reminder(reminder_id: int):
    reminder = Reminder.query.filter_by(id=reminder_id, user_id=current_user.id).first()
    if not reminder:
        flash("Reminder not found.", "error")
    else:
        db.session.delete(reminder)
        db.session.commit()
        flash("Reminder removed.", "success")
    return redirect(url_for("reminders.list_reminders"))


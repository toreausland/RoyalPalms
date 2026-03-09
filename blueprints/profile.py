from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from forms import ProfileForm, ChangePasswordForm

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def edit():
    form = ProfileForm(obj=current_user)
    pw_form = ChangePasswordForm()

    if form.validate_on_submit() and 'submit' in request.form:
        current_user.name = form.name.data.strip()
        current_user.apartment = form.apartment.data.strip()
        current_user.phase = form.phase.data
        current_user.phone = form.phone.data.strip() if form.phone.data else None
        db.session.commit()
        flash('Profilen er oppdatert.', 'success')
        return redirect(url_for('profile.edit'))

    return render_template('profile/edit.html', form=form, pw_form=pw_form)


@profile_bp.route('/endre-passord', methods=['POST'])
@login_required
def change_password():
    pw_form = ChangePasswordForm()
    if pw_form.validate_on_submit():
        if not current_user.check_password(pw_form.current_password.data):
            flash('Nåværende passord er feil.', 'danger')
            return redirect(url_for('profile.edit'))
        current_user.set_password(pw_form.new_password.data)
        db.session.commit()
        flash('Passordet er endret.', 'success')
    else:
        flash('Feil ved passordendring. Sjekk at alle felter er fylt ut korrekt.', 'danger')
    return redirect(url_for('profile.edit'))

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from models import db, User, ActivityLog
from forms import RegistrationForm, LoginForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/registrer', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        existing = User.query.filter_by(email=email).first()

        if existing and existing.has_registered:
            # Allerede fullført registrering — kan ikke registrere på nytt
            flash('Denne e-postadressen er allerede registrert. Bruk innlogging.', 'danger')
            return render_template('auth/register.html', form=form)

        if existing and not existing.has_registered:
            # Pre-opprettet bruker fra invitasjonslisten — fullfør registreringen
            existing.name = form.name.data.strip()
            existing.apartment = form.apartment.data.strip()
            existing.phase = form.phase.data
            existing.phone = form.phone.data.strip() if form.phone.data else None
            existing.set_password(form.password.data)
            existing.is_approved = True  # Inviterte brukere godkjennes automatisk
            user = existing
        else:
            # Helt ny bruker (ikke på listen) — må godkjennes av admin
            user = User(
                name=form.name.data.strip(),
                email=email,
                apartment=form.apartment.data.strip(),
                phase=form.phase.data,
                phone=form.phone.data.strip() if form.phone.data else None,
                is_approved=False,
            )
            user.set_password(form.password.data)
            db.session.add(user)

        log = ActivityLog(
            action='registrering',
            description=f'{user.name} registrerte seg ({user.apartment}, {user.phase})',
            user=user,
        )
        db.session.add(log)
        db.session.commit()

        if user.is_approved:
            flash('Registreringen var vellykket! Du kan nå logge inn.', 'success')
        else:
            flash(
                'Registreringen er mottatt! En administrator må godkjenne kontoen din '
                'før du kan logge inn. Du vil få tilgang så snart dette er gjort.',
                'info',
            )
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/logg-inn', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()

        if user and not user.has_registered:
            # Bruker finnes men har ikke fullført registrering
            flash('Du må fullføre registreringen først. Klikk "Registrer deg" nedenfor.', 'warning')
            return render_template('auth/login.html', form=form)

        if user and user.check_password(form.password.data):
            if not user.is_approved:
                flash(
                    'Kontoen din venter på godkjenning fra en administrator. '
                    'Du vil få tilgang så snart registreringen er godkjent.',
                    'warning',
                )
                return render_template('auth/login.html', form=form)

            login_user(user)
            next_page = request.args.get('next')
            flash(f'Velkommen, {user.name}!', 'success')
            return redirect(next_page or url_for('main.dashboard'))

        flash('Feil e-post eller passord.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logg-ut')
def logout():
    logout_user()
    flash('Du er nå logget ut.', 'info')
    return redirect(url_for('main.index'))

import csv
import io
import os
import shutil
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, Response, request, send_file, current_app
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Topic, Comment, Document, ActivityLog
from forms import TopicForm, AdminMemberForm

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Du har ikke tilgang til denne siden.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@login_required
@admin_required
def panel():
    total_members = User.query.count()
    total_topics = Topic.query.count()
    total_documents = Document.query.count()
    pending_approvals = User.query.filter_by(is_approved=False).filter(
        User.password_hash.isnot(None)
    ).all()
    topics = Topic.query.order_by(Topic.sort_order.asc()).all()
    recent_activity = ActivityLog.query.order_by(
        ActivityLog.created_at.desc()
    ).limit(20).all()
    return render_template(
        'admin/panel.html',
        total_members=total_members,
        total_topics=total_topics,
        total_documents=total_documents,
        pending_approvals=pending_approvals,
        topics=topics,
        recent_activity=recent_activity,
    )


@admin_bp.route('/medlemmer')
@login_required
@admin_required
def members():
    users = User.query.order_by(User.phase.asc(), User.apartment.asc()).all()
    return render_template('admin/members.html', users=users)


@admin_bp.route('/medlemmer/eksport')
@login_required
@admin_required
def export_members():
    users = User.query.order_by(User.phase.asc(), User.apartment.asc()).all()
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(['Navn', 'E-post', 'Leilighet', 'Fase', 'Telefon', 'Registrert'])
    for u in users:
        writer.writerow([
            u.name, u.email, u.apartment, u.phase,
            u.phone or '', u.created_at.strftime('%d.%m.%Y')
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=medlemmer_royal_palms.csv'}
    )


@admin_bp.route('/medlem/<int:user_id>/rediger', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_member(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminMemberForm(obj=user)

    if form.validate_on_submit():
        # Sjekk at e-post ikke kolliderer med annen bruker
        if form.email.data.lower().strip() != user.email:
            existing = User.query.filter_by(email=form.email.data.lower().strip()).first()
            if existing:
                flash('E-postadressen er allerede i bruk av en annen bruker.', 'danger')
                return render_template('admin/edit_member.html', form=form, member=user)

        user.name = form.name.data.strip()
        user.email = form.email.data.lower().strip()
        user.apartment = form.apartment.data.strip() if form.apartment.data else ''
        user.phase = form.phase.data
        user.phone = form.phone.data.strip() if form.phone.data else None
        user.is_admin = form.is_admin.data

        # Sett nytt passord hvis angitt
        if form.reset_password.data:
            user.set_password(form.reset_password.data)

        log = ActivityLog(
            action='rediger_medlem',
            description=f'{current_user.name} redigerte profilen til {user.name}',
            user_id=current_user.id,
        )
        db.session.add(log)
        db.session.commit()

        flash(f'Profilen til {user.name} er oppdatert.', 'success')
        return redirect(url_for('admin.members'))

    return render_template('admin/edit_member.html', form=form, member=user)


@admin_bp.route('/medlem/<int:user_id>/slett', methods=['POST'])
@login_required
@admin_required
def delete_member(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('Du kan ikke slette din egen konto.', 'danger')
        return redirect(url_for('admin.members'))

    name = user.name
    # Slett relaterte data
    Comment.query.filter_by(user_id=user.id).delete()
    ActivityLog.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)

    log = ActivityLog(
        action='slett_medlem',
        description=f'{current_user.name} slettet brukeren {name}',
        user_id=current_user.id,
    )
    db.session.add(log)
    db.session.commit()

    flash(f'{name} er fjernet fra kjøpergruppen.', 'info')
    return redirect(url_for('admin.members'))


@admin_bp.route('/medlem/<int:user_id>/godkjenn', methods=['POST'])
@login_required
@admin_required
def approve_member(user_id):
    user = User.query.get_or_404(user_id)
    user.is_approved = True

    log = ActivityLog(
        action='godkjenn_medlem',
        description=f'{current_user.name} godkjente registreringen til {user.name}',
        user_id=current_user.id,
    )
    db.session.add(log)
    db.session.commit()

    flash(f'{user.name} er godkjent og kan nå logge inn.', 'success')
    return redirect(url_for('admin.panel'))


@admin_bp.route('/medlem/<int:user_id>/avvis', methods=['POST'])
@login_required
@admin_required
def reject_member(user_id):
    user = User.query.get_or_404(user_id)
    name = user.name

    # Slett bruker og relaterte data
    Comment.query.filter_by(user_id=user.id).delete()
    ActivityLog.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)

    log = ActivityLog(
        action='avvis_medlem',
        description=f'{current_user.name} avslo registreringen til {name}',
        user_id=current_user.id,
    )
    db.session.add(log)
    db.session.commit()

    flash(f'Registreringen til {name} er avvist og kontoen fjernet.', 'info')
    return redirect(url_for('admin.panel'))


@admin_bp.route('/backup')
@login_required
@admin_required
def download_backup():
    """Last ned backup av databasen som .db-fil."""
    db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
    if not db_uri.startswith('sqlite:///'):
        flash('Backup støttes kun for SQLite-databaser.', 'danger')
        return redirect(url_for('admin.panel'))

    db_path = db_uri.replace('sqlite:///', '')
    if not os.path.exists(db_path):
        flash('Databasefilen ble ikke funnet.', 'danger')
        return redirect(url_for('admin.panel'))

    # Kopier til temp-fil for trygg nedlasting
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'royal_palms_backup_{timestamp}.db'
    backup_path = os.path.join(os.path.dirname(db_path), backup_filename)
    shutil.copy2(db_path, backup_path)

    log = ActivityLog(
        action='backup',
        description=f'{current_user.name} lastet ned database-backup',
        user_id=current_user.id,
    )
    db.session.add(log)
    db.session.commit()

    response = send_file(
        backup_path,
        as_attachment=True,
        download_name=backup_filename,
    )

    # Slett temp-filen etter sending
    @response.call_on_close
    def cleanup():
        if os.path.exists(backup_path):
            os.remove(backup_path)

    return response


@admin_bp.route('/tema/nytt', methods=['GET', 'POST'])
@login_required
@admin_required
def create_topic():
    form = TopicForm()
    if form.validate_on_submit():
        max_order = db.session.query(db.func.max(Topic.sort_order)).scalar() or 0
        topic = Topic(
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            status=form.status.data,
            sort_order=max_order + 1,
            created_by_id=current_user.id,
        )
        db.session.add(topic)

        log = ActivityLog(
            action='nytt_tema',
            description=f'{current_user.name} opprettet tema «{topic.title[:60]}»',
            user_id=current_user.id,
            topic_id=topic.id,
        )
        db.session.add(log)
        db.session.commit()

        flash('Nytt tema opprettet.', 'success')
        return redirect(url_for('admin.panel'))
    return render_template('admin/topic_form.html', form=form, editing=False)


@admin_bp.route('/tema/<int:topic_id>/rediger', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    form = TopicForm(obj=topic)
    if form.validate_on_submit():
        topic.title = form.title.data.strip()
        topic.description = form.description.data.strip()
        topic.status = form.status.data

        log = ActivityLog(
            action='rediger_tema',
            description=f'{current_user.name} redigerte tema «{topic.title[:60]}»',
            user_id=current_user.id,
            topic_id=topic.id,
        )
        db.session.add(log)
        db.session.commit()

        flash('Tema oppdatert.', 'success')
        return redirect(url_for('admin.panel'))
    return render_template('admin/topic_form.html', form=form, editing=True, topic=topic)


@admin_bp.route('/tema/<int:topic_id>/slett', methods=['POST'])
@login_required
@admin_required
def delete_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    Comment.query.filter_by(topic_id=topic.id).delete()
    ActivityLog.query.filter_by(topic_id=topic.id).delete()
    db.session.delete(topic)
    db.session.commit()
    flash('Tema slettet.', 'info')
    return redirect(url_for('admin.panel'))

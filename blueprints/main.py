from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import User, Topic, ActivityLog

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@main_bp.route('/oversikt')
@login_required
def dashboard():
    total_members = User.query.count()
    total_topics = Topic.query.count()
    active_topics = Topic.query.filter(
        Topic.status.in_(['under_diskusjon', 'sendt_til_advokat'])
    ).count()
    topics = Topic.query.order_by(Topic.sort_order.asc()).all()
    members = User.query.order_by(User.phase.asc(), User.apartment.asc()).all()
    recent_activity = ActivityLog.query.order_by(
        ActivityLog.created_at.desc()
    ).limit(10).all()

    return render_template(
        'main/dashboard.html',
        total_members=total_members,
        total_topics=total_topics,
        active_topics=active_topics,
        topics=topics,
        members=members,
        recent_activity=recent_activity,
    )

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Topic, Comment, ActivityLog
from forms import CommentForm

topics_bp = Blueprint('topics', __name__)


@topics_bp.route('/')
@login_required
def list_topics():
    active_topics = Topic.query.filter(
        Topic.status != 'arkivert'
    ).order_by(Topic.sort_order.asc()).all()
    archived_topics = Topic.query.filter_by(
        status='arkivert'
    ).order_by(Topic.sort_order.asc()).all()
    return render_template(
        'topics/list.html',
        active_topics=active_topics,
        archived_topics=archived_topics,
    )


@topics_bp.route('/<int:topic_id>', methods=['GET', 'POST'])
@login_required
def detail(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data.strip(),
            topic_id=topic.id,
            user_id=current_user.id,
        )
        db.session.add(comment)

        log = ActivityLog(
            action='kommentar',
            description=f'{current_user.name} kommenterte på «{topic.title[:60]}»',
            user_id=current_user.id,
            topic_id=topic.id,
        )
        db.session.add(log)
        db.session.commit()

        flash('Kommentaren ble lagt til.', 'success')
        return redirect(url_for('topics.detail', topic_id=topic.id) + '#kommentarer')

    comments = topic.comments.all()
    return render_template('topics/detail.html', topic=topic, comments=comments, form=form)

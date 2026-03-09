import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Document, ActivityLog

documents_bp = Blueprint('documents', __name__)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@documents_bp.route('/')
@login_required
def list_documents():
    docs = Document.query.order_by(Document.created_at.desc()).all()
    return render_template('documents/list.html', documents=docs)


@documents_bp.route('/last-opp', methods=['GET', 'POST'])
@login_required
def upload():
    if not current_user.is_admin:
        flash('Kun admin kan laste opp dokumenter.', 'danger')
        return redirect(url_for('documents.list_documents'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        file = request.files.get('file')

        if not title:
            flash('Tittel er påkrevd.', 'danger')
            return render_template('documents/upload.html')

        if not file or file.filename == '':
            flash('Velg en fil å laste opp.', 'danger')
            return render_template('documents/upload.html')

        if not allowed_file(file.filename):
            flash('Filtypen er ikke tillatt.', 'danger')
            return render_template('documents/upload.html')

        original = secure_filename(file.filename)
        ext = original.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name))

        doc = Document(
            title=title,
            description=description or None,
            filename=unique_name,
            original_filename=original,
            uploaded_by_id=current_user.id,
        )
        db.session.add(doc)

        log = ActivityLog(
            action='dokument',
            description=f'{current_user.name} lastet opp «{title}»',
            user_id=current_user.id,
        )
        db.session.add(log)
        db.session.commit()

        flash('Dokument lastet opp.', 'success')
        return redirect(url_for('documents.list_documents'))

    return render_template('documents/upload.html')


@documents_bp.route('/last-ned/<int:doc_id>')
@login_required
def download(doc_id):
    doc = Document.query.get_or_404(doc_id)
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        doc.filename,
        as_attachment=True,
        download_name=doc.original_filename,
    )

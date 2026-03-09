from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

PHASE_CHOICES = [
    ('Fase 1', 'Fase 1'),
    ('Fase 2', 'Fase 2'),
    ('Fase 3', 'Fase 3'),
]

STATUS_CHOICES = [
    ('under_diskusjon', 'Under diskusjon'),
    ('sendt_til_advokat', 'Sendt til advokat'),
    ('avklart', 'Avklart'),
    ('avsluttet', 'Avsluttet'),
    ('arkivert', 'Arkivert'),
]


class RegistrationForm(FlaskForm):
    name = StringField('Navn', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('E-post', validators=[DataRequired(), Email()])
    password = PasswordField('Passord', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Bekreft passord', validators=[DataRequired(), EqualTo('password', message='Passordene må være like')])
    apartment = StringField('Leilighet (f.eks. Tiger Palm A1)', validators=[DataRequired(), Length(max=50)])
    phase = SelectField('Fase', choices=PHASE_CHOICES, validators=[DataRequired()])
    phone = StringField('Telefon (valgfritt)', validators=[Optional(), Length(max=30)])
    submit = SubmitField('Registrer deg')


class LoginForm(FlaskForm):
    email = StringField('E-post', validators=[DataRequired(), Email()])
    password = PasswordField('Passord', validators=[DataRequired()])
    submit = SubmitField('Logg inn')


class ProfileForm(FlaskForm):
    name = StringField('Navn', validators=[DataRequired(), Length(min=2, max=120)])
    apartment = StringField('Leilighet', validators=[DataRequired(), Length(max=50)])
    phase = SelectField('Fase', choices=PHASE_CHOICES, validators=[DataRequired()])
    phone = StringField('Telefon', validators=[Optional(), Length(max=30)])
    submit = SubmitField('Lagre endringer')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Nåværende passord', validators=[DataRequired()])
    new_password = PasswordField('Nytt passord', validators=[DataRequired(), Length(min=8)])
    new_password2 = PasswordField('Bekreft nytt passord', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Endre passord')


class TopicForm(FlaskForm):
    title = StringField('Tittel', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Beskrivelse', validators=[DataRequired()])
    status = SelectField('Status', choices=STATUS_CHOICES, validators=[DataRequired()])
    submit = SubmitField('Lagre')


class AdminMemberForm(FlaskForm):
    name = StringField('Navn', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('E-post', validators=[DataRequired(), Email()])
    apartment = StringField('Leilighet', validators=[Optional(), Length(max=50)])
    phase = SelectField('Fase', choices=PHASE_CHOICES, validators=[DataRequired()])
    phone = StringField('Telefon', validators=[Optional(), Length(max=30)])
    is_admin = BooleanField('Administrator')
    reset_password = PasswordField('Sett nytt passord (la stå tomt for å beholde)', validators=[Optional(), Length(min=8)])
    submit = SubmitField('Lagre endringer')


class CommentForm(FlaskForm):
    body = TextAreaField('Din kommentar', validators=[DataRequired(), Length(min=1, max=5000)])
    submit = SubmitField('Legg til kommentar')

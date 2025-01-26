"""contact form app."""

import decouple
import flask
import flask_cors
import flask_wtf
import sendgrid
import sendgrid.helpers.mail
import wtforms
import wtforms.csrf.core
import uuid

_secret_key = decouple.config("SECRET_KEY")
_sendgrid_api_key = decouple.config("SENDGRID_API_KEY", default=None)
_sendgrid_sender_address = decouple.config("SENDGRID_SENDER_ADDRESS", default=None)
_sendgrid_contact_address = decouple.config("SENDGRID_CONTACT_ADDRESS", default=None)
if _sendgrid_api_key is None:
    print("SENDGRID_API_KEY not found in .env file. Email will not be sent.")
if _sendgrid_api_key and not _sendgrid_sender_address:
    raise ValueError("SENDGRID_SENDER_ADDRESS must be set if SENDGRID_API_KEY is set.")

app = flask.Flask(__name__)
app.secret_key = _secret_key
app.config["WTF_CSRF_ENABLED"] = False
csrf = wtforms.csrf.core.CSRF()
cors = flask_cors.CORS(app)

class _ContactForm(flask_wtf.FlaskForm):
    name = wtforms.StringField(
        "Your Name",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=2, max=50),
        ],
    )
    email = wtforms.StringField(
        "Email you would like to be contacted at",
        validators=[wtforms.validators.DataRequired(), wtforms.validators.Email()],
    )
    message = wtforms.TextAreaField(
        "Message",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=5, max=500),
        ],
    )


def _send_email(name, email, message):
    if not _sendgrid_api_key:
        print("SENDGRID_API_KEY not found in .env file. Email will not be sent.")
        print("testing mode, not sending:", name, email, message)
        return "TEST_VALID" in message

    sg = sendgrid.SendGridAPIClient(api_key=_sendgrid_api_key)
    message = sendgrid.helpers.mail.Mail(
        from_email=sendgrid.helpers.mail.Email(
            _sendgrid_sender_address, f"{name} via contact form"
        ),
        subject=f"New message from {name} via the contact form - Message ID {uuid.uuid4().hex[:8]}",
        to_emails=_sendgrid_contact_address,
        plain_text_content=f"Message form {name}\n\n{message}",
    )
    message.reply_to=sendgrid.helpers.mail.Email(email, name)
    try:
        sg = sendgrid.SendGridAPIClient(api_key=_sendgrid_api_key)
        response = sg.send(message)
        print("Email sent, response code:", response.status_code)
    except Exception as e:
        print(e)
        return False
    
    return True


@app.route("/", methods=["GET", "POST"])
def _contact():
    form = _ContactForm()
    if form.is_submitted():
        if form.validate():
            name = form.name.data
            email = form.email.data
            message = form.message.data

            if _send_email(name, email, message):
                return flask.render_template(
                    "result.html", result="Thank you for submitting your message!"
                )
            flask.flash(
                "We're sorry, but there was an error sending your message."
                " Please try again later."
            )
        else:
            print("Form is not valid")
            print(flask.request.form)
            print(form.errors)
            flask.flash("There was an error with your submission. Please try again.")
    return flask.render_template("contact.html", form=form)

"""contact form app."""

import fnmatch
import uuid

import flask
import flask_wtf
import sendgrid
import sendgrid.helpers.mail
import wtforms

from contact_form import _config

_secret_key = _config.secret_key
_sendgrid_api_key = _config.sendgrid_api_key

app = flask.Flask(__name__)
app.secret_key = _secret_key
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "None"


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


def _send_email(name, email, message, domain):
    if not _sendgrid_api_key:
        print("SENDGRID_API_KEY not configured. Email will not be sent.")
        print("testing mode, not sending:", name, email, message)
        return "TEST_VALID" in message

    for config in _config.domains:
        if not fnmatch.fnmatch(domain, config.pattern):
            continue

        sg = sendgrid.SendGridAPIClient(api_key=_sendgrid_api_key)
        message = sendgrid.helpers.mail.Mail(
            from_email=sendgrid.helpers.mail.Email(
                config.sender_address, f"{name} via contact form"
            ),
            subject=(
                f"New message from {name} via the contact form "
                f"- Message ID {uuid.uuid4().hex[:8]}"
            ),
            to_emails=config.recipient_address,
            plain_text_content=f"Message form {name}\n\n{message}",
        )
        message.reply_to = sendgrid.helpers.mail.Email(email, name)
        try:
            sg = sendgrid.SendGridAPIClient(api_key=_sendgrid_api_key)
            response = sg.send(message)
            print("Email sent, response code:", response.status_code)
        except Exception as e:
            print(e)
            return False
        return True
    else:
        print(
            f"No config domain matched {domain}."
            f" Tried: {', '.join([i.pattern for i in _config.domains])}"
        )
        return False


@app.route("/", methods=["GET", "POST"])
def _contact():
    form = _ContactForm()
    if form.is_submitted():
        if form.validate():
            domain = flask.request.host
            name = form.name.data
            email = form.email.data
            message = form.message.data

            if _send_email(name, email, message, domain):
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

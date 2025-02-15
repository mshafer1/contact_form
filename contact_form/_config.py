import decouple as _decouple

secret_key: str = _decouple.config("SECRET_KEY")
sendgrid_api_key: str = _decouple.config("SENDGRID_API_KEY", default=None)
sendgrid_sender_address: str = _decouple.config("SENDGRID_SENDER_ADDRESS", default=None)
contact_address: str = _decouple.config("SENDGRID_CONTACT_ADDRESS", default=None)
if sendgrid_api_key is None:
    print("SENDGRID_API_KEY not found in .env file. Email will not be sent.")
if sendgrid_api_key and not sendgrid_sender_address:
    raise ValueError("SENDGRID_SENDER_ADDRESS must be set if SENDGRID_API_KEY is set.")

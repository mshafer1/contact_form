import fnmatch as _fnmatch
import pathlib as _pathlib
import typing as _typing

import decouple as _decouple
import yaml as _yaml


class DomainConfig(_typing.NamedTuple):
    """Type definition for per-domain config."""

    pattern: str
    """Domain is considered a match if fnmatch.fnmatch(domain, pattern)."""

    sender_address: str
    """Address this domain should send as."""

    recipient_address: str
    """Address this domain should send to."""


_config_dir: _typing.Optional[_pathlib.Path] = _decouple.config(
    "CONFIG_DIR", default=_pathlib.Path(__file__).parent, cast=_pathlib.Path
)

_config_file: _typing.Optional[_pathlib.Path] = (
    None if _config_dir is None else (_config_dir / ".config.yaml")
)
_config: _typing.Optional[_typing.Dict[str, dict]] = None
if _config_file and _config_file.is_file():
    _config = _yaml.load(_config_file.read_text(), Loader=_yaml.CSafeLoader)

secret_key: str = _decouple.config("SECRET_KEY")
sendgrid_api_key: str = _decouple.config("SENDGRID_API_KEY", default=None)
if sendgrid_api_key is None:
    print("SENDGRID_API_KEY not found in env or .env file. Email will not be sent.")

if _config is None:
    _sendgrid_sender_address: str = _decouple.config("SENDGRID_SENDER_ADDRESS", default=None)
    _contact_address: str = _decouple.config("SENDGRID_CONTACT_ADDRESS", default=None)
    if sendgrid_api_key and not _sendgrid_sender_address:
        raise ValueError("SENDGRID_SENDER_ADDRESS must be set if SENDGRID_API_KEY is set.")
    domains = [
        DomainConfig(
            "*", sender_address=_sendgrid_sender_address, recipient_address=_contact_address
        )
    ]
else:
    domains = [DomainConfig(**v) for v in _config]

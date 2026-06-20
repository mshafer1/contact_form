"""Run dev server."""

import contact_form

if __name__ == "__main__":
    app = contact_form.app

    app.run(debug=contact_form._config.DEBUG_MODE, host="0.0.0.0")

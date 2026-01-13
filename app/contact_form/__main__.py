"""Run dev server."""

import contact_form

if __name__ == "__main__":
    app = contact_form.app

    app.run(debug=True, host="0.0.0.0")

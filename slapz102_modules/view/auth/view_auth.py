import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template


def html_login(error=None, success=None):
    return render_template("auth/login.html", error=error, success=success)
# end def


def html_register(error=None):
    return render_template("auth/register.html", error=error)
# end def


def html_unauthorized():
    return render_template("auth/unauthorized.html"), 403
# end def


def html_setup(error=None):
    return render_template("auth/setup.html", error=error)
# end def

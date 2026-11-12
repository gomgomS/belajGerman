import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template
from landingpage import landingpage_proc


def html_index():
    data = landingpage_proc.get_site_data()
    return render_template("index.html", data=data)
# end def


def html_about():
    data = landingpage_proc.get_site_data()
    return render_template("about.html", data=data)
# end def


def html_faq():
    data = landingpage_proc.get_site_data()
    return render_template("faq.html", data=data)
# end def


def html_kontak():
    data = landingpage_proc.get_site_data()
    return render_template("contact.html", data=data)
# end def

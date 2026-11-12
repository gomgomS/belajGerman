import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import traceback
from flask import Blueprint, request

from view.landingpage import view_landingpage

landingpage_blueprint = Blueprint("landingpage_blueprint", __name__)


@landingpage_blueprint.route("/", methods=["GET"])
def index():
    try:
        return view_landingpage.html_index()
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def


@landingpage_blueprint.route("/tentang", methods=["GET"])
def about():
    try:
        return view_landingpage.html_about()
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def


@landingpage_blueprint.route("/faq", methods=["GET"])
def faq():
    try:
        return view_landingpage.html_faq()
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def


@landingpage_blueprint.route("/kontak", methods=["GET"])
def kontak():
    try:
        return view_landingpage.html_kontak()
    except Exception:
        print(traceback.format_exc())
        return "An error occurred", 500
    # end try
# end def

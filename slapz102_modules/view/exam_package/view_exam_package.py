import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template


def html_packages_list(packages, user, level_names=None, test_names=None):
    return render_template("expert/packages_list.html", packages=packages, user=user,
                           level_names=level_names or {}, test_names=test_names or {})
# end def


def html_package_form(package, user, test_types=None, levels=None, test_names=None):
    return render_template("expert/package_form.html",
                           package=package, user=user,
                           test_types=test_types or [],
                           levels=levels or [],
                           test_names=test_names or [])
# end def


def html_package_detail(package, user, levels=None, test_names=None, type_tests=None):
    levels     = levels or []
    test_names = test_names or []
    pkg        = package or {}
    level_code = pkg.get("level_code") or pkg.get("test_type") or ""
    level_label = next((r.get("label") for r in levels if r.get("code") == level_code), level_code)
    test_name_label = next(
        (r.get("label") for r in test_names if r.get("code") == pkg.get("test_name_code")),
        pkg.get("test_name_code") or ""
    )
    return render_template("expert/package_builder.html", package=package, user=user,
                           levels=levels, test_names=test_names,
                           type_tests=type_tests or [],
                           pkg_url="/expert/exam-package/" + str(pkg.get("package_no") or pkg.get("pkey") or ""),
                           level_code=level_code,
                           level_label=level_label,
                           test_name_label=test_name_label)
# end def


def html_package_preview(package, user, pkg_url=""):
    pkg = package or {}
    return render_template(
        "expert/package_preview.html",
        package=package,
        user=user,
        pkg_url=pkg_url or ("/expert/exam-package/" + str(pkg.get("package_no") or pkg.get("pkey"))),
    )
# end def


def html_package_bank_picker(package, section, candidates, user, part=None, package_url=""):
    return render_template(
        "expert/package_bank_picker.html",
        package=package,
        section=section,
        part=part,
        candidates=candidates or [],
        package_url=package_url or ("/expert/exam-package/" + str(package.get("package_no") or package.get("pkey"))),
        user=user,
    )
# end def

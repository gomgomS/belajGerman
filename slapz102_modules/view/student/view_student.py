import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template


def html_student_dashboard(stats, results, packages, subscription, sub_plans, user,
                           credit_balance=0, credit_error="", credit_ok="",
                           regular_packages=None, premium_packages=None):
    return render_template(
        "student/dashboard.html",
        stats=stats, results=results, packages=packages,
        subscription=subscription, sub_plans=sub_plans, user=user,
        credit_balance=credit_balance, credit_error=credit_error, credit_ok=credit_ok,
        regular_packages=regular_packages if regular_packages is not None else packages,
        premium_packages=premium_packages or [],
    )
# end def


def html_student_pricing(sub_plans, subscription, user, error=""):
    return render_template(
        "student/pricing.html",
        sub_plans=sub_plans, subscription=subscription, error=error, user=user,
    )
# end def


def html_student_subscription(subscription, sub_plans, user):
    return render_template(
        "student/abo.html",
        subscription=subscription, sub_plans=sub_plans, user=user,
    )
# end def


def html_student_history(results, orders, user,
                         results_locked=False, teaser_results=None, total_results=0):
    return render_template(
        "student/verlauf.html",
        results=results, orders=orders, user=user,
        results_locked=results_locked,
        teaser_results=teaser_results or [],
        total_results=total_results,
    )
# end def

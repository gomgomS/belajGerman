import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

from flask import render_template


def html_admin_dashboard(stats, user):
    return render_template("admin/dashboard.html", stats=stats, user=user)
# end def


def html_admin_students(students, user):
    return render_template("admin/students.html", students=students, user=user)
# end def


def html_admin_staff(staff, user):
    return render_template("admin/staff.html", staff=staff, user=user)
# end def


def html_expert_dashboard(stats, user):
    return render_template("expert/dashboard.html", stats=stats, user=user)
# end def


SETTINGS_MENU = [
    {
        "key"   : "tes",
        "title" : "Level",
        "desc"  : "Daftar level ujian: Goethe-Zertifikat A1, A2, B1, dst.",
        "href"  : "/dashboard/admin/settings/level",
        "ready" : True,
    },
    {
        "key"   : "test-name",
        "title" : "Nama Tes",
        "desc"  : "Daftar nama tes: Goethe-Zertifikat, TestDaF, telc, dst.",
        "href"  : "/dashboard/admin/settings/test-name",
        "ready" : True,
    },
    {
        "key"   : "test-type",
        "title" : "Bagian Ujian",
        "desc"  : "Bagian ujian & deskripsinya: Hören, Lesen, Schreiben, Sprechen",
        "href"  : "/dashboard/admin/settings/test-type",
        "ready" : True,
    },
    {
        "key"   : "sub-plan",
        "title" : "Paket Langganan",
        "desc"  : "Atur paket Free, Basic, Pro, Premium: harga bulanan & kredit AI",
        "href"  : "/dashboard/admin/settings/sub-plan",
        "ready" : True,
    },
]


def html_admin_settings_home(user):
    return render_template("admin/settings.html", settings_menu=SETTINGS_MENU, user=user)
# end def


def html_admin_settings_tes(test_types, user):
    return render_template("admin/settings_level.html", test_types=test_types, user=user)
# end def


def html_admin_settings_test_name(test_names, user):
    return render_template("admin/settings_test_name.html", test_names=test_names, user=user)
# end def


def html_admin_settings_type_test(type_tests, user, dump_counts=None):
    return render_template("admin/settings_type_test.html", type_tests=type_tests,
                           dump_counts=dump_counts or {}, user=user)
# end def


def html_admin_settings_type_test_dumps(type_test, dumps, user, ok="", error="", jenis_labels=None):
    return render_template("admin/settings_type_test_dumps.html", type_test=type_test,
                           dumps=dumps, ok=ok, error=error, user=user,
                           jenis_labels=jenis_labels or [])
# end def


def html_admin_settings_dump_preview(type_test, dump, item, user):
    return render_template("admin/dump_preview_sprechen.html", type_test=type_test,
                           dump=dump, item=item, user=user)
# end def


def html_admin_settings_sub_plan(sub_plans, user, cycles=None):
    return render_template(
        "admin/settings_sub_plan.html",
        sub_plans=sub_plans, cycles=cycles or [], user=user,
    )
# end def

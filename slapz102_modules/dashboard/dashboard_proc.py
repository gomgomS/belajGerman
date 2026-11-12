import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import traceback

import database
import config


def get_admin_stats():
    try:
        mgdDB = database.get_db_conn(config.mainDB)

        total_users     = mgdDB.db_toefl_user.count_documents({"is_deleted": False})
        total_packages  = mgdDB.db_toefl_package.count_documents({"is_deleted": False, "status": "PUBLISHED"})
        total_orders    = mgdDB.db_toefl_order.count_documents({})
        pending_orders  = mgdDB.db_toefl_order.count_documents({"status": "PENDING"})
        confirmed_orders = mgdDB.db_toefl_order.count_documents({"status": "CONFIRMED"})

        pipeline = [
            {"$match": {"status": "CONFIRMED"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        revenue_result = list(mgdDB.db_toefl_order.aggregate(pipeline))
        total_revenue  = revenue_result[0]["total"] if revenue_result else 0

        recent_orders  = list(mgdDB.db_toefl_order.find().sort("rec_timestamp", -1).limit(10))
        recent_users   = list(mgdDB.db_toefl_user.find({"is_deleted": False}, {"password": 0}).sort("rec_timestamp", -1).limit(10))

        return {
            "status"          : "OK",
            "total_users"     : total_users,
            "total_packages"  : total_packages,
            "total_orders"    : total_orders,
            "pending_orders"  : pending_orders,
            "confirmed_orders": confirmed_orders,
            "total_revenue"   : total_revenue,
            "recent_orders"   : recent_orders,
            "recent_users"    : recent_users,
        }
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def


def get_expert_stats(expert_pkey):
    try:
        mgdDB = database.get_db_conn(config.mainDB)

        my_packages  = list(mgdDB.db_toefl_package.find({"fk_expert_id": expert_pkey, "is_deleted": False}).sort("rec_timestamp", -1))
        my_passages  = mgdDB.db_toefl_passage.count_documents({"fk_expert_id": expert_pkey, "is_deleted": False})
        my_questions = mgdDB.db_toefl_question.count_documents({"fk_expert_id": expert_pkey, "is_deleted": False})

        return {
            "status"      : "OK",
            "my_packages" : my_packages,
            "total_passages"  : my_passages,
            "total_questions" : my_questions,
        }
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR", "my_packages": [], "total_passages": 0, "total_questions": 0}
    # end try
# end def


def get_peserta_stats(user_pkey):
    try:
        mgdDB = database.get_db_conn(config.mainDB)

        access_list  = list(mgdDB.db_toefl_access.find({"fk_user_id": user_pkey, "status": "ACTIVE"}))
        total_exams  = mgdDB.db_toefl_result.count_documents({"fk_user_id": user_pkey})
        recent_results = list(mgdDB.db_toefl_result.find({"fk_user_id": user_pkey}).sort("completed_at", -1).limit(5))

        for result in recent_results:
            package = mgdDB.db_toefl_package.find_one({"pkey": result.get("fk_package_id")}, {"title": 1, "test_type": 1})
            result["package_data"] = package
        # end for

        return {
            "status"        : "OK",
            "access_count"  : len(access_list),
            "total_exams"   : total_exams,
            "recent_results": recent_results,
        }
    except Exception:
        print(traceback.format_exc())
        return {"status": "ERROR"}
    # end try
# end def

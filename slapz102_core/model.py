import time

import copy

import pymongo

import os

import sys



from bson.objectid import ObjectId





class mongo_model:



    def __init__(self, record, lookup, db_handle):

        self._mongo_record  = copy.deepcopy(record)

        self._lookup_record = copy.deepcopy(lookup)

        self._db_handle     = db_handle

    # end def



    def put(self, key, value):

        if not (key in self._lookup_record):

            raise ValueError('SETTING_NON_EXISTING_FIELD', key, value)

        # end if

        self._mongo_record[key] = value

    # end def



    def get(self):

        return self._mongo_record

    # end def



    def delete(self , query):

        collection_name = self._lookup_record["__db__name__"]

        self._db_handle[collection_name].remove( query )

    # end def



    def insert(self, lock=None):

        collection_name = self._lookup_record["__db__name__"]

        del self._mongo_record["__db__name__"]

        if lock == None:

            self._db_handle[collection_name].insert_one(

                self._mongo_record

            )

        else:

            self._db_handle[collection_name].insert_one(

                self._mongo_record,

                session=lock

            )

        # end if

    # end def



    def update(self, query):

        collection_name = self._lookup_record["__db__name__"]

        self._db_handle[collection_name].update_one(

            query,

            { "$set" : self._mongo_record }

        )

    # end def

# end class



#

# MongoDB collection schemas used by ai-39py

#

db = {



    "db_config_all" : {

        "name"                  : "",

        "add_url"               : "",

        "edit_url"              : "",

        "value"                 : "",

        "count"                 : 0 ,

        "desc"                  : "",

        "type"                  : "",

        "misc"                  : "",

        "bo_access"             : "FALSE",

        "bo_access_2"           : "FALSE"

    },



    "db_config_general" : {

        "name"                  : "",

        "value"                 : "",

        "order"                 : 0 ,

        "status"                : "ENABLE",

        "desc"                  : "",

        "misc"                  : "",

    },



    "db_config_messages" : {

        "name"                  : "",

        "value"                 : "",

        "code"                  : "",

        "type"                  : "",

        "desc"                  : "",

        "status"                : "ENABLE",

    },



    "db_config_menu_webapp_handler" : {

        "name"                  : "",

        "value"                 : "",

        "href"                  : "",

        "status"                : "ENABLE",

        "fk_menu_id"            : "CONFIGURATION"

    },



    "db_config_webapp_menu_privilege" : {

        "name"                  : "",

        "value"                 : "",

        "order"                 : 0 ,

        "status"                : "ENABLE",

        "fk_privilege_id"       : "SELECT PRIVILEGE",

        "fk_menu_id"            : "SELECT MENU",

        "desc"                  : ""

    },



    "db_config_webapp_role_privilege" : {

        "name"                  : "",

        "value"                 : "",

        "order"                 : 0 ,

        "status"                : "ENABLE",

        "fk_privilege_id"       : "SELECT PRIVILEGE",

        "fk_role_id"            : "SELECT ROLE"

    },



    "db_config_webapp_route_privileges" : {

        "name"                  : "",

        "value"                 : "",

        "href"                  : "",

        "order"                 : 0 ,

        "route_type"            : "",

        "status"                : "ENABLE",

        "misc"                  : "",

        "desc"                  : "" ,

        "display_text"          : "",

        "icon"                  : "",

        "bo_access"             : "TRUE",

    },



    "db_config" : {

        "_id"                   : ObjectId(),

        "name"                  : "",

        "value"                 : "",

        "desc"                  : "",

        "config_type"           : "",

        "misc"                  : "",

        "data"                  : {}

    },



    "db_cookies" : {

        "fk_user_id"            : "",

        "cookie_id"             : "",

        "user_agent"            : {},

        "referrer"              : "",

        "x_forward_for"         : "",

        "username"              : "",

        "expire_time"           : "",

        "active"                : "",

    },



    "db_log_login_auth" : {

        "fk_user_id"            : "" ,

        "usernmae"              : "",

        "desc"                  : "",

        "state"                 : "LOGIN_FAILED",

    },



    "db_security_api_core" : {

        "api_key"               : "",

        "api_secret"            : "",

        "active"                : "TRUE",

        "description"           : ""

    },



    "db_security_cfs" : {

        "token_value"           : "",

        "username"              : "",

        "password"              : "",

        "expire_time"           : "",

        "active"                : "TRUE"

    },



    "db_security_user" : {

        "token_value"           : "",

        "username"              : "",

        "password"              : "",

        "expire_time"           : "",

        "active"                : "TRUE"

    },



    "db_setting_app" : {

        "idle_account"          : "",

        "force_change_password" : "",

        "password_history"      : "",

        "password_length"       : "",

        "variable_password"     : {

            "numeric"               : "FALSE",

            "lower_case"            : "FALSE",

            "upper_case"            : "FALSE",

            "symbol"                : "FALSE",

            "symbol_str"            : ""

        },

        "wrong_counter"         : "",

        "limit_history_password": 0,

        "screen_timeout"        : 0,

        "tran_timeout"          : 0,

    },



    "db_unique_counter" : {

        "counter"               : 0,

    },



    "db_super_user" : {

        "username"              : "",

        "password"              : "",

        "role"                  : "ADMIN",

    },



    "db_user" : {

        "fk_user_id"            : "",

        "username"              : "",

        "password"              : "",

        "role"                  : "",

        "role_position_value"   : "",

        "name"                  : "",

        "phone"                 : "",

        "email"                 : "",

        "type"                  : "",

        "status"                : "ACTIVE",

    },



    "db_user_auth" : {

        "fk_user_id"            : "",

        "username"              : "",

        "password"              : "",

    },



    "db_service_search_extract" : {

        "extract_id"            : "",

        "fk_user_id"            : "",

        "name"                  : "",

        "description"           : "",

        "status"                : "DRAFT",

        "row_count"             : 0,

        "updated_at"            : "",

    },

    "db_service_search_extract_row" : {

        "extract_id"            : "",

        "fk_user_id"            : "",

        "row_number"            : 0,

        "row_data"              : {},

    },

    "db_loan_agreement_extract" : {

        "extract_id"            : "",

        "fk_user_id"            : "",

        "name"                  : "",

        "description"           : "",

        "status"                : "DRAFT",

        "row_count"             : 0,

        "updated_at"            : "",

    },

    "db_loan_agreement_extract_row" : {

        "extract_id"            : "",

        "fk_user_id"            : "",

        "row_number"            : 0,

        "row_data"              : {},

    },

    # ─────────────────────────────────────────────────────────────
    # TOEFL PLATFORM COLLECTIONS
    # ─────────────────────────────────────────────────────────────

    "db_toefl_user" : {

        "user_id"               : "",

        "username"              : "",

        "email"                 : "",

        "password"              : "",

        "full_name"             : "",

        "phone"                 : "",

        "role"                  : "peserta",

        "status"                : "ACTIVE",

    },

    "db_toefl_session" : {

        "session_id"            : "",

        "fk_user_id"            : "",

        "username"              : "",

        "role"                  : "",

        "full_name"             : "",

        "user_agent"            : "",

        "ip_address"            : "",

        "expire_time"           : 0,

        "is_active"             : True,

    },

    "db_toefl_passage" : {

        "passage_id"            : "",

        "fk_package_section_id" : "",

        "fk_expert_id"          : "",

        "title"                 : "",

        "content_type"          : "text",

        "content_text"          : "",

        "audio_url"             : "",

        "instruction"           : "",          # Sprechen: Aufgabe/instruksi yang tampil ke siswa

        "image_url"             : "",          # Sprechen: gambar soal

        "sample_answer"         : "",          # Sprechen: Musterantwort (contoh jawaban)

        "prep_seconds"          : 0,           # Sprechen: detik persiapan

        "speak_seconds"         : 0,           # Sprechen: detik bicara

        "is_premium"            : False,       # penanda premium (info penyusun — khususnya tugas Sprechen)

        "sort_order"            : 0,

        "question_count"        : 0,

        "question_mode"         : "grouped",   # single | grouped | sprechen

        "answer_type"           : "mc",        # mc = pilihan ganda A–D | rf = Richtig/Falsch | cloze = Lückentext | speak = Sprechen (rekam suara)

        "cloze_answer_mode"     : "mc",        # cara menjawab rumpang Lückentext: mc = pilihan A–D | input = ketik jawaban (isian)

        "passage_sub_type"      : "",

        "section_key"           : "",

        "sub_type_key"          : "",

        "status"                : "DRAFT",

    },

    "db_toefl_question" : {

        "question_id"           : "",

        "fk_passage_id"         : "",

        "fk_package_section_id" : "",

        "fk_expert_id"          : "",

        "question_text"         : "",

        "option_a"              : "",

        "option_b"              : "",

        "option_c"              : "",

        "option_d"              : "",

        "option_a_image"        : "",          # URL gambar opsi, e.g. /static/images/xxx.png

        "option_b_image"        : "",

        "option_c_image"        : "",

        "option_d_image"        : "",

        "answer_type"           : "mc",        # rf: option_a = Richtig, option_b = Falsch

        "correct_answer"        : "A",

        "answer_text"           : "",          # Lückentext isian: kunci jawaban ketik (boleh multi, pisah ';')

        "explanation"           : "",

        "section_key"           : "",

        "sub_type_key"          : "",

        "is_premium"            : False,       # penanda soal premium (info penyusun — tidak memengaruhi akses/harga)

        "sort_order"            : 0,

        "status"                : "DRAFT",

    },

    "db_toefl_package" : {

        "package_id"            : "",

        "title"                 : "",

        "test_type"             : "ITP",

        "description"           : "",

        "price_basic"           : 0,

        "price_premium"         : 0,

        "is_premium"            : False,       # True = siswa membuka paket ini dengan Kredit AI

        "premium_credit_cost"   : 10,          # biaya buka (kredit) untuk paket premium

        "status"                : "DRAFT",

        "fk_expert_id"          : "",

        "total_questions"       : 0,

        "duration_minutes"      : 0,

        "cover_image"           : "",

        "package_no"            : 0,           # nomor urut untuk URL /expert/exam-package/<no>

        "level_code"            : "",          # db_level.code

        "test_name_code"        : "",          # db_test_name.code

    },

    "db_toefl_section_item" : {

        "fk_package_section_id" : "",

        "fk_passage_id"         : "",

        "fk_part_id"            : "",          # db_toefl_package_part.pkey, kosong = tanpa bagian

        "sort_order"            : 0,

    },

    "db_toefl_package_part" : {

        "fk_package_id"         : "",

        "fk_package_section_id" : "",

        "name"                  : "",          # bebas: "Teil 1", "Structure", dst.

        "sort_order"            : 0,

    },

    "db_toefl_package_section" : {

        "section_id"            : "",

        "fk_package_id"         : "",

        "title"                 : "",

        "section_type"          : "",

        "duration_minutes"      : 0,

        "sort_order"            : 0,

        "question_count"        : 0,

    },

    "db_toefl_exam_session" : {

        "exam_session_id"       : "",

        "fk_user_id"            : "",

        "fk_package_id"         : "",

        "fk_order_id"           : "",

        "current_section_id"    : "",

        "current_question_index": 0,

        "section_deadline"      : 0,

        "status"                : "IN_PROGRESS",

        "started_at"            : 0,

        "completed_at"          : 0,

        "section_order"         : [],

    },

    "db_toefl_exam_answer" : {

        "answer_id"             : "",

        "fk_exam_session_id"    : "",

        "fk_question_id"        : "",

        "fk_section_id"         : "",

        "selected_answer"       : "",

        "is_correct"            : False,

        "saved_at"              : 0,

    },

    "db_toefl_result" : {

        "result_id"             : "",

        "fk_exam_session_id"    : "",

        "fk_user_id"            : "",

        "fk_package_id"         : "",

        "total_score"           : 0,

        "listening_score"       : 0,

        "structure_score"       : 0,

        "reading_score"         : 0,

        "section_breakdown"     : {},

        "completed_at"          : 0,

    },

    "db_toefl_order" : {

        "order_id"              : "",

        "order_type"            : "EXAM",      # EXAM (per paket, legacy) | SUBSCRIPTION (langganan)

        "fk_user_id"            : "",

        "fk_package_id"         : "",

        "package_title"         : "",

        "tier"                  : "BASIC",

        "plan_code"             : "",          # SUBSCRIPTION: FREE | BASIC | PRO | PREMIUM

        "cycle"                 : "",          # SUBSCRIPTION: MONTHLY | QUARTERLY | YEARLY

        "months"                : 0,           # SUBSCRIPTION: 1 | 3 | 12

        "amount"                : 0,

        "status"                : "PENDING",

        "payment_method"        : "MANUAL",

        "payment_proof"         : "",

        "confirmed_by"          : "",

        "confirmed_at"          : 0,

        "notes"                 : "",

    },

    "db_level" : {

        "code"                  : "",

        "label"                 : "",

        "sort_order"            : 0,

        "status"                : "ACTIVE",

    },

    "db_toefl_section_template" : {

        "fk_test_type_code"     : "",

        "title"                 : "",

        "section_type"          : "",

        "duration_minutes"      : 0,

        "sort_order"            : 0,

    },

    "db_test_name" : {

        "code"                  : "",

        "label"                 : "",          # e.g. "Goethe-Zertifikat"

        "sort_order"            : 0,

        "status"                : "ACTIVE",

    },

    "db_test_type_dump" : {

        "fk_test_type_code"     : "",          # HOEREN | LESEN | ...

        "question_mode"         : "single",    # single | grouped

        "answer_type"           : "mc",        # mc | rf | cloze

        "cloze_mode"            : "",          # khusus cloze: mc | select | input (kosong = mc)

        "title"                 : "",          # ringkasan untuk daftar

        "dump_json"             : "",          # satu objek soal (single) / kelompok (grouped)

        "sort_order"            : 0,

        "status"                : "ACTIVE",

    },

    "db_test_type" : {

        "code"                  : "",          # HOEREN | LESEN | SCHREIBEN | SPRECHEN

        "label"                 : "",          # e.g. "Hören"

        "description"           : "",          # e.g. "Mendengarkan"

        "sort_order"            : 0,

        "status"                : "ACTIVE",

    },

    "db_toefl_access" : {

        "access_id"             : "",

        "fk_user_id"            : "",

        "fk_package_id"         : "",

        "fk_order_id"           : "",

        "scope"                 : "PACKAGE",   # PACKAGE (satu paket, legacy) | PLATFORM (semua ujian via langganan)

        "tier"                  : "BASIC",

        "status"                : "ACTIVE",

        "granted_at"            : 0,

        "expire_at"             : 0,           # epoch ms; 0 = tanpa batas (legacy EXAM)

    },

    # ─────────────────────────────────────────────────────────────
    # GERMAN PLATFORM – AI FEEDBACK
    # ─────────────────────────────────────────────────────────────

    "db_german_ai_feedback" : {

        "feedback_id"           : "",

        "fk_result_id"          : "",

        "fk_exam_session_id"    : "",

        "fk_user_id"            : "",

        "fk_package_id"         : "",

        "ai_provider"           : "gemini",   # "gemini" | "openai"

        "prompt_tokens"         : 0,

        "completion_tokens"     : 0,

        "feedback_text"         : "",         # teks feedback bahasa Indonesia/Jerman

        "level_estimate"        : "",         # e.g. "B1", "B2"

        "strengths"             : [],         # list string

        "improvements"          : [],         # list string

        "status"                : "PENDING",  # PENDING | OK | ERROR

        "generated_at"          : 0,

    },

    # ─────────────────────────────────────────────────────────────
    # GERMAN PLATFORM – KREDIT AI (ledger)
    # ─────────────────────────────────────────────────────────────

    "db_credit_ledger" : {

        "ledger_id"             : "",

        "fk_user_id"            : "",

        "delta"                 : 0,           # positif = grant, negatif = pemakaian

        "balance_after"         : 0,           # saldo kredit setelah transaksi

        "trx_type"              : "",          # GRANT_SUBSCRIPTION | GRANT_BACKFILL | EXAM_UNLOCK | ADMIN_ADJUST

        "fk_package_id"         : "",          # khusus EXAM_UNLOCK: paket yang dibuka

        "notes"                 : "",

    },

    # ─────────────────────────────────────────────────────────────
    # GERMAN PLATFORM – SUBSCRIPTION PLAN
    # ─────────────────────────────────────────────────────────────

    "db_subscription_plan" : {

        "code"                  : "",          # FREE | BASIC | PRO | PREMIUM

        "label"                 : "",

        "tagline"               : "",          # deskripsi singkat untuk kartu harga

        "price_idr"             : 0,           # harga bulanan (IDR), 0 = gratis

        "price_quarterly_idr"   : 0,           # harga 3 bulan; 0 = otomatis (bulanan x 3)

        "price_yearly_idr"      : 0,           # harga 12 bulan; 0 = otomatis (bulanan x 12)

        "discount_monthly_pct"  : 0,           # diskon bulanan (%)

        "discount_quarterly_pct": 0,           # diskon 3 bulan (%)

        "discount_yearly_pct"   : 0,           # diskon tahunan (%)

        "ai_credits_monthly"    : 0,           # kredit AI per bulan

        "sort_order"            : 0,

        "status"                : "ACTIVE",    # ACTIVE | INACTIVE

    },

}



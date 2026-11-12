import sys
sys.path.append("slapz102_core")
sys.path.append("slapz102_modules")
sys.path.append("slapz102_settings")
sys.path.append("slapz102_stdlib")
sys.path.append("slapz102_storage")

import html
import re


def clean_html_dic(data_dict):
    cleaned = {}
    for key, value in data_dict.items():
        if isinstance(value, str):
            cleaned[key] = html.escape(value.strip())
        else:
            cleaned[key] = value
        # end if
    # end for
    return cleaned
# end def


def clean_str(value):
    if isinstance(value, str):
        return html.escape(value.strip())
    # end if
    return value
# end def


def allow_html(value):
    if isinstance(value, str):
        return value.strip()
    # end if
    return value
# end def


def clean_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
    # end try
# end def


def strip_objectid(doc):
    """Recursively convert a MongoDB document to a JSON-safe dict.
    Drops the _id field and converts any remaining ObjectId to str."""
    if doc is None:
        return None
    # end if
    if not isinstance(doc, dict):
        return doc
    # end if
    result = {}
    for k, v in doc.items():
        if k == "_id":
            continue
        elif isinstance(v, dict):
            result[k] = strip_objectid(v)
        elif isinstance(v, list):
            result[k] = [
                strip_objectid(i) if isinstance(i, dict) else
                (str(i) if i.__class__.__name__ == "ObjectId" else i)
                for i in v
            ]
        elif v.__class__.__name__ == "ObjectId":
            result[k] = str(v)
        else:
            result[k] = v
        # end if
    # end for
    return result
# end def


def strip_objectid_list(docs):
    """Apply strip_objectid to a list of MongoDB documents."""
    if not docs:
        return []
    # end if
    return [strip_objectid(d) for d in docs]
# end def

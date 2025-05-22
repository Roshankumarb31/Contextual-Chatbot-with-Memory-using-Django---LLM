import os
import json
import decimal
from urllib.parse import urlparse
from psycopg2 import connect, Error
from psycopg2.extras import RealDictCursor
from django.conf import settings


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)


def clean_response(raw_response):
    try:
        cleaned = raw_response.strip().replace("```json", "").replace("```", "")
        cleaned = cleaned.replace("\\n", "\n").replace('\\"', '"')

        print("Cleaned string:", cleaned)

        data = json.loads(cleaned)

        output_data = {
            "reply": data.get("reply", ""),
            "is_query_generated": bool(data.get("is_query_generated", 0)),
            "table_display": bool(data.get("table_display", 0)),
            "query": data.get("sql_query") if data.get("is_query_generated") else False
        }

        output_path = os.path.join(settings.BASE_DIR, 'static', 'json')
        os.makedirs(output_path, exist_ok=True)

        with open(os.path.join(output_path, 'output_data.json'), 'w') as file:
            json.dump(output_data, file, indent=4)

        return output_data

    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

    return None


def fetch_from_db(query):
    try:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL not set in environment")

        result = urlparse(db_url)
        conn = connect(
            database=result.path.lstrip('/'),
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port or 5432
        )

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)
        records = cursor.fetchall()

        json_dir = os.path.join(settings.BASE_DIR, 'static', 'json')
        os.makedirs(json_dir, exist_ok=True)

        with open(os.path.join(json_dir, "data.json"), "w", encoding="utf-8") as file:
            json.dump(records, file, indent=4, cls=DecimalEncoder)

        cursor.close()
        conn.close()

        return True

    except Error as db_err:
        print(f"Database Error: {db_err}")
    except Exception as e:
        print(f"Error: {e}")

    return False
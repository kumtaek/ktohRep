from typing import Tuple


def java_system_prompt() -> str:
    return (
        "너는 정적 분석 보조 AI다. 지시된 스키마에 맞춘 JSON만 출력해라. "
        "설명 문장, 마크다운, 코드블록, 기타 텍스트는 절대 포함하지 마라."
    )


def java_user_prompt(snippet: str) -> Tuple[str, str]:
    prompt_id = "java_struct_extractor_v1"
    user = (
        "다음 Java 코드에서 클래스와 메서드를 추출해 JSON으로만 응답해라.\n"
        "스키마:\n"
        "{\n  \"classes\": [ {\n    \"name\": str, \n    \"fqn\": str?, \n    \"start_line\": int?, \n    \"end_line\": int?,\n    \"methods\": [ { \n      \"name\": str, \n      \"signature\": str?, \n      \"return_type\": str?, \n      \"start_line\": int?, \n      \"end_line\": int? \n    } ]\n  } ]\n}\n"
        "JSON 외 출력 금지. 값이 불명확하면 null 또는 생략.\n\n"
        f"<CODE>\n{snippet}\n</CODE>"
    )
    return prompt_id, user


def jsp_system_prompt() -> str:
    return (
        "너는 정적 분석 보조 AI다. 지시된 스키마에 맞춘 JSON만 출력해라. "
        "설명 문장, 마크다운, 코드블록, 기타 텍스트는 절대 포함하지 마라."
    )


def jsp_user_prompt(snippet: str) -> Tuple[str, str]:
    prompt_id = "jsp_sql_extractor_v1"
    user = (
        "다음 파일에서 SQL 문과 테이블/조인/필수필터를 추출해 JSON으로만 응답해라.\n"
        "스키마:\n"
        "{\n  \"sql_units\": [ {\n    \"stmt_kind\": \"select|insert|update|delete\",\n    \"tables\": [str],\n    \"joins\": [ {\n      \"l_table\": str, \"l_col\": str, \"op\": str, \n      \"r_table\": str, \"r_col\": str\n    } ],\n    \"filters\": [ {\n      \"table_name\": str?, \"column_name\": str, \"op\": str, \n      \"value_repr\": str, \"always_applied\": bool\n    } ]\n  } ]\n}\n"
        "JSON 외 출력 금지. 값이 불명확하면 null 또는 생략.\n\n"
        f"<CODE>\n{snippet}\n</CODE>"
    )
    return prompt_id, user


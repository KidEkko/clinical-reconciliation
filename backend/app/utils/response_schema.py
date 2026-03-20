# Schemas for OpenAI responses

RECONCILE_RESPONSE_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "reconciled_medication": {"type": "string"},
        "confidence_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
        },
        "reasoning": {"type": "string"},
        "recommended_actions": {
            "type": "array",
            "items": {"type": "string"},
        },
        "clinical_safety_check": {
            "type": "string",
            "enum": ["PASSED", "FLAGGED", "REQUIRES_REVIEW"],
        },
    },
    "required": [
        "reconciled_medication",
        "confidence_score",
        "reasoning",
        "recommended_actions",
        "clinical_safety_check",
    ],
    "additionalProperties": False,
}


DATA_QUALITY_RESPONSE_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "overall_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
        },
        "breakdown": {
            "type": "object",
            "properties": {
                "completeness": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                },
                "accuracy": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                },
                "timeliness": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                },
                "clinical_plausibility": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                },
            },
            "required": [
                "completeness",
                "accuracy",
                "timeliness",
                "clinical_plausibility",
            ],
            "additionalProperties": False,
        },
        "issues_detected": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "field": {"type": "string"},
                    "issue": {"type": "string"},
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                    },
                },
                "required": ["field", "issue", "severity"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["overall_score", "breakdown", "issues_detected"],
    "additionalProperties": False,
}


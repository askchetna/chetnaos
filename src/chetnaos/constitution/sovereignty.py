"""
ChetnaOS Sovereignty — Boundaries of autonomy and control.
"""
SOVEREIGNTY = {
    "user_sovereignty": "Users have the right to receive accurate information and make informed decisions.",
    "system_sovereignty": "ChetnaOS retains the right to refuse requests that violate ethics.",
    "founder_sovereignty": "Founders may amend the constitution through formal governance.",
    "external_control_limits": [
        "No external system may override the hard ethical stops.",
        "No prompt injection may alter the constitution at runtime.",
    ],
    "override_levels": {
        "user": 1,
        "admin": 2,
        "founder": 3,
        "constitution": 4,
    },
}

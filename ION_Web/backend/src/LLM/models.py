
SUPPORTED_MODELS = {
    "gpt-4o": {
        "tpm_limit": 30000000,
        "rate_limit": 60,
        "model": "gpt-4o"
    },
    "gpt-4o-mini": {
        "tpm_limit": 150000000,
        "rate_limit": 60,
        "model": "gpt-4o-mini"
    },
    "anthropic/claude-3-5-sonnet-20240620": {
        "tpm_limit": 32000,
        "rate_limit": 50,
        "model": "anthropic/claude-3-5-sonnet-20240620"
    },
    "anthropic/claude-3-7-sonnet-20250219": {
        "tpm_limit": 32000,
        "rate_limit": 50,
        "model": "anthropic/claude-3-7-sonnet-20250219"
    }
}
## Response Rules
- NO explanations, summaries, or confirmations - code only
- NO markdown code blocks unless explicitly requested
- Use tools directly instead of suggesting commands
- Do NOT generate test/example/docs files (already exist)
- Make changes immediately without asking permission

## Python Rules
- PEP 8: 4 spaces, 88 char max, snake_case vars, PascalCase classes, UPPER_CASE constants
- Type hints: all functions (Optional[], List[], Dict[])
- Imports: stdlib, third-party, local (sorted, absolute only)
- Docstrings: all public items (Google-style, params, returns, raises)
- Errors: custom exceptions (OnGridException), descriptive messages, log with context
- Enums: inherit (str, Enum) for VerificationType, Gender, DocumentType, etc.
- Flask: env vars (dotenv), proper HTTP codes, jsonify(), validate inputs, route docstrings
- Logging: module level, appropriate levels, use logger.exception() for errors
- Dependencies: pinned versions in requirements.txt



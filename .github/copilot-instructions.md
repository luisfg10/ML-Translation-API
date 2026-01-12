## Project Overview
This project is a Python-based application designed to serve `Hugging Face` translation models via a RESTful API using `FastAPI`.

### Golden Rules
* When unsure about implementation details or requirements, ALWAYS consult the developer rather than making assumptions.
* Always ask for permission before creating new files or deleting existing ones.
* Limit your responses to the specific ask of the developer.

### Coding Standards
* Functions/methods: Always include a docstring briefly describing its purpose and parameters, along with type hints for parameters and return values. No need to over-explain obvious functionality.
* Naming: `snake_case` (functions/variables), `PascalCase` (classes), `SCREAMING_SNAKE` (constants).
* Use the typing library for type hints in both functions and regular objects, with imports such as `List`, `Dict`, `Optional`, `Union`, etc.
* Always use **logger** from `loguru` for logging instead of generic `print` statements.
* Limit line length to 100 characters tops, and respect standard flake8 linter rules.

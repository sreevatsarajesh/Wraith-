# Contributing to Wraith

Issues and pull requests are welcome. Good first contributions include new ghost personalities, shell compatibility tests, configurable response frequency, and stronger secret redaction.

Before submitting:
1. Run `pytest`.
2. Confirm the shell hook never executes generated model output.
3. Keep all inference local by default.
4. Document any new stored data and provide a way to erase it.

# Contributing

Open an issue describing the expected behaviour, observed behaviour and a minimal synthetic scenario. For a code change:

1. Create a branch and keep the change focused.
2. Add or update tests for changes to admission, scoring or recovery behaviour.
3. Run `python -m unittest discover -s tests -v` from the repository root.
4. Run the included policy comparison and explain any changed results.
5. Update documentation when public interfaces or assumptions change.
6. Open a pull request describing the change and checks performed.

Do not claim simulator outputs are real network measurements. Never include device credentials, private network configurations, personal information or unpublished research data without permission.

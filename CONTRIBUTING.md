# Contributing to Physiological G-Code

Thanks for your interest in improving this project!

## Getting set up

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # defaults work for local SQLite development
python manage.py migrate
python manage.py load_hexagrams
python manage.py load_codons
python manage.py runserver      # http://localhost:8000
```

Python 3.11+ is required (3.12 recommended).

## Running the tests

Please include tests for any change and keep the suite green:

```bash
pytest                                        # everything
pytest tests/test_genetic_engine.py -v        # engine only
pytest --cov=api --cov=genetic_engine         # with coverage
```

## Guidelines

- **Code style**: the repo uses `black` and `isort` (both in `requirements.txt`);
  run them before committing (`black . && isort .`).
- **Migrations**: if you change a model, generate a migration
  (`python manage.py makemigrations api`) and commit it with your change.
- **API surface**: keep responses additive — add new fields instead of
  changing the meaning of existing ones.
- **Commit messages**: short imperative subject line; explain *why* in the body
  when the change isn't obvious.
- **Science content** (codon tables, hexagram data): include a source or
  citation for factual changes.

## Reporting issues

Open a GitHub issue with: what you did, what you expected, what happened,
and the full traceback if one was raised.

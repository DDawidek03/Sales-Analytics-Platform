# Security

## Public repository checklist

- Never commit `.env`, database exports, generated JSON/CSV files, local backups or IDE files.
- The repository intentionally contains `.env.example`, not `.env`; copy it locally and fill in secrets only on your own machine.
- Keep `FLASK_SECRET_KEY`, Azure credentials and Cosmos DB keys in environment variables only.
- Use a new random `FLASK_SECRET_KEY` of at least 32 characters for every deployment.
- Set `SESSION_COOKIE_SECURE=true` when serving the application over HTTPS.
- Do not use production credentials in the Power BI file. Review its data sources and remove saved credentials before publishing.
- Rotate any credential immediately if it was ever committed or shared.

## Scope

This repository is a demonstration package. The included Flask development server binds to `127.0.0.1` and runs with debug mode disabled. It is not a production deployment configuration; production use still requires HTTPS, a hardened WSGI server, restricted database access, rate limiting and operational monitoring.

The `.pbix` file is a binary artifact and cannot be fully audited by a text-based secret scan. Its data sources and embedded model must be reviewed in Power BI Desktop before the public repository is pushed.
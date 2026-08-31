# Companies Directory

This directory contains company-specific data and is **NOT tracked in git** for security reasons.

## Structure

Each company should have the following files:

```
companies/
└── CompanyName/
    ├── meta.json          # OAuth tokens and realm ID (SENSITIVE)
    ├── context.json       # Company context and preferences
    └── PROFILE.md         # Company profile
```

## Adding a Company

Use the company manager to add a new company:

```bash
python company_manager.py
```

This will guide you through:
1. Entering the company name
2. Providing the QBO Realm ID
3. Completing the OAuth flow to get tokens

## Security Warning

**NEVER commit `meta.json` files to version control.** They contain:
- `access_token`: OAuth access token
- `refresh_token`: OAuth refresh token
- `realm_id`: QuickBooks company ID

These files are automatically excluded via `.gitignore`.

## File Descriptions

| File | Description | Sensitive |
|------|-------------|-----------|
| `meta.json` | OAuth tokens and realm ID | YES - Never commit |
| `context.json` | Company preferences, chart of accounts, rules | No |
| `PROFILE.md` | Company description and notes | No |

## Managing Multiple Companies

Dexter supports multiple companies. You can:

1. **List companies**: `python company_manager.py --list`
2. **Switch companies**: `python company_manager.py --switch`
3. **Add company**: `python company_manager.py --add`
4. **Remove company**: `python company_manager.py --remove`

## Data Isolation

Each company's data is completely isolated:
- Separate OAuth tokens
- Separate context and preferences
- Separate memory and learning data

This ensures that data from one company is never mixed with another.

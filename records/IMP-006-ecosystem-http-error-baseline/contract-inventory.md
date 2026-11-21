# IMP-006 Contract Inventory

Date: 2026-10-13
Scope: Read-only inventory of the HTTP and Apps Script Web App boundaries used by
`pf-rates`, `pf-payroll`, and `pf-sheets`.

## Evidence sources

- `pf-rates` route decorators and `docs/api.md`;
- `pf-payroll` route decorators and `docs/api.md`;
- `pf-sheets/src/interfaces/webapp.js` and `docs/api.md`;
- root Postman collection `postman/pf-ecosystem.postman_collection.json`;
- generated OpenAPI remains the final runtime contract where documentation differs.

No production payloads, credentials, authorization headers, or raw operational logs
were collected.

## Authentication boundary

| Service | Public boundary | Authentication |
|---|---|---|
| `pf-rates` | `GET /health` | None |
| `pf-rates` | All other routes | `X-API-Key` |
| `pf-payroll` | `GET /health` | None |
| `pf-payroll` | All other routes | `X-API-Key` |
| `pf-sheets` | `doGet` / `doPost` Web App | `key` query parameter / request parameter |

## pf-rates HTTP surface

| Method | Path | Source |
|---|---|---|
| GET | `/health` | `interfaces/api/main.py` |
| GET | `/monetary-units` | `interfaces/api/main.py` |
| GET | `/exchange-rates` | `routes/exchange_rates.py` |
| GET | `/exchange-rates/value` | `routes/exchange_rates.py` |
| POST | `/exchange-rates/values` | `routes/exchange_rates.py` |
| POST | `/exchange-rates/refresh` | `routes/exchange_rates.py` |
| GET | `/economic-indices` | `routes/economic_indices.py` |
| GET | `/economic-indices/value` | `routes/economic_indices.py` |
| POST | `/economic-indices/values` | `routes/economic_indices.py` |
| POST | `/economic-indices/refresh` | `routes/economic_indices.py` |
| GET | `/income-tax-brackets` | `routes/income_tax_brackets.py` |
| GET | `/income-tax-brackets/list` | `routes/income_tax_brackets.py` |
| POST | `/income-tax-brackets/refresh` | `routes/income_tax_brackets.py` |
| POST | `/exports/financial-data` | `routes/exports.py` |
| GET | `/exports/jobs` | `routes/export_jobs.py` |
| GET | `/exports/jobs/{job_id}` | `routes/export_jobs.py` |
| POST | `/exports/jobs/stop` | `routes/export_jobs.py` |
| POST | `/exports/jobs/{job_id}/stop` | `routes/export_jobs.py` |
| POST | `/sync` | `routes/sync.py` |

## pf-payroll HTTP surface

| Method | Path | Source |
|---|---|---|
| GET | `/health` | `routes/health.py` |
| GET | `/payroll` | `routes/payroll.py` |
| GET | `/payroll/{period_id}` | `routes/payroll.py` |
| DELETE | `/payroll` | `routes/payroll.py` |
| DELETE | `/payroll/{period_id}` | `routes/payroll.py` |
| POST | `/payroll/import/json` | `routes/payroll.py` |
| POST | `/payroll/import/spreadsheet` | `routes/payroll.py` |
| POST | `/payroll/pdf-preview` | `routes/payroll.py` |
| GET | `/payroll/spreadsheet` | `routes/payroll_export.py` |
| GET | `/payroll/spreadsheet/template` | `routes/payroll_export.py` |
| POST | `/payroll/templates` | `routes/pdf_templates.py` |
| GET | `/payroll/templates` | `routes/pdf_templates.py` |
| GET | `/payroll/templates/{template_id}` | `routes/pdf_templates.py` |
| PUT | `/payroll/templates/{template_id}` | `routes/pdf_templates.py` |
| DELETE | `/payroll/templates/{template_id}` | `routes/pdf_templates.py` |
| GET | `/payroll/employers` | `routes/employers_contracts.py` |
| POST | `/payroll/employers` | `routes/employers_contracts.py` |
| DELETE | `/payroll/employers` | `routes/employers_contracts.py` |
| GET | `/payroll/contracts` | `routes/employers_contracts.py` |
| POST | `/payroll/contracts` | `routes/employers_contracts.py` |
| DELETE | `/payroll/contracts` | `routes/employers_contracts.py` |
| GET | `/reference-data/pension-institutions` | `routes/reference_data.py` |
| GET | `/reference-data/health-institutions` | `routes/reference_data.py` |
| GET | `/reference-data/pension-plans` | `routes/reference_data.py` |
| GET | `/reference-data/health-plans` | `routes/reference_data.py` |
| GET | `/reference-data/contribution-caps` | `routes/reference_data.py` |
| GET | `/reference-data/payroll-concepts` | `routes/reference_data.py` |

## pf-sheets Web App surface

| Method | Operation | Source |
|---|---|---|
| GET | `doGet`: single value lookup using `date`, `code`, and `key` | `src/interfaces/webapp.js` |
| POST | `doPost`: batch value lookup using `pairs` and `key` | `src/interfaces/webapp.js` |

The Web App returns plain text for `doGet` and JSON for `doPost`. The boundary is
not a FastAPI route and must not be normalized as if it were one.

## Documentation and Postman comparison

The route inventory contains 19 `pf-rates` paths and 31 `pf-payroll` paths
(including the shared health/reference surfaces). Every inspected implementation
path has a corresponding entry in the owning `docs/api.md`.

The Postman collection represents the dynamic paths with collection variables or
concrete example identifiers, including:

- `{{export_job_id}}` for export-job lookup and stop operations;
- concrete template IDs for template lookup, update, and delete;
- the documented `pf-sheets` Web App request shapes in its service folder.

No implementation-to-API-docs mismatch was identified in this read-only pass. No
public contract change is proposed. The next slice is sanitized evidence-template
creation and synthetic failure validation.

## Initial observations

1. The service route inventories and documented API surfaces can be compared using
   their repository-owned docs and generated OpenAPI.
2. `pf-rates` and `pf-payroll` share the `X-API-Key` authentication convention,
   while `pf-sheets` uses its Web App `key` parameter.
3. `pf-sheets` is a consumer boundary with `doGet` and `doPost`; it is not a direct
   consumer of singular `pf-rates` value endpoints in the current batch/export path.
4. The inventory does not declare a defect. Differences become contract failures
   only after request/response/status/auth comparisons against the actual consumer.

## Next validation

- Create the sanitized evidence template.
- Validate representative synthetic contract, client, application, dependency,
  infrastructure, and unknown cases.
- Record any intentional differences or unresolved mismatches as sanitized evidence.

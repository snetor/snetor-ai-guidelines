# Logo & icon catalog

Logos live in the shared Snetor asset set (`snetor-html-slides/assets/logos` and `.../branding`), so
both visual skills share one source of truth. Pass the **file name** (e.g. `"azure-key-vault.png"`)
to `image` / `card` / `icon_row`. Run `python scripts/excalidraw_snetor.py` for the authoritative,
up-to-date list. If something is missing, add a transparent-background PNG to the shared `logos/`.

> Names are the actual file names (including `azure-ressource-group.png`, which keeps its spelling).

## Snetor brand (`branding/`)
`snetor_full_logo.png` (header), `snetor_full_logo_reversed.png` (on dark), `snetor_globe.png`
(compact mark), `snetor_colors.png`, `snetor_shapes.png`, `Hero-banner-abstrait.jpg`.

## Azure — services (use for resource-group / service boxes)
| File | Use for |
|---|---|
| `azure.png` | The subscription / Azure overall (corner logo) |
| `azure-ressource-group.png` | A resource group |
| `azure-subnet.png` | VNet / subnets / networking |
| `azure-private-endpoint.png` | Private endpoints / private DNS |
| `azure-key-vault.png` | Key Vault / secrets |
| `azure-log-analytics.png` | Log Analytics / monitoring |
| `azure-cost-analysis.png` | Budget / cost / FinOps |
| `azure-aca.png` | Container Apps |
| `azure-acr.png` | Container Registry |
| `azure-aks.png` | Kubernetes (AKS) |
| `azure-function.png` | Function App |
| `azure-sql.png` | Azure SQL / SQL Database |
| `azure-blob-storage.png` | Blob storage |
| `azure-app-insights.png` | Application Insights |
| `azure-front-door.png` | Front Door (public entry) |
| `azure-waf.png` | WAF |
| `azure-ai-foundry.png` | Azure AI Foundry / model hosting |

## Microsoft / M365 & data
`microsoft.png`, `microsoft_fabric.png` (Fabric), `powerbi.png`, `sharepoint.png`,
`power-automate.png`, `entra-id.png` (Entra ID / groups / identity), `databricks.png`.

## AI models & assistants
`anthropic.png`, `claude.png`, `openai.png`, `gemini.png`, `mistral.png`, `perplexity.png`,
`vertex-ai.png`, `amazon-bedrock.png`, `copilot.png`, `copilot-studio.png`, `copilot-cowork.png`,
`codex.png`, `litellm.png` (the LiteLLM gateway).

## Dev / infra / tooling
`github.png`, `github-actions.png` (CI/CD, SP), `terraform.png` (IaC, tf-plan/apply),
`postgresql.png`, `redis.png`, `twenty.png` (Twenty CRM), `obsidian.png`.

## Clouds (for multi-cloud / comparison)
`aws.png`, `amazon.png`, `gcp.png`, `google.png`.

## SAP & ERP / ECM
`sap.png`, `s4-hana.png` (S/4HANA), `sap-b1.png`, `sap-concur.png`, `opentext.png`.

## Snetor ecosystem (partners / tools / customers)
`alpega-tms.png`, `buyco.png`, `datasur.png`, `kantox.png`, `xeneta.png`.

## Tips
- One representative icon per box; for technical app boxes add a 2–4 icon **row** of the underlying
  services (`icon_row`). Don't overcrowd.
- The toolkit auto-trims transparent margins and downscales, so mixing square glyphs and wide
  lockups still sizes consistently.

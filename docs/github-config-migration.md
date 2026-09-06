# Retiring github-config

Inventory and migration proposal, 6 September 2026. Recommended next implementation: move the generic issue/PR templates and funding configuration into `.github`, then remove their legacy sync mappings and redundant consumer copies in a small pilot.

## Audited scope

The inventory covers all **32 tracked files** and every active mapping in [github-config at a6ad975](https://github.com/klaasnicolaas/github-config/tree/a6ad975471de4c6a2c7849e6de1da3e4cfff6e25). Its [sync configuration](https://github.com/klaasnicolaas/github-config/blob/a6ad975471de4c6a2c7849e6de1da3e4cfff6e25/.github/sync.yml) expands to **442 file destinations across 31 repositories**: 27 personal Python packages, pypackage-template, home-assistant-glow, and two NIPKaart projects. Sixteen of the 17 export-source files are actively mapped; Dependabot is unused.

Counts below describe configured copies, not verified equality with every destination's current contents. The template can receive the same source in its own configuration and in generated-package files. Repository-specific differences must be checked before removing local copies.

Current rollout: [central defaults #1](https://github.com/klaasnicolaas/.github/pull/1), [sync exclusions #443](https://github.com/klaasnicolaas/github-config/pull/443), and [template #579](https://github.com/klaasnicolaas/pypackage-template/pull/579) are merged. [Gridnet #1309](https://github.com/klaasnicolaas/python-gridnet/pull/1309) remains open. Central labels have successfully synchronized Gridnet and the template; the remaining packages are not enrolled yet.

## Shared-source decisions

Paths in the first column are relative to `github-config`. Counts are destination files / distinct repositories.

| Source | Copies / repos | Destination and migration decision |
| --- | --- | --- |
| `github/FUNDING.yml` | 30 / 30 | `.github/.github/FUNDING.yml` as an account default. Current content names klaasnicolaas for GitHub Sponsors and Ko-fi. Preserve intentional local funding choices. |
| `github/ISSUE_TEMPLATE/bug_report.yml` | 30 / 30 | `.github/.github/ISSUE_TEMPLATE/bug_report.yml` as an account default. Generic form; requires the `bug` label. |
| `github/ISSUE_TEMPLATE/feature_request.yml` | 30 / 30 | `.github/.github/ISSUE_TEMPLATE/feature_request.yml` as an account default. Requires `enhancement` and `new-feature`. |
| `github/PULL_REQUEST_TEMPLATE.md` | 30 / 30 | `.github/.github/PULL_REQUEST_TEMPLATE.md` as an account default; preserve package-specific checklists where needed. |
| `github/labels.yml` | 29 / 29 | Already replaced centrally by `labels/base.yml`. Enroll remaining repositories, extend token access and remove local copies. |
| `github/release-drafter.yml` | 28 / 28 | Already replaced by the current `.github/release-drafter.yml` here. Remove local configs after checking overrides and action compatibility. |
| `github/workflows/sync-labels.yaml` | 28 / 28 | Remove per-repository workflows after enrolling targets in the central sync. No reusable caller is needed for labels. |
| `github/workflows/pr-labels.yaml` | 31 / 30 | First reusable-workflow candidate: `.github/workflows/pr-labels.yaml` with `workflow_call`. The source already supports that trigger. Keep a small local PR-event caller. |
| `github/workflows/stale.yaml` | 31 / 30 | Reusable workflow with local schedule/manual caller and repository token. Preserve current 30-day stale / 7-day close policy initially, with explicit inputs for exceptions. |
| `github/workflows/lock.yaml` | 31 / 30 | Reusable workflow with local schedule/manual caller. Preserve the current 30-day closed-issue / 1-day closed-PR inactivity thresholds initially. |
| `github/workflows/release-drafter.yaml` | 28 / 28 | Keep the small workflow in the package template for now; its policy is already central. A reusable wrapper adds little value at this stage. |
| `python_package/renovate.json` | 26 / 26 | Replace with the existing `renovate-python.json` preset here and small local `extends` files. Preserve overrides. |
| `python_package/.devcontainer/devcontainer.json` | 28 / 28 | Maintain through pypackage-template; each package needs a local file. Reconcile old tooling settings before retiring this source. |
| `python_package/.gitignore` | 29 / 28 | Maintain through pypackage-template; retain local project-specific exclusions. |
| `python_package/.yamllint` | 31 / 30 | Maintain through pypackage-template and keep a local config for offline tooling. Avoid adding a remote-download dependency for linting. |
| `nipkaart/.gitignore` | 2 / 2 | Keep with the NIPKaart projects or their own template. It adds `app/data/*.json`; do not replace it blindly with the generic Python file. |
| `python_package/dependabot.yml` | 0 / 0 | Candidate for deletion with its commented-out mapping after confirming no external manual use. Do not create another shared dependency policy. |

## Repository-local infrastructure

These remaining 15 tracked files maintain `github-config` itself; they are not distributed sources.

| Files | Disposition |
| --- | --- |
| `.github/FUNDING.yml`, `.github/labels.yml`, `.github/release-drafter.yml`, `.github/renovate.json` | Adopt the same central defaults/preset for github-config while it remains active; remove duplicates only after label enrollment and compatibility checks. |
| `.github/workflows/labels.yaml` | Remove after adding github-config to the central label targets. It still uses the old label-sync action. |
| `.github/workflows/release-drafter.yaml` | Keep during the transition, consuming central release policy. |
| `.github/sync.yml`, `.github/workflows/sync.yaml` | Shrink mappings per migration. Retire the release-triggered sync only after the last target has an alternative. Do not recreate this full copy mechanism in `.github`. |
| `.github/workflows/linting.yaml`, `.pre-commit-config.yaml`, `.yamllint`, `pyproject.toml`, `poetry.lock` | Keep while the legacy repository is maintained. Its Poetry/pre-commit environment is not needed by the new central configs. Local uncommitted prek migration changes were excluded from this audit and remain untouched. |
| `README.md` | Document the replacement locations and eventual archival status. |
| `LICENSE` | Retain for the repository's own contents and history; licenses must also remain in individual packages. |

## Constraints that determine the rollout

GitHub account defaults apply to repositories with the same owner, including private repositories, when no local override exists. Issue templates are special: an existing local issue-template configuration or valid template prevents the entire default folder from being used. Required form labels must exist both here and in each consuming repository. Inherited files are not included in repository clones. [GitHub default-file documentation](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)

Ownership is decided: `NIPKaart/disabled-parking` and `NIPKaart/offstreet-parking` migrate to **NIPKaart/.github** for their central defaults and automation. Retire their legacy mappings after that owner-specific replacement is ready.

**Home Assistant Glow participates in klaasnicolaas/.github** alongside the other personal repositories: shared community defaults, central labels, and applicable release/triage workflows. Its current legacy mappings cover only funding and labels, but that is a description of the old setup, not a restriction on migration. Enroll Glow in the central label targets and token access during rollout. Keep project-specific tooling local; select Renovate rules appropriate to Glow rather than assuming every personal repository is a Python package.

Reusable workflows require local callers; putting an ordinary workflow here does not make it run in other repositories. Keep events and schedules local, grant only the caller permissions needed by each job, and pin shared workflow references to commits maintained by Renovate. Preserve required check names or update branch protection when moving PR validation. [GitHub reusable-workflow documentation](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)

The PR-label workflow only reads metadata. Its migration should not add PR code checkout or execution. Stale/lock can use each caller's repository token; a new account-wide write token is unnecessary for those workflows.

## Existing divergence to resolve

- The template's PR-label workflow pins action v2.1.2, whereas the legacy source uses v3.1.1. Choose and validate the shared version, rather than copying either file without review.
- The legacy devcontainer installs a pre-commit feature but runs `poetry run prek install`, and still contains mypy/older Python-extension settings. Reconcile it with the current template and intended ty/prek tooling before rollout.
- The legacy Renovate source has custom GitHub Actions version extraction/regex rules. The published Python preset uses built-in version handling and digest pinning instead; migration should keep that newer behavior.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`, and issue-template `config.yml` do not exist among the export sources. They are future additions, not files already waiting to be moved. Draft account-wide content separately; package-specific security/support details may stay local.

## Migration order and completion checks

1. **Finish the existing pilot.** Merge Gridnet #1309 and verify its default-branch release workflow loads the central policy. Central labels and the template migration are already in place.
2. **Move community defaults.** Publish funding and generic issue/PR templates here. Create their required labels in this repository as well as the pilot. Remove the corresponding sync mappings before deleting redundant local files in the pilot/template. Check the issue chooser, PR form and sponsor link in GitHub, including one repository with a deliberate local override.
3. **Centralize PR-label validation.** Add one reusable workflow and pilot its local caller. Exercise label changes and preserve the required status check. Then remove the old sync mapping and roll out.
4. **Centralize stale and lock.** Add two reusable workflows with small local callers and explicit policy inputs. Compare effective inputs to current behavior before the next scheduled runs. Replace legacy mappings as callers migrate.
5. **Roll out and retire template-owned sources.** Migrate remaining packages in batches; enroll label targets and token access together, preserve overrides, and use Copier updates for local tooling files. Verify existing Copier answers/version tracking before expecting automated updates; adopt legacy packages individually where needed. Include Glow in the personal-account rollout. Coordinate the NIPKaart handover to NIPKaart/.github independently.
6. **Retire github-config.** Confirm no active mappings or external references remain, close or supersede old sync PRs, remove unused secrets, disable the sync workflow, document replacement locations, and archive the repository. Retain history and license.

For each batch, publish the replacement first, protect consumers from legacy sync, migrate local files/callers, and verify behavior before marking maintenance work complete. A copied or inherited file alone is not proof that the relevant workflow or UI uses it.

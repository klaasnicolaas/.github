# Shared configuration rollout

## Shared configuration rollout — 2026-09-06

Workflows remain local. Shared Release Drafter and Renovate configuration lives in klaasnicolaas/.github; central label synchronization is the explicit exception. All 31 label targets were successfully synchronized in [run 34056657321](https://github.com/klaasnicolaas/.github/actions/runs/34056657321).

Merge order: [central defaults #7](https://github.com/klaasnicolaas/.github/pull/7), then [legacy sync exclusions #445](https://github.com/klaasnicolaas/github-config/pull/445), then the consumer PRs below. Glow targets develop and retains its unprefixed release tags, npm policy and hardware forms. Local issue forms/Discussions links remain. NIPKaart keeps its own ownership and existing sync until its .github is ready. github-config is not ready for archival: remaining local tooling/workflow sources and NIPKaart mappings still have consumers.

These are proposed changes, not completed default-branch maintenance. All existing completion fields are preserved. Gridnet and the template already use shared defaults. Central PRs #1–4 and #6, legacy #443–444, Gridnet #1309–1310, template #578–580 and Glow #1040 are merged. Reusable-workflow PR #5 remains closed without merging.

| Repository | PR | Base |
| --- | --- | --- |
| klaasnicolaas/github-config | [#445](https://github.com/klaasnicolaas/github-config/pull/445) | main |
| klaasnicolaas/home-assistant-glow | [#1041](https://github.com/klaasnicolaas/home-assistant-glow/pull/1041) | develop |
| klaasnicolaas/python-antwerpen | [#1209](https://github.com/klaasnicolaas/python-antwerpen/pull/1209) | main |
| klaasnicolaas/python-arnhem | [#876](https://github.com/klaasnicolaas/python-arnhem/pull/876) | main |
| klaasnicolaas/python-autarco | [#1078](https://github.com/klaasnicolaas/python-autarco/pull/1078) | main |
| klaasnicolaas/python-brussel | [#1190](https://github.com/klaasnicolaas/python-brussel/pull/1190) | main |
| klaasnicolaas/python-dresden | [#1171](https://github.com/klaasnicolaas/python-dresden/pull/1171) | main |
| klaasnicolaas/python-dusseldorf | [#1173](https://github.com/klaasnicolaas/python-dusseldorf/pull/1173) | main |
| klaasnicolaas/python-easyenergy | [#1185](https://github.com/klaasnicolaas/python-easyenergy/pull/1185) | main |
| klaasnicolaas/python-eindhoven | [#1255](https://github.com/klaasnicolaas/python-eindhoven/pull/1255) | main |
| klaasnicolaas/python-eiswarnung | [#1317](https://github.com/klaasnicolaas/python-eiswarnung/pull/1317) | main |
| klaasnicolaas/python-energyzero | [#1219](https://github.com/klaasnicolaas/python-energyzero/pull/1219) | main |
| klaasnicolaas/python-hamburg | [#1196](https://github.com/klaasnicolaas/python-hamburg/pull/1196) | main |
| klaasnicolaas/python-koeln | [#1071](https://github.com/klaasnicolaas/python-koeln/pull/1071) | main |
| klaasnicolaas/python-liege | [#1149](https://github.com/klaasnicolaas/python-liege/pull/1149) | main |
| klaasnicolaas/python-muenster | [#1070](https://github.com/klaasnicolaas/python-muenster/pull/1070) | main |
| klaasnicolaas/python-namur | [#1135](https://github.com/klaasnicolaas/python-namur/pull/1135) | main |
| klaasnicolaas/python-nednl | [#686](https://github.com/klaasnicolaas/python-nednl/pull/686) | main |
| klaasnicolaas/python-odp-amsterdam | [#1280](https://github.com/klaasnicolaas/python-odp-amsterdam/pull/1280) | main |
| klaasnicolaas/python-odp-gent | [#1120](https://github.com/klaasnicolaas/python-odp-gent/pull/1120) | main |
| klaasnicolaas/python-odp-stockholm | [#808](https://github.com/klaasnicolaas/python-odp-stockholm/pull/808) | main |
| klaasnicolaas/python-omnikinverter | [#1353](https://github.com/klaasnicolaas/python-omnikinverter/pull/1353) | main |
| klaasnicolaas/python-p1monitor | [#1256](https://github.com/klaasnicolaas/python-p1monitor/pull/1256) | main |
| klaasnicolaas/python-powerfox | [#841](https://github.com/klaasnicolaas/python-powerfox/pull/841) | main |
| klaasnicolaas/python-solcast-pv | [#587](https://github.com/klaasnicolaas/python-solcast-pv/pull/587) | main |
| klaasnicolaas/python-spoolman | [#425](https://github.com/klaasnicolaas/python-spoolman/pull/425) | main |
| klaasnicolaas/python-weerlive | [#753](https://github.com/klaasnicolaas/python-weerlive/pull/753) | main |
| klaasnicolaas/python-zurich | [#1079](https://github.com/klaasnicolaas/python-zurich/pull/1079) | main |

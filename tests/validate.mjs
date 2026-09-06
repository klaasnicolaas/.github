import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const source = resolve(process.env.RELEASE_DRAFTER_SOURCE || '.validation/release-drafter');
const require = createRequire(`${source}/package.json`);
const { parse } = require('yaml');
const load = (path) => import(pathToFileURL(`${source}/src/${path}`));
const { configSchema } = await load('actions/drafter/config/schemas/config.schema.ts');
const { commonConfigSchema } = await load('actions/drafter/config/schemas/common-config.schema.ts');
const { mergeInputAndConfig } = await load('actions/drafter/config/merge-input-and-config.ts');
const { resolveVersionKeyIncrement } = await load('actions/drafter/lib/build-release-payload/resolve-version-increment.ts');
const { categorizePullRequests } = await load('actions/drafter/lib/build-release-payload/categorize-pull-requests.ts');
const raw = parse(readFileSync('.github/release-drafter-python.yml', 'utf8'));
for (const key of ['version-resolver', 'exclude-labels', 'include-labels', 'exclude-paths']) assert.equal(key in raw, false);
for (const category of raw.categories) {
  assert.equal('labels' in category, false);
  assert.equal('label' in category, false);
}
const config = mergeInputAndConfig({ config: configSchema.parse({ ...raw, commitish: "refs/heads/main" }), input: commonConfigSchema.parse({}) });
const pr = (labels) => ({ title: 'Example change', labels: { nodes: labels.map(name => ({ name })) }, changedFiles: [] });
const scenarios = [
  [[], 'patch'], [['bugfix'], 'patch'], [['maintenance'], 'patch'], [['ci'], 'patch'],
  [['dependencies'], 'patch'], [['documentation'], 'patch'], [['enhancement'], 'patch'],
  [['refactor'], 'patch'], [['performance'], 'patch'], [['chore'], 'patch'],
  [['new-feature'], 'minor'], [['minor'], 'minor'], [['breaking-change'], 'major'],
  [['major'], 'major'], [['minor', 'major'], 'major'], [['new-feature', 'breaking-change'], 'major'],
  [['sync', 'breaking-change'], 'patch'], [['sync', 'major'], 'patch'],
];
for (const [labels, expected] of scenarios) {
  assert.equal(resolveVersionKeyIncrement({ pullRequests: [pr(labels)], config }), expected, labels.join(','));
}
assert.equal(resolveVersionKeyIncrement({ pullRequests: [pr(['dependencies']), pr(['minor']), pr(['major'])], config }), 'major');
const [unmatched, sections] = categorizePullRequests({ pullRequests: [pr(['sync', 'major'])], config });
assert.equal(unmatched.length + sections.reduce((n, section) => n + section.pullRequests.length, 0), 0);
const [, matching] = categorizePullRequests({ pullRequests: [pr(['maintenance', 'dependencies'])], config });
assert.deepEqual(matching.filter(x => x.pullRequests.length).map(x => x.title), ['🧰 Maintenance', '⬆️ Dependency updates']);
assert.equal(raw.categories.find(x => x.title === '⬆️ Dependency updates')['collapse-after'], 5);

const labels = parse(readFileSync('labels/python.yml', 'utf8'));
const names = new Set();
for (const label of labels) {
  assert.equal(typeof label.name, 'string');
  assert(label.name.length <= 50);
  assert(!names.has(label.name.toLowerCase()));
  names.add(label.name.toLowerCase());
  assert(/^[\da-f]{6}$/i.test(String(label.color)), label.name);
  assert(!label.description || label.description.length <= 100);
}
for (const category of raw.categories) {
  const when = category.when || {};
  for (const name of [...(when.labels || []), ...(when.label ? [when.label] : [])]) assert(names.has(name), name);
}
const renovate = JSON.parse(readFileSync('renovate-python.json', 'utf8'));
for (const rule of renovate.packageRules) for (const label of rule.addLabels || []) assert(names.has(label), label);
console.log(`Validated release policy with upstream v7.7.0, ${scenarios.length + 1} version scenarios, category behavior and ${labels.length} consistent labels.`);

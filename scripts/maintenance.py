#!/usr/bin/env python3
"""Preview/apply a maintenance epic and repository sub-issues using authenticated gh."""
import argparse
import json
import subprocess
from pathlib import Path


def graphql(query, **variables):
    result = subprocess.run(
        ['gh', 'api', 'graphql', '--input', '-'],
        input=json.dumps({'query': query, 'variables': variables}),
        text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr + result.stdout)
    data = json.loads(result.stdout)
    if data.get('errors'):
        raise RuntimeError(data['errors'])
    return data['data']


def mutation(name, input_type, values, selection):
    return graphql(
        'mutation($input:' + input_type + '!){' + name +
        '(input:$input){' + selection + '}}', input=values,
    )[name]


def find_issue(issues, marker, title):
    matches = [i for i in issues if marker in i['body'] or i['title'] == title]
    if len(matches) > 1:
        raise ValueError(f'Ambiguous existing issues for {title}; resolve before applying')
    return matches[0] if matches else None


def repository(name):
    owner, repo = name.split('/')
    cursor = None
    issues = []
    while True:
        data = graphql('''query($owner:String!,$name:String!,$cursor:String){
          repository(owner:$owner,name:$name){id nameWithOwner isPrivate
            isArchived hasIssuesEnabled viewerPermission
            issues(first:100,after:$cursor){nodes{id title body url parent{id}}
              pageInfo{hasNextPage endCursor}}
          }}''', owner=owner, name=repo, cursor=cursor)['repository']
        if not data or data['isArchived'] or not data['hasIssuesEnabled']:
            raise ValueError(f'{name}: unavailable, archived or issues disabled')
        if data['viewerPermission'] not in ['ADMIN', 'MAINTAIN', 'WRITE', 'TRIAGE']:
            raise ValueError(f'{name}: insufficient access to manage sub-issues')
        issues.extend(data['issues']['nodes'])
        page = data['issues']['pageInfo']
        if not page['hasNextPage']:
            data['issues'] = issues
            return data
        cursor = page['endCursor']


def project_fields(project):
    return graphql('''query($id:ID!){node(id:$id){... on ProjectV2{
      fields(first:100){nodes{... on ProjectV2Field{id name dataType}
        ... on ProjectV2SingleSelectField{id name options{id name}}}}
    }}}''', id=project)['node']['fields']['nodes']


def field_updates(entry, fields):
    updates = []
    for name, value in entry.get('fields', {}).items():
        field = next(f for f in fields if f['name'] == name)
        if 'options' in field:
            payload = {'singleSelectOptionId': next(
                o['id'] for o in field['options'] if o['name'] == value)}
        elif field['dataType'] == 'TEXT':
            payload = {'text': value}
        else:
            raise ValueError(f'Unsupported field type for {name}')
        updates.append((field['id'], payload))
    return updates


def load_manifest(path):
    manifest = json.loads(path.read_text())
    defaults = manifest.get('task_defaults', {})
    tasks = []
    for task in manifest['tasks']:
        entry = {**defaults, **task}
        entry['fields'] = {**defaults.get('fields', {}), **task.get('fields', {})}
        tasks.append(entry)
    manifest['tasks'] = tasks
    for entry in [manifest['epic'], *tasks]:
        if 'body_file' in entry:
            entry['body'] = (path.parent / entry['body_file']).read_text()
        for key in ['title', 'body']:
            entry[key] = entry[key].replace('{repository}', entry['repository']).replace(
                '{name}', entry['repository'].split('/')[-1])
    return manifest


def run(manifest, apply=False):
    entries = [manifest['epic'], *manifest['tasks']]
    project = manifest['project']
    fields = project_fields(project)
    cache = {}
    plans = []
    markers = set()
    for index, entry in enumerate(entries):
        repo_name = entry['repository']
        if repo_name not in cache:
            cache[repo_name] = repository(repo_name)
        repo = cache[repo_name]
        role = 'epic' if index == 0 else 'task'
        marker = '<!-- maintenance:' + manifest['key'] + ':' + role + ':' + entry.get('key', repo['nameWithOwner']) + ' -->'
        if marker in markers:
            raise ValueError('Multiple tasks in one repository require distinct entry keys')
        markers.add(marker)
        existing = find_issue(repo['issues'], marker, entry['title'])
        draft = None
        if entry.get('draft_item'):
            draft = graphql('''query($id:ID!){node(id:$id){... on ProjectV2Item{
              project{id} content{__typename ... on DraftIssue{id title body}
                ... on Issue{id title body url parent{id}}}
            }}}''', id=entry['draft_item'])['node']
            if not draft or draft['project']['id'] != project:
                raise ValueError('Draft item missing or belongs to another project')
            content = draft['content']
            if content['__typename'] == 'Issue':
                if not existing or content['id'] != existing['id']:
                    raise ValueError('Converted item does not match the intended issue')
            elif content['__typename'] != 'DraftIssue' or existing:
                raise ValueError('Resolve duplicate/unsupported project item before applying')
        updates = field_updates(entry, fields)
        if existing and existing['parent']:
            epic = plans[0]['existing'] if plans else None
            if not epic or existing['parent']['id'] != epic['id']:
                raise ValueError('Existing issue already belongs to another parent')
        action = 'reuse' if existing else 'convert' if draft else 'create'
        print(f'{action}: {repo["nameWithOwner"]} [{"private" if repo["isPrivate"] else "public"}] — {entry["title"]}', flush=True)
        plans.append(dict(entry=entry, repo=repo, existing=existing, marker=marker, updates=updates))
    if not apply:
        print(f'Preview only: 1 epic, {len(manifest["tasks"])} tasks. Use --apply to execute.')
        return
    parent = None
    for plan in plans:
        entry = plan['entry']
        issue = plan['existing']
        reused = issue is not None
        body = entry['body'] + '\n\n' + plan['marker']
        if not issue and entry.get('draft_item'):
            # Supply the reviewed public body before conversion; preserve the project item.
            draft = graphql('query($id:ID!){node(id:$id){... on ProjectV2Item{content{... on DraftIssue{id}}}}}', id=entry['draft_item'])['node']['content']
            mutation('updateProjectV2DraftIssue', 'UpdateProjectV2DraftIssueInput',
                     {'draftIssueId': draft['id'], 'body': body}, 'draftIssue{id}')
            result = mutation('convertProjectV2DraftIssueItemToIssue',
                              'ConvertProjectV2DraftIssueItemToIssueInput',
                              {'itemId': entry['draft_item'], 'repositoryId': plan['repo']['id']},
                              'item{content{... on Issue{id url parent{id}}}}')
            issue = result['item']['content']
        elif not issue:
            issue = mutation('createIssue', 'CreateIssueInput',
                             {'repositoryId': plan['repo']['id'], 'title': entry['title'], 'body': body},
                             'issue{id url parent{id}}')['issue']
        item = mutation('addProjectV2ItemById', 'AddProjectV2ItemByIdInput',
                        {'projectId': project, 'contentId': issue['id']}, 'item{id}')['item']
        # Reruns preserve status, edited descriptions and other progress.
        if not reused:
            for field, value in plan['updates']:
                mutation('updateProjectV2ItemFieldValue', 'UpdateProjectV2ItemFieldValueInput',
                         {'projectId': project, 'itemId': item['id'], 'fieldId': field, 'value': value},
                         'projectV2Item{id}')
        if parent and not issue.get('parent'):
            mutation('addSubIssue', 'AddSubIssueInput',
                     {'issueId': parent['id'], 'subIssueId': issue['id']}, 'issue{id}')
        if parent is None:
            parent = issue
        print(issue['url'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    run(load_manifest(args.manifest), args.apply)

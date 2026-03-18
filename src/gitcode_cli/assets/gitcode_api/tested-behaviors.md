# Tested Behaviors

This file records behavior verified against the live GitCode API during a smoke test on March 6, 2026. Use these notes when live behavior differs from the endpoint examples.

## Verified workflow

The following workflow was executed successfully in a temporary private repository and then cleaned up:

- `POST /api/v5/user/repos`
- `GET /api/v5/repos/{owner}/{repo}`
- `GET /api/v5/repos/{owner}/{repo}/branches`
- `POST /api/v5/repos/{owner}/{repo}/branches`
- `GET /api/v5/repos/{owner}/{repo}/contents/{path}?ref=<branch>`
- `PUT /api/v5/repos/{owner}/{repo}/contents/{path}`
- `POST /api/v5/repos/{owner}/issues`
- `POST /api/v5/repos/{owner}/{repo}/pulls`
- `GET /api/v5/repos/{owner}/{repo}/pulls`
- `GET /api/v5/repos/{owner}/{repo}/issues`
- `DELETE /api/v5/repos/{owner}/{repo}`

## Important behavior notes

### Repository initialization

- Creating a repository with `auto_init=true` creates an initial commit on `main`
- The initialized repository already contains `README.md`
- Because of that, calling `POST /api/v5/repos/{owner}/{repo}/contents/README.md` immediately after creation returns `400`

Observed error body:

```json
{
  "error_code": 400,
  "error_code_name": "UN_KNOW",
  "error_message": "The path cannot be created: README.md ,because README.md already exist."
}
```

Practical rule:

- Use `POST .../contents/{path}` only when the file does not exist
- Use `PUT .../contents/{path}` when the file already exists and include the current `sha`

### Repository consistency right after creation

- Immediately after `POST /api/v5/user/repos`, some follow-up repository endpoints may briefly return `404 project not found`
- In testing, a read-after-create `GET /api/v5/repos/{owner}/{repo}` succeeded before branch creation, and then `POST /api/v5/repos/{owner}/{repo}/branches` succeeded

Practical rule:

- After creating a repository, perform a confirming `GET /api/v5/repos/{owner}/{repo}` before branch or contents operations
- If the repository was just created and a repository-scoped endpoint returns `404`, retry after a short delay instead of assuming the repository name is wrong

### File lookup before update

- `GET /api/v5/repos/{owner}/{repo}/contents/{path}?ref=<branch>` returns the current blob `sha`
- That `sha` can be passed to `PUT /api/v5/repos/{owner}/{repo}/contents/{path}` to update the file on that branch

### Response shape differences seen in practice

- `DELETE /api/v5/repos/{owner}/{repo}` returned `204` with an empty body
- Issue creation returned `number` as a string: `"1"`
- Pull request creation returned `number` as an integer: `1`
- Issue list responses included localized fields such as `issue_state: "待办的"`

Practical rule:

- Do not assume numeric IDs and ordinal fields always share the same type across endpoints
- Parse identifiers defensively

### Branch and pull request behavior

- New personal repositories created during the test used `main` as the default branch
- `POST /api/v5/repos/{owner}/{repo}/branches` with `refs=main` successfully created a feature branch
- `POST /api/v5/repos/{owner}/{repo}/pulls` successfully opened a PR from the feature branch back to `main`
- Passing `milestone_number` when creating a pull request successfully attached the milestone to the PR response

### Form-encoded endpoints

- Label creation was successfully tested with `POST /api/v5/repos/{owner}/{repo}/labels`
- This endpoint expects `application/x-www-form-urlencoded`

Practical rule:

- Do not assume every mutating endpoint accepts JSON
- Check the endpoint reference for request content type

### Issue and pull request label assignment

- `POST /api/v5/repos/{owner}/{repo}/issues/{number}/labels` returned `201` with an array of label objects
- `POST /api/v5/repos/{owner}/{repo}/pulls/{number}/labels` returned `201` with an array of label objects

Practical rule:

- Treat successful label-assignment endpoints as returning arrays, not a single label object
- Do not assume success is always `200`; for these endpoints `201` is expected in practice

### Protected branch rules

- `GET /api/v5/repos/{owner}/{repo}/protect_branches` returned `[]` on a new repository
- `PUT /api/v5/repos/{owner}/{repo}/branches/main/setting` returned `404` with `Protected branch not found`
- `DELETE /api/v5/repos/{owner}/{repo}/branches/main/setting` returned `404` with `main branch or tag not found`

Practical rule:

- Do not use `PUT /branches/{wildcard}/setting` as the first step when there is no existing protected branch rule
- First create the rule with the dedicated create-rule endpoint, then use the update/delete endpoints

### Release upload URLs

- `GET /api/v5/repos/{owner}/{repo}/releases/{tag}/upload_url?file_name=...` returned `200`
- The response contained a signed upload `url` and required `headers`
- The returned callback payload included a callback URL containing the access token used for the request

Practical rule:

- Treat release upload URLs and returned headers as sensitive
- Avoid logging or sharing the full upload URL or callback data in plain text unless necessary

### Pull request comment IDs

- `POST /api/v5/repos/{owner}/{repo}/pulls/{number}/comments` returned `201`
- The response included both a string `id` and an integer `note_id`
- Calling `GET /api/v5/repos/{owner}/{repo}/pulls/comments/{id}` with the string `id` failed with:

```json
{
  "error_message": "Orchestration error: Invalid path parameter: note_id, number required"
}
```

Practical rule:

- For pull request comments, prefer `note_id` when a later endpoint expects a numeric comment identifier

## Suggested agent behavior

- Prefer a read-before-write flow for mutable operations
- Surface the exact HTTP status and body for non-2xx responses
- When a docs example and the live response differ, trust the live response for subsequent steps in the same task

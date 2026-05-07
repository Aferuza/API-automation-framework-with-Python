# ── Authenticated User ─────────────────────────────────────────────────────────
USER            = "/user"               # GET — validate token, fetch authed user

# ── Repository Management ──────────────────────────────────────────────────────
USER_REPOS      = "/user/repos"         # GET list / POST create

REPO            = "/repos/{owner}/{repo}"             # GET / PATCH / DELETE
REPO_BRANCHES   = "/repos/{owner}/{repo}/branches"    # GET — list branches
REPO_ISSUES     = "/repos/{owner}/{repo}/issues"      # GET list / POST create

# ── Collaborators & Permissions (OAuth scope testing) ─────────────────────────
REPO_COLLABORATORS = "/repos/{owner}/{repo}/collaborators/{username}"  # PUT / DELETE
REPO_TOPICS        = "/repos/{owner}/{repo}/topics"   # GET / PUT
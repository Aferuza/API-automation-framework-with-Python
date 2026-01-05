
USER= "/user"
# validates token (get)
AUTH_USER="/user"

USER_REPOS = "/user/repos"
REPO = "/repos/{owner}/{repo}"                # Get, update, delete a specific repo
REPO_BRANCHES = "/repos/{owner}/{repo}/branches"  # List branches (optional workflow test)
REPO_ISSUES = "/repos/{owner}/{repo}/issues"      # Create, list, update issues (optional)

# Additional endpoints for testing advanced OAuth2 / SSO flows
# These can be used to validate scope and token permissions
REPO_COLLABORATORS = "/repos/{owner}/{repo}/collaborators/{username}"  # Add/remove collaborators
REPO_TOPICS = "/repos/{owner}/{repo}/topics"



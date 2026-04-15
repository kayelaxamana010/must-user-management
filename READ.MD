## must-user-management

IaC for managing GitHub teams and AWS IAM users from a single config.
Built with CDKTF (Python). One config change triggers updates to both providers.

### Prerequisites
- Python 3.11+
- Node.js 18+ (for CDKTF CLI)
- AWS credentials with IAM permissions
- GitHub personal access token (admin:org scope)
- S3 bucket for Terraform state

### Getting started

  pip install -r requirements.txt
  cdktf get
  export GITHUB_TOKEN=ghp_...
  export TF_STATE_BUCKET=your-bucket-name
  cdktf deploy --auto-approve   # deploys dev environment by default

### Adding a user

Open config/users.yaml and add an entry:

  - name: diana
    github_username: diana-gh
    github_team: backend      # must match a team defined in github.teams
    aws_account: dev          # must match a key in aws.accounts

Push to main. The CI pipeline handles the rest.

### Removing a user

Delete their entry from config/users.yaml and push to main.

### Environments

  DEPLOY_ENV=dev  cdktf deploy   # default
  DEPLOY_ENV=prod cdktf deploy

### Assumptions

- GitHub usernames are placeholders; real accounts must exist in the org.
- AWS accounts share a single region (ap-southeast-1, configurable via AWS_REGION).
- Terraform state is stored in S3 with encryption enabled.
- AWS auth uses OIDC in CI; locally, use aws-vault or standard credential chain
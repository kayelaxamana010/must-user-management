#!/usr/bin/env python3
import yaml
import os
from constructs import Construct
from cdktf import App, TerraformStack, S3Backend
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_github.provider import GithubProvider
from components.github_component import GitHubTeamComponent
from components.aws_component import AWSUserComponent


def load_config(path: str = "config/users.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


class UserManagementStack(TerraformStack):
    def __init__(self, scope: Construct, id: str,
                 config: dict, env: str = "dev"):
        super().__init__(scope, id)

        # Remote state — keeps Terraform state off local disk
        S3Backend(
            self,
            bucket=os.environ.get("TF_STATE_BUCKET", "must-cdktf-state"),
            key=f"user-management/{env}/terraform.tfstate",
            region=os.environ.get("AWS_REGION", "ap-southeast-1"),
            encrypt=True,
        )

        # Providers — credentials injected via environment variables
        AwsProvider(self, "aws",
            region=os.environ.get("AWS_REGION", "ap-southeast-1"))

        GithubProvider(self, "github",
            owner=config["github"]["org"],
            token=os.environ.get("GITHUB_TOKEN"))

        # Components
        GitHubTeamComponent(
            self, "github-teams",
            org=config["github"]["org"],
            teams_config=config["github"]["teams"],
            users=config["users"],
        )

        AWSUserComponent(
            self, "aws-users",
            accounts_config=config["aws"]["accounts"],
            users=config["users"],
            env=env,
        )


if __name__ == "__main__":
    app = App()
    config = load_config()
    env = os.environ.get("DEPLOY_ENV", "dev")
    UserManagementStack(app, f"user-management-{env}",
                        config=config, env=env)
    app.synth()
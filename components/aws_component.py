from constructs import Construct
from cdktf import TerraformOutput
from cdktf_cdktf_provider_aws.iam_user import IamUser
from cdktf_cdktf_provider_aws.iam_group import IamGroup
from cdktf_cdktf_provider_aws.iam_group_membership import IamGroupMembership
from cdktf_cdktf_provider_aws.iam_group_policy_attachment import (
    IamGroupPolicyAttachment
)


class AWSUserComponent(Construct):
    """
    Creates IAM users and assigns them to account-scoped groups.
    All resources are tagged with env + team for visibility.
    Policies are attached at the group level (least-privilege pattern).
    """

    def __init__(self, scope: Construct, id: str,
                 accounts_config: dict, users: list, env: str = "dev"):
        super().__init__(scope, id)

        self.iam_users: dict[str, IamUser] = {}
        self.groups: dict[str, IamGroup] = {}

        # Create IAM groups and attach policies
        for account_name, cfg in accounts_config.items():
            group = IamGroup(
                self, f"group-{account_name}",
                name=f"must-{cfg['group_name']}-{env}",
            )
            self.groups[account_name] = group

            for idx, policy_arn in enumerate(cfg.get("policies", [])):
                IamGroupPolicyAttachment(
                    self, f"policy-{account_name}-{idx}",
                    group=group.name,
                    policy_arn=policy_arn,
                )

        # Create IAM users and collect group assignments
        group_members: dict[str, list[str]] = {
            k: [] for k in accounts_config
        }

        for user in users:
            iam_name = f"must-{user['name']}-{env}"
            iam_user = IamUser(
                self, f"iam-user-{user['name']}",
                name=iam_name,
                tags={
                    "env": env,
                    "team": user["github_team"],
                    "managed_by": "cdktf",
                },
            )
            self.iam_users[user["name"]] = iam_user

            acct = user["aws_account"]
            if acct not in group_members:
                raise ValueError(
                    f"AWS account '{acct}' not defined for user '{user['name']}'"
                )
            group_members[acct].append(iam_name)

            TerraformOutput(
                self, f"iam-arn-{user['name']}",
                value=iam_user.arn,
                description=f"IAM ARN for {user['name']}",
            )

        # Bulk assign users to their groups
        for account_name, members in group_members.items():
            if members:
                IamGroupMembership(
                    self, f"group-membership-{account_name}",
                    name=f"must-{account_name}-members-{env}",
                    users=members,
                    group=self.groups[account_name].name,
                )
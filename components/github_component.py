from constructs import Construct
from cdktf import TerraformOutput
from cdktf_cdktf_provider_github.team import Team
from cdktf_cdktf_provider_github.team_membership import TeamMembership


class GitHubTeamComponent(Construct):
    """
    Creates GitHub teams and assigns users based on config.
    Each team is prefixed with 'must-' to enforce naming conventions.
    """

    def __init__(self, scope: Construct, id: str,
                 org: str, teams_config: list, users: list):
        super().__init__(scope, id)

        self.teams: dict[str, Team] = {}

        # Create each team from config
        for team_cfg in teams_config:
            team_name = team_cfg["name"]
            team = Team(
                self, f"team-{team_name}",
                name=f"must-{team_name}",
                description=team_cfg.get("description", ""),
                privacy=team_cfg.get("privacy", "closed"),
            )
            self.teams[team_name] = team
            TerraformOutput(
                self, f"team-{team_name}-id",
                value=team.id,
                description=f"GitHub team ID for {team_name}",
            )

        # Assign each user to their team
        for user in users:
            team_name = user["github_team"]
            if team_name not in self.teams:
                raise ValueError(
                    f"Team '{team_name}' not defined in config"
                    f" for user '{user['name']}'"
                )
            TeamMembership(
                self, f"membership-{user['name']}",
                team_id=self.teams[team_name].id,
                username=user["github_username"],
                role="member",
            )
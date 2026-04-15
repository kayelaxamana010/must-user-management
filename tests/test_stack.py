import pytest
import yaml
from pathlib import Path


def load_config():
    path = Path(__file__).parent.parent / "config" / "users.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def test_config_has_required_top_level_keys():
    config = load_config()
    for key in ("users", "github", "aws"):
        assert key in config, f"Missing top-level key: {key}"


def test_all_users_have_required_fields():
    config = load_config()
    required = {"name", "github_username", "github_team", "aws_account"}
    for user in config["users"]:
        missing = required - set(user.keys())
        assert not missing, (
            f"User '{user.get('name')}' is missing fields: {missing}"
        )


def test_github_teams_referenced_are_defined():
    config = load_config()
    valid = {t["name"] for t in config["github"]["teams"]}
    for user in config["users"]:
        assert user["github_team"] in valid, (
            f"User '{user['name']}' references undefined team '{user['github_team']}'"
        )


def test_aws_accounts_referenced_are_defined():
    config = load_config()
    valid = set(config["aws"]["accounts"].keys())
    for user in config["users"]:
        assert user["aws_account"] in valid, (
            f"User '{user['name']}' references undefined account '{user['aws_account']}'"
        )


def test_no_duplicate_user_names():
    config = load_config()
    names = [u["name"] for u in config["users"]]
    assert len(names) == len(set(names)), "Duplicate user names found"


def test_no_duplicate_github_usernames():
    config = load_config()
    handles = [u["github_username"] for u in config["users"]]
    assert len(handles) == len(set(handles)), "Duplicate GitHub usernames found"
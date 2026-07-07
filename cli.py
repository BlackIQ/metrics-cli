#!/usr/bin/env python3

import requests
import typer
from art import text2art
from rich.console import Console
from rich_gradient import Gradient
from termcolor import cprint

from settings import settings

app = typer.Typer(
    help="OpenHubble CLI",
    no_args_is_help=True,
    add_completion=False,
)

console = Console()


# -------------------------------------------------------------------
# UI
# -------------------------------------------------------------------

def print_art():
    openhubble_art = text2art("OpenHubble")
    cli_art = text2art("CommandLine")

    palette = [
        "#3674B5",
        "#578FCA",
        "#A1E3F9",
        "#D1F8EF",
    ]

    print()

    console.print(
        Gradient(openhubble_art, colors=palette, justify="center")
    )

    console.print(
        Gradient(cli_art, colors=palette[::-1], justify="center")
    )


@app.callback()
def main():
    """
    OpenHubble CLI
    """
    check_for_updates()


# -------------------------------------------------------------------
# GitHub
# -------------------------------------------------------------------

def get_github_releases():
    response = requests.get(
        "https://api.github.com/repos/OpenHubble/cli/releases"
    )
    response.raise_for_status()
    return response.json()


def compare_versions(current_version, releases):
    latest = releases[0]

    if latest["tag_name"] == current_version:
        return None

    return f"""
+-----------------------------------------------+
| New version available!
|
| {latest["name"]}
| Version: {latest["tag_name"]}
| Release: {latest["html_url"]}
+-----------------------------------------------+
"""


def ask_user_to_update(current_version):
    if typer.confirm(
            f"You are using {current_version}. Update now?"
    ):
        update(False)
    else:
        cprint(
            "Run 'openhubble update' whenever you're ready.",
            "yellow",
        )


def check_for_updates():
    current = settings.project_version

    releases = get_github_releases()

    msg = compare_versions(current, releases)

    if msg:
        cprint(msg, "green")
        ask_user_to_update(current)


# -------------------------------------------------------------------
# Commands
# -------------------------------------------------------------------

@app.command()
def version():
    """Show version."""
    cprint(
        f"OpenHubble CLI {settings.project_version}",
        "cyan",
        attrs=["bold"],
    )


@app.command()
def update(confirm: bool = True):
    """Update the CLI."""

    current = settings.project_version
    releases = get_github_releases()

    latest = releases[0]["tag_name"]

    if latest == current:
        cprint(
            f"Already using latest version ({current})",
            "yellow",
        )
        raise typer.Exit()

    cprint(f"Updating to {latest}", "blue")

    if confirm:
        if not typer.confirm("Continue?"):
            cprint("Aborted.", "yellow")
            raise typer.Exit()

    # subprocess.run(
    #     ["sudo", Path("/opt/openhubble-cli/scripts/update.sh")],
    #     check=True,
    )

    cprint("Updated successfully.", "green") \

    @ app.command()


def uninstall():
    """Uninstall OpenHubble."""

    if not typer.confirm("Really uninstall?"):
        cprint("Aborted.", "yellow")
        raise typer.Exit()

    # subprocess.run(
    #     ["sudo", Path("/opt/openhubble-cli/scripts/uninstall.sh")],
    #     check=True,
    # )

    cprint("Uninstalled successfully.", "green")


@app.command()
def ping(
        host: str = "127.0.0.1",
        port: str = "9703",
        key: str = "apikey",
        protocol: str = typer.Option(
            "https",
            "--protocol",
            help="http or https",
        ),
):
    """Ping the agent."""

    url = f"{protocol}://{host}:{port}/api/ping"

    try:
        r = requests.get(
            url,
            headers={"X-API-KEY": key},
        )

        r.raise_for_status()

        if r.json().get("message") == "pong":
            cprint("Agent is running.", "green")
        else:
            cprint("Unexpected response.", "yellow")

    except requests.RequestException as e:
        cprint(f"Error: {e}", "red")


@app.command("get")
def get_metric_command(
        host: str = "127.0.0.1",
        port: str = "9703",
        key: str = "apikey",
        metric: str = "hostname",
        protocol: str = typer.Option(
            "https",
            "--protocol",
        ),
):
    """Get a metric."""

    url = (
        f"{protocol}://{host}:{port}"
        f"/api/get?metric={metric}"
    )

    try:
        r = requests.get(
            url,
            headers={"X-API-KEY": key},
        )

        r.raise_for_status()

        data = r.json()

        if "metric" in data:
            cprint(f"Metric: {data['metric']}", "green")
        else:
            cprint("Unexpected response.", "yellow")

    except requests.RequestException as e:
        cprint(f"Error: {e}", "red")


@app.command()
def help():
    """Show custom help."""
    print_art()
    typer.echo(app.get_help())


if __name__ == "__main__":
    app()

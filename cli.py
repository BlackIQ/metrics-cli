#!/usr/bin/python3

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer
from art import text2art
from rich.console import Console
from rich_gradient import Gradient
from termcolor import cprint

from settings import settings
from utils.metric import get_metric
from utils.ping import ping_agent
from utils.uninstall import uninstall_function
from utils.update import update_function

app = typer.Typer(
    help="OpenHubble CLI",
    no_args_is_help=True,
    add_completion=True,
)

console = Console()


@dataclass
class AgentConfig:
    host: str = "127.0.0.1"
    port: int = 9703
    key: str = "apikey"
    use_https: bool = False


def load_config(path: Path | None) -> AgentConfig:
    config = AgentConfig()

    if path is None:
        return config

    with path.open("rb") as f:
        data = tomllib.load(f)

    return AgentConfig(
        host=data.get("host", config.host),
        port=data.get("port", config.port),
        key=data.get("key", config.key),
        use_https=data.get("use_https", config.use_https),
    )


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


def show_version(value: bool):
    if value:
        cprint(
            f"OpenHubble CLI {settings.project_version}",
            "cyan",
            attrs=["bold"],
        )

        raise typer.Exit()


@app.callback()
def main(
        version: Annotated[
            bool | None,
            typer.Option(
                "--version", "-v",
                callback=show_version,
                is_eager=True,
                help="Show application version"
            )
        ] = None
):
    pass


@app.command("version", rich_help_panel="CLI", help="Show application version")
def version():
    show_version()


@app.command("update", rich_help_panel="CLI", help="Update application")
def update():
    update_function()


@app.command("uninstall", rich_help_panel="CLI", help="Uninstall application")
def uninstall():
    uninstall_function()


@app.command("ping", rich_help_panel="Agent", help="Ping Agent server")
def ping(
        host: Annotated[
            str, typer.Option(
                "--host", "-H",
                help="Host running Agent",
                prompt="Enter Agent host"
            )
        ] = "127.0.0.1",
        port: Annotated[
            int, typer.Option(
                "--port", "-P",
                help="Port that Agent expose",
                prompt="Enter Agent port"
            )
        ]
        = 9703,
        key: Annotated[
            str, typer.Option(
                "--key", "-K",
                help="API Key you defined in Agent",
                prompt="Enter the Agent API Key"
            )
        ] = "apikey",
        use_https: Annotated[
            bool, typer.Option(
                "--use-https",
                help="Use connection over HTTPS with Agent",
                prompt="Do you want to use HTTPS",
            )
        ] = False,
):
    ping_agent(host, port, key, use_https)


@app.command("pimgf", rich_help_panel="Agent", help="Ping Agent server with a file")
def pingf(
        config_file: Annotated[
            Path | None,
            typer.Option(
                "--file", "-F",
                help="Load Agent configuration from a TOML file",
                exists=True,
                readable=True,
            ),
        ] = None,
):
    conf = load_config(config_file)

    host = conf.host
    port = conf.port
    key = conf.key
    use_https = conf.use_https

    ping_agent(host, port, key, use_https)


@app.command("get", rich_help_panel="Agent", help="Get metric from agent")
def get_metric_command(
        host: Annotated[
            str, typer.Option(
                "--host", "-H",
                help="Host running Agent",
                prompt="Enter Agent host"
            )
        ] = "127.0.0.1",
        port: Annotated[
            int, typer.Option(
                "--port", "-P",
                help="Port that Agent expose",
                prompt="Enter Agent port"
            )
        ]
        = 9703,
        key: Annotated[
            str, typer.Option(
                "--key", "-K",
                help="API Key you defined in Agent",
                prompt="Enter the Agent API Key"
            )
        ] = "apikey",
        use_https: Annotated[
            bool, typer.Option(
                "--use-https",
                help="Use connection over HTTPS with Agent",
                prompt="Do you want to use HTTPS",
                is_eager=True
            )
        ] = False,
        metric: Annotated[
            str, typer.Option(
                "--metric", "-M",
                help="Metric you want to get from Agent",
                prompt="Enter the metric"
            )
        ] = "agent.hostname"
):
    get_metric(host, port, key, use_https, metric)


if __name__ == "__main__":
    app()

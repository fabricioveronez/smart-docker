import os
import sys
import argparse

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown

from src.tools import get_tools
from src.prompt import SYSTEM_PROMPT

# Carrega .env da raiz do projeto (diretório pai de src/)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

console = Console()

BANNER = r"""
 ____                       _   ____             _
/ ___| _ __ ___   __ _ _ __| |_|  _ \  ___   ___| | _____ _ __
\___ \| '_ ` _ \ / _` | '__| __| | | |/ _ \ / __| |/ / _ \ '__|
 ___) | | | | | | (_| | |  | |_| |_| | (_) | (__|   <  __/ |
|____/|_| |_| |_|\__,_|_|   \__|____/ \___/ \___|_|\_\___|_|
"""


def show_banner():
    banner_text = Text(BANNER, style="bold cyan")
    subtitle = Text("Analise inteligente de Dockerfiles", style="italic white")
    banner_text.append("\n")
    banner_text.append(subtitle)
    console.print(Panel(banner_text, border_style="cyan"))


def main():
    parser = argparse.ArgumentParser(
        description="SmartDocker - Analise inteligente de Dockerfiles"
    )
    parser.add_argument("caminho", help="Caminho do diretorio raiz do projeto")
    # Diretório raiz do projeto (pai de src/)
    projeto_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_output = os.path.join(projeto_dir, "relatorio.md")

    parser.add_argument(
        "-o", "--output",
        default=default_output,
        help="Caminho do arquivo de relatorio (padrao: relatorio.md na raiz)",
    )
    args = parser.parse_args()

    caminho = os.path.abspath(args.caminho)

    show_banner()

    if not os.path.isdir(caminho):
        console.print(f"[bold red]Erro: '{caminho}' nao e um diretorio valido.[/bold red]")
        sys.exit(1)

    console.print(f"[bold cyan]Projeto:[/bold cyan] {caminho}\n")

    llm = ChatGoogleGenerativeAI(model="gemini-3-pro-preview")

    tools = get_tools(caminho)

    agent = create_agent(
        llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )

    with console.status("[bold cyan]Investigando estrutura do projeto...", spinner="dots"):
        resultado = agent.invoke(
            {"messages": [("human", f"Analise o projeto no diretorio: {caminho}")]},
        )

    conteudo = resultado["messages"][-1].content

    if isinstance(conteudo, list):
        relatorio = "\n".join(
            bloco.get("text", "") if isinstance(bloco, dict) else str(bloco)
            for bloco in conteudo
        )
    else:
        relatorio = conteudo

    console.print()
    console.rule(style="cyan")
    console.print()
    console.print(Markdown(relatorio))
    console.print()
    console.rule(style="cyan")
    console.print()

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(relatorio)

    console.print(Panel(
        f"[bold green]Relatorio salvo em:[/bold green] {args.output}",
        border_style="green",
    ))


if __name__ == "__main__":
    main()

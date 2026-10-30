import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

api_url = "https://de.wikipedia.org/w/api.php"
headers = {"User-Agent": "WikiRaceHalloween"}

ziel = "Halloween"

console = Console()

def get_random_start_page():
    params = {
        "action": "query",
        "format": "json",
        "list": "random",
        "rnlimit": 1,
        "rnnamespace": 0,
        "rnfilterredir": "nonredirects",
        "rnminsize": 500
    }

    response = requests.get(api_url, params=params, headers=headers)
    response.raise_for_status()
    response_json = response.json()

    return response_json["query"]["random"][0]["title"]


def get_links(wikipage):
    links = []

    params = {
        "action": "query",
        "format": "json",
        "formatversion": 2,
        "generator": "links",
        "titles": wikipage,
        "prop": "info",
        "gplnamespace": 0,
        "gpllimit": "max"
    }

    while True:
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        response_json = response.json()

        for page in response_json.get("query", {}).get("pages", []):
            if "missing" not in page:
                links.append(page["title"])

        if "continue" not in response_json:
            break

        params.update(response_json["continue"])

    return sorted(set(links), key=str.casefold)


def main():
    try:
        start_wikipage = get_random_start_page()

        if start_wikipage.casefold() == ziel.casefold():
            start_wikipage = get_random_start_page()
    except (requests.RequestException, ValueError, KeyError, IndexError) as error:
        print(f"Fehler beim start: {error}")
        return

    click_count = 0
    max_links_to_show = 20

    while True:
        try:
            links = get_links(start_wikipage)
        except (requests.RequestException, ValueError, KeyError, IndexError) as error:
            print(f"Fehler beim start: {error}")
            return

        page = 0


        while True:
            start = page * max_links_to_show
            visible_links = links[start:start + max_links_to_show]
            total_pages = max(1, (len(links) + max_links_to_show - 1) // max_links_to_show)


            console.clear()
            console.print("[bold red]WIKI RACE[/bold red]\n")


            console.print(
                Panel(
                    start_wikipage,
                    title="Aktuelle Seite",
                    border_style="yellow",
                )
            )

            console.print(
                f"[green]Ziel:[/green] {ziel}"
                f"  |  [blue]Klicks:[/blue] {click_count}\n"
            )

            table = Table(title=f"Links ({len(links)})")
            table.add_column("Nr.", style="cyan")
            table.add_column("Seite", style="cyan")

            for index, title in enumerate(visible_links, start=1):
                table.add_row(str(index), title)

            console.print(table)

            console.print(f"\nSeite {page + 1}/{total_pages}")

            console.print("\n[cyan]Zahl[/cyan] = Seite öffnen")

            console.print(
                "[cyan]w[/cyan] = Weiter"
                " | [cyan]s[/cyan] = Zurück"
                " | [cyan]r[/cyan] = Neustart"
                " | [cyan]q[/cyan] = Beenden"
            )

            choice = console.input("\n[bold yellow]> [/bold yellow]").strip()

            if choice.lower() == "q":
                return

            elif choice.lower() == "r":
                try:
                    start_wikipage = get_random_start_page()
                    if start_wikipage.casefold() == ziel.casefold():
                        start_wikipage = get_random_start_page()
                except (requests.RequestException, ValueError, KeyError, IndexError) as error:
                    console.print(f"Error beim neustart {error}")
                    return

                click_count = 0
                break

            elif choice.lower() == "w":
                if page + 1 < total_pages:
                    page += 1

            elif choice.lower() == "s":
                if page > 0:
                    page -= 1

            elif choice.isdigit():
                index = int(choice) - 1

                if 0 <= index < len(visible_links):
                    start_wikipage = visible_links[index]
                    click_count += 1

                    if start_wikipage.casefold() == ziel.casefold():
                        console.clear()
                        console.print(
                            Panel(
                                f"[bold green]Halloween erreicht![/bold green]\n\n"
                                f"Benötigte Klicks: {click_count}\n\n"
                                "https://de.wikipedia.org/wiki/Halloween",
                                title="WIKI Halloween Race Gewonnen!",
                                border_style="green",
                            )
                        )
                        return

                    break

if __name__ == "__main__":
    main()

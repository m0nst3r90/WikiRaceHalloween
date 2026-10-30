import requests

api_url = "https://de.wikipedia.org/w/api.php"
headers = {"User-Agent": "WikiRaceHalloween"}

ziel = "Halloween"

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









if __name__ == "__main__":
    main()

#!/usr/bin/env python3

"""
Make data Lansing, Michigan from World Historical Gazetteer and Michigan Memories
available to teachers as they create lesson plans in the OER Commons Editor.

queries:
* whg Lansing, Michigan
* michmemories Lansing river images
* worldbank Health Service Delivery
"""

import asyncio

import httpx
from bs4 import BeautifulSoup


def dbpedia(page: str) -> str:
    soup = BeautifulSoup(page, "html.parser")
    return soup.find("span", {"property": "dbo:abstract", "lang": "en"}).text


def decolonialatlas(page: str) -> str:
    page = "\n".join(line for line in page.splitlines() if "Lansing" in line)
    return BeautifulSoup(page, "html.parser").text


def getty(page: str) -> str:
    """
    <TD COLSPAN=5><SPAN CLASS=page><BR><B>Note: </B>Located on Grand river where it joins the Red Cedar river; site was wilderness in 1847 when state capital was moved here; grew with arrival of railroad & development of motor industry in 1880s; now produces automobiles.</SPAN></TD></TR>
    """
    page = "\n".join(line for line in page.splitlines() if "<B>Note: </B>" in line)
    return BeautifulSoup(page, "html.parser").text


async def fetch_text(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch {url}: {response.status_code}")
            return ""


async def whgazetteer():
    urls = (
        # "https://michmemories.org/exhibits/default/catalog?q=lansing",
        # "https://whgazetteer.org/places/14156749/portal",
        "https://www.getty.edu/vow/TGNFullDisplay?find=Michigan&place=&nation=&prev_page=1&english=Y&subjectid=2052433",
        "https://decolonialatlas.wordpress.com/turtle-island-decolonized/",
        # "https://dbpedia.org/page/Lansing,_Michigan",
    )

    tasks = [fetch_text(url) for url in urls]
    results = await asyncio.gather(*tasks)

    funcs = {func.__name__: func for func in (decolonialatlas, dbpedia, getty)}
    for url, result in zip(urls, results):
        if result:
            for func in funcs:
                if func in url:
                    result = funcs[func](result)
                    break
            print(f"Text from {url}:\n\n{result}\n\n{'='*50}\n")
        else:
            print(f"Failed to fetch text from {url}")


if __name__ == "__main__":
    # from pathlib import Path
    from subprocess import run
    from time import sleep
    from webbrowser import open_new_tab

    # Type: whg Lansing, Michigan
    print("whg: World Historical Gazetteer")
    print("michmem: Michigan Memories\n")
    _ = input("Search: (ex. 'whg Canada') ")
    sleep(2)

    print(
        "3 World Historical Gazetteer datasets found: Getty, Decolonial Atlas, DBpedia\n"
    )
    open_new_tab("https://whgazetteer.org/places/14156749/portal")
    print("Parsing 3 sources...\n")
    sleep(2)
    asyncio.run(whgazetteer())

    # Type: michmem Lansing river images
    _ = input("Search: (ex. 'whg Canada') ")
    print("4 Michigan Memories selected: Lansing river images\n")
    open_new_tab(
        "https://michmemories.org/exhibits/default/catalog?q=Lansing+river+images"
    )
    sleep(2)
    run("open *.jpg", shell=True)
    # for i, image_file in enumerate(Path(__file__).glob("*.jpg")):
    #    print(f"Opening {image_file}...")
    #    sleep(1)
    #    run(["open", image_file])

    # Type: worldbank Health Service Delivery
    #
    _ = input("Search: (ex. 'whg Canada') ")
    print(
        "1 Worldbank pdf file: The Power of Data Collection on Health Service Delivery\n"
    )
    open_new_tab(
        "https://openknowledge.worldbank.org/bitstreams/a34428a8-81c0-4c98-88b8-a5637bc5fde8/download"
    )
    # sleep(2)
    # run("open *.jpg", shell=True)
    # for i, image_file in enumerate(Path(__file__).glob("*.jpg")):
    #    print(f"Opening {image_file}...")
    #    sleep(1)
    #    run(["open", image_file])
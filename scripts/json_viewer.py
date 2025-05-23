#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "fastapi",
#     "httpx",
#     "jinja2",
#     "pydantic",
#     "toga",
#     "uvicorn",
# ]
# ///

from __future__ import annotations

import json
import os
import threading
import time
import webbrowser

# from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

# from .json_viewer_models import Model

# generated by datamodel-codegen:
#   filename:  json_viewer.json
#   timestamp: 2025-04-15T07:35:16+00:00


class Highlight(BaseModel):
    snippet: list[str]
    title: list[str] | None = None


class Highlight1(BaseModel):
    snippet: list[str]


class Duplicate(BaseModel):
    url: str
    surt_url: str
    host: str
    domain: str
    tld: str
    first_captured: str
    snippet: str
    title: str
    content_type: str
    highlight: Highlight1


class Hit(BaseModel):
    url: str
    surt_url: str
    host: str
    domain: str
    tld: str
    first_captured: str  # datetime
    snippet: str
    title: str
    content_type: str
    highlight: Highlight
    duplicates: list[Duplicate] | None = None


class PublicationDate(BaseModel):
    field_2011_10: int = Field(..., alias="2011-10")
    field_2011_12: int = Field(..., alias="2011-12")
    field_2015_08: int = Field(..., alias="2015-08")
    field_2017_11: int = Field(..., alias="2017-11")


class Tlds(BaseModel):
    org: int


class Domains(BaseModel):
    iskme_org: int = Field(..., alias="iskme.org")


class Languages(BaseModel):
    en: int
    it: int


class Aggregations(BaseModel):
    publication_date: PublicationDate
    tlds: Tlds
    domains: Domains
    is_seed: dict[str, Any]
    languages: Languages
    first_captured_year: dict[str, Any]


class Model(BaseModel):
    total: int
    hits: list[Hit]
    aggregations: Aggregations


# If the json file does not exist, fetch it via the URL environment variable.
if not (json_file := Path(__file__).with_suffix(".json")).exists():
    if not (url := os.getenv("URL")):
        msg = "Please set the URL environment variable"
        raise ValueError(msg)

    if not (json_payload := httpx.get(url).raise_for_status().json()):
        msg = f"Failed to fetch JSON payload from {url=}"
        raise ValueError(msg)

    json_file.write_text(json.dumps(json_payload, indent=2))

# uv tool run --from=datamodel-code-generator datamodel-codegen \
#             --input json_viewer.json --input-file-type json \
#             --output json_viewer_models.py

model = Model.model_validate_json(json_file.read_text())
app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def read_hit(request: Request, index: int = 0) -> HTMLResponse:
    index = max(0, min(index, len(model.hits) - 1))
    hit = model.hits[index]
    return templates.TemplateResponse(
        "hit_table.html",
        {
            "request": request,
            "hit": hit,
            "index": index,
            "has_prev": index > 0,
            "has_next": index < len(model.hits) - 1,
            "hits_len": len(model.hits),
        },
    )


def run_server() -> None:
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    Path("templates").mkdir(exist_ok=True)
    Path("templates/hit_table.html").write_text("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hit Viewer</title>
        <style>
            body { font-family: sans-serif; padding: 2rem; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 2rem; }
            th, td { padding: 0.5rem; border: 1px solid #ccc; }
            th { background-color: #f4f4f4; text-align: left; }
            .nav-buttons a {
                margin: 0.5rem;
                padding: 0.5rem 1rem;
                text-decoration: none;
                border: 1px solid #ccc;
                background-color: #eee;
                color: black;
                border-radius: 5px;
            }
            .nav-buttons a.disabled {
                pointer-events: none;
                opacity: 0.5;
            }
        </style>
    </head>
    <body>
        <h1>Hit {{ index + 1 }} of {{ hits_len }}: {{ hit.dict()["title"] }}</h1>
        <table>
            <tbody>
                {% for field, value in hit.dict().items() if field in
                    ("url", "snippet", "highlight", "duplicates")
                %}
                    <tr>
                        <th>{{ field }}</th>
                        <td>{{ value }}</td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
        <div class="nav-buttons">
            {% if has_prev %}
                <a href="/?index={{ index - 1 }}">Previous</a>
            {% else %}
                <a class="disabled">Previous</a>
            {% endif %}
            {% if has_next %}
                <a href="/?index={{ index + 1 }}">Next</a>
            {% else %}
                <a class="disabled">Next</a>
            {% endif %}
        </div>
    </body>
    </html>
    """)

    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8000")

    server_thread.join()  # Keep the server running until the user presses Ctrl+C twice

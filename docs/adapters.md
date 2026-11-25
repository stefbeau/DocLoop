# Adapters: where your docs live

Every tool reads and writes pages through a `PageStore`. Two ship with the
project.

| Store | Use it when | Page id |
| --- | --- | --- |
| `GitMarkdownStore` | Docs are `.md` or `.mdx` files in a repository | Path under the docs folder, without the extension |
| `JsonCmsStore` | Docs live in a content system you can export to JSON | The system's own page id |

`open_store(path)` picks one: a folder opens as Markdown, a `.json` file as a
CMS export.

## The JSON export shape

```json
{ "pages": [ { "id": "1042", "title": "Exporting data", "body": "...",
               "visibility": "public", "url": "https://help.example.com/1042" } ] }
```

## Writing a live adapter

To talk to a content system directly, subclass `PageStore` and implement four
methods. Everything else, including the gate, works unchanged.

```python
from docloop.models import Page
from docloop.stores import PageStore

class MyCmsStore(PageStore):
    def __init__(self, client):
        self.client = client

    def list_ids(self) -> list[str]:
        return [str(p["id"]) for p in self.client.list_pages()]

    def get(self, page_id: str) -> Page:
        p = self.client.get_page(page_id)          # raise KeyError if missing
        return Page(id=str(p["id"]), title=p["title"], body=p["body"],
                    visibility=p["visibility"], location=p["url"])

    def write(self, page_id: str, body: str) -> None:
        self.client.update_page(page_id, body)      # called only by `apply`, after approval

    def exists(self, page_id: str) -> bool:        # optional: override if listing is slow
        return self.client.page_exists(page_id)
```

Then pass it in: `Workspace(MyCmsStore(client))`.

Two things to keep true in any adapter:

- `get` must raise `KeyError` for an id that does not exist. The rule that no
  invented page id gets through depends on it.
- `write` is the only method that changes anything, and only `apply` calls it.

## Change events

A change event is a JSON file:

```json
{ "id": "retire-csv", "title": "...", "body": "...",
  "comments": ["..."], "labels": ["deprecation"], "source": "pull_request" }
```

Map whatever you have onto it: a pull request (title, description, review
comments, labels), an issue, a release-note entry, or a ticket. Include the
comments. The request for a customer notice is often made there.

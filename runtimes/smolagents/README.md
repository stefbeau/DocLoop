# Runtime 3: smolagents

The same core and the same skills, driven by Hugging Face's `smolagents`.

- **Lead:** a `ToolCallingAgent` whose instructions are the `docs-change-lead` skill.
- **Subagent:** a managed agent, `page_drafter`, with four tools.
- **Skills:** loaded on demand through a `load_skill` tool.

## Run locally

```
pip install -r runtimes/smolagents/requirements.txt
export HF_TOKEN=...            # a Hugging Face token with inference access
python runtimes/smolagents/app.py
```

Then ask: `Handle the change event in examples/events/retire-csv.json`.

Set `DOCLOOP_MODEL` to choose a model id and `DOCLOOP_DOCS` to point at your own docs.

## Deploy as a Space

Create a Gradio Space and copy into it: `runtimes/smolagents/app.py` and
`requirements.txt` at the top level, plus the `docloop/`, `skills/` and
`examples/` folders. Add `HF_TOKEN` as a secret.

## What has been verified

The tools and both agents are constructed in the test suite. A full run needs a
model endpoint and was not exercised in the test suite.

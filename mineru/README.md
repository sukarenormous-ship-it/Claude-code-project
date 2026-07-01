# MinerU

[MinerU](https://github.com/opendatalab/MinerU) converts PDF, DOCX, PPTX, XLSX
and images into structured **Markdown / JSON** (handles complex layouts, scanned
pages, formulas → LaTeX, tables → HTML, 100+ languages).

Everything here is self-contained in this `mineru/` folder and does **not** touch
the JavaScript project in the repository root.

## Install

```bash
bash mineru/setup.sh
```

This creates `mineru/.venv/` (git-ignored, ~5 GB) and installs `mineru[core]`.
Installed version in this environment: **3.4.0** (Python 3.11).

## Use

```bash
# Convert a document (CPU-friendly pipeline backend)
bash mineru/run.sh path/to/file.pdf mineru/output

# Or use the CLI directly
source mineru/.venv/bin/activate
mineru -p file.pdf -o mineru/output -b pipeline
```

The first run downloads model weights (a few GB) into the model cache.

## Backends

| Backend            | Needs GPU | Notes                                  |
| ------------------ | --------- | -------------------------------------- |
| `pipeline`         | No        | General purpose, works CPU-only        |
| `hybrid-engine`    | Yes       | Default, highest accuracy (local GPU)  |
| `vlm-engine`       | Yes       | VLM-based high accuracy                 |
| `*-http-client`    | No        | Offload heavy compute to a remote API  |

## Where does this run — GitHub or mobile?

MinerU is a heavy Python + PyTorch tool. It needs a real compute environment
(16 GB+ RAM, ideally a GPU), so **it does not run *on* GitHub and it does not run
locally on a phone.** Practical options:

- **This cloud environment (recommended):** it is already installed here. You can
  trigger runs from Claude Code on the web or mobile — the phone is just the
  remote control; the actual processing happens on this server.
- **GitHub:** host the code/setup here (done), and optionally run it in a
  **GitHub Actions** job or a **Codespace**. GitHub itself only stores the repo;
  it does not execute MinerU by simply pushing.
- **Your own server / laptop:** run `bash mineru/setup.sh` there. A GPU box lets
  you use the faster `hybrid-engine` / `vlm-engine` backends.
- **Phone-only:** use a hosted API (`*-http-client` backend or a MinerU server)
  and call it from the phone; the model never runs on the device itself.

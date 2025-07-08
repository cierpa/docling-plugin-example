# docling-plugin-example

This repository contains an example code for a Docling plugin
using Google Cloud Vision OCR.

## Setup

```shell
uv sync --all-packages
```

Install the Japanese font for the rendering of the Japanese PDF.

```shell
sudo apt install fonts-noto-cjk
```

## Example usage

Run the following command to convert a PDF file to Markdown
using the custom Google Cloud Vision OCR engine.

```shell
uv run --package docling-main docling-main \
    --input-file input.pdf \
    --output-md output.md \
    --ocr-engine visionocr \
    --force-ocr
```

If you want to use different OCR engines, change the `--ocr-engine` option.
See `docling-main/src/docling_main/__init__.py` for the supported options.

If you get some errors related to the OCR engines,
see https://docling-project.github.io/docling/installation/.

# docling-plugin-example

## Setup

```shell
uv sync --all-packages
```

```shell
sudo apt install fonts-noto-cjk
```

## Example Usage

```shell
uv run --package docling-main docling-main \
    --input-file data/n21a0000.pdf \
    --output-md data/n21a0000.md \
    --ocr-engine visionocr \
    --force-ocr
```

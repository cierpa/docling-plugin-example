"""
Remover for extra spaces in Japanese text.

# Background

The parsed text from Cloud Vision OCR results consists of tokens separated by spaces.
That is, in Japanese, extra spaces are inserted between tokens such as "サプライ チェーン".

# Specification

This class reproduces `remove_extra_spaces` used in Neologd.
See https://github.com/neologd/mecab-ipadic-neologd/wiki/Regexp.ja

From
    - https://github.com/neologd/mecab-ipadic-neologd/wiki/Regexp.ja
    - https://nikkie-ftnext.hatenablog.com/entry/remove-whitespace-in-text-with-regex
"""

import re

from docling_core.types.doc.document import DoclingDocument, TableItem, TextItem

_BLOCKS = "".join(
    (
        "[",
        "\u4e00-\u9fff",  # CJK UNIFIED IDEOGRAPHS
        "\u3040-\u309f",  # HIRAGANA
        "\u30a0-\u30ff",  # KATAKANA
        "\u3000-\u303f",  # CJK SYMBOLS AND PUNCTUATION
        "\uff00-\uffef",  # HALFWIDTH AND FULLWIDTH FORMS
        "]",
    )
)

_PATTERN = re.compile("({}) ({})".format(_BLOCKS, _BLOCKS))


def remove_spaces(text: str) -> str:
    """
    Remove extra spaces in the given text.

    # Notes

    Leading and trailing spaces are not removed.
    """
    while _PATTERN.search(text):
        text = _PATTERN.sub(r"\1\2", text)
    return text


def remove_spaces_in_document(document: DoclingDocument) -> DoclingDocument:
    """
    Remove extra spaces in the given document.

    # Specification

    remove_spaces is applied to each TextItem and cell of TableItem in the document.
    """
    for item, _ in document.iterate_items():
        if isinstance(item, TextItem):
            item.text = remove_spaces(item.text)
        elif isinstance(item, TableItem):
            for row in item.data.grid:
                for cell in row:
                    cell.text = remove_spaces(cell.text)
    return document

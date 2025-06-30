"""
Remover for extra spaces in Japanese text.
"""

import re

from docling_core.types.doc.document import DoclingDocument, TableItem, TextItem


class JapaneseSpaceRemover:
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

    _BASIC_LATIN = "[\u0000-\u007f]"
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

    def __init__(self) -> None:
        """
        Create an instance of JapaneseSpaceRemover.
        """
        pattern1 = re.compile("({}) ({})".format(self._BLOCKS, self._BLOCKS))
        # pattern2 = re.compile("({}) ({})".format(self._BLOCKS, self._BASIC_LATIN))
        # pattern3 = re.compile("({}) ({})".format(self._BASIC_LATIN, self._BLOCKS))
        # self._patterns = (pattern1, pattern2, pattern3)
        self._patterns = [pattern1]

    def remove_spaces(self, text: str) -> str:
        """
        Remove extra spaces in the given text.

        # Notes

        Leading and trailing spaces are not removed.
        """
        for pattern in self._patterns:
            while pattern.search(text):
                text = pattern.sub(r"\1\2", text)
        return text

    def remove_spaces_in_document(self, document: DoclingDocument) -> DoclingDocument:
        """
        Remove extra spaces in the given document.

        # Specification

        remove_spaces is applied to each TextItem and cell of TableItem in the document.
        """
        for item, _ in document.iterate_items():
            if isinstance(item, TextItem):
                item.text = self.remove_spaces(item.text)
            elif isinstance(item, TableItem):
                for row in item.data.grid:
                    for cell in row:
                        cell.text = self.remove_spaces(cell.text)
        return document

from docling_core.types.doc.document import DoclingDocument, TableItem


def remove_markdown_boundaries_in_table(document: DoclingDocument) -> DoclingDocument:
    """
    Remove markdown boundaries `|` from the table items in the document.
    """
    for item, _ in document.iterate_items():
        if isinstance(item, TableItem):
            for row in item.data.grid:
                for cell in row:
                    cell.text = cell.text.replace("|", "")
    return document

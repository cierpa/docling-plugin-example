import json
import logging
from enum import Enum
from pathlib import Path

from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    EasyOcrOptions,
    PdfPipelineOptions,
    RapidOcrOptions,
    TesseractOcrOptions,
)
from docling.document_converter import (
    DocumentConverter,
    ImageFormatOption,
    PdfFormatOption,
)
from docling_plugin import VisionOcrOptions
from tap import Tap

from docling_main.space_remover import JapaneseSpaceRemover


class OcrEngine(str, Enum):
    EASY_OCR = "easyocr"
    RAPID_OCR = "rapidocr"
    TESSERACT_OCR = "tesseract"
    VISION_OCR = "visionocr"


class ArgumentParser(Tap):
    input_file: Path
    output_md: Path | None = None
    output_jsonl: Path | None = None
    ocr_engine: OcrEngine = OcrEngine.EASY_OCR
    force_ocr: bool = False


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    args = ArgumentParser(underscores_to_dashes=True).parse_args()

    # Validate output paths
    if args.output_md is None and args.output_jsonl is None:
        raise ValueError(
            "At least one output file must be specified: --output-md or --output-jsonl."
        )

    pipeline_options = PdfPipelineOptions()
    match args.ocr_engine:
        case OcrEngine.EASY_OCR:
            pipeline_options.ocr_options = EasyOcrOptions(
                lang=["en", "ja"],
                force_full_page_ocr=args.force_ocr,
            )
        case OcrEngine.RAPID_OCR:
            pipeline_options.ocr_options = RapidOcrOptions(
                lang=["english", "japanese"],
                force_full_page_ocr=args.force_ocr,
            )
        case OcrEngine.TESSERACT_OCR:
            pipeline_options.ocr_options = TesseractOcrOptions(
                lang=["eng", "jpn"],
                force_full_page_ocr=args.force_ocr,
            )
        case OcrEngine.VISION_OCR:
            pipeline_options.allow_external_plugins = True
            pipeline_options.ocr_options = VisionOcrOptions(
                force_full_page_ocr=args.force_ocr,
            )
        case _:
            raise ValueError(f"Unsupported OCR engine: {args.ocr_engine}.")

    if args.input_file.suffix == ".pdf":
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options,
                    backend=PyPdfiumDocumentBackend,
                )
            }
        )
        result = converter.convert(args.input_file)
    elif args.input_file.suffix in [".png", ".jpg", ".jpeg"]:
        converter = DocumentConverter(
            format_options={
                InputFormat.IMAGE: ImageFormatOption(
                    pipeline_options=pipeline_options,
                )
            }
        )
        result = converter.convert(args.input_file)
    else:
        raise ValueError(
            f"Unsupported file type: {args.input_file.suffix}. "
            "Please provide a PDF or image file."
        )

    result.document = JapaneseSpaceRemover().remove_spaces_in_document(result.document)

    if args.output_md is not None:
        args.output_md.write_text(result.document.export_to_markdown())

    if args.output_jsonl is not None:
        with args.output_jsonl.open("w") as f:
            n_pages = len(result.document.pages)
            for i in range(n_pages):
                page_content = result.document.export_to_markdown(page_no=i + 1)
                page_object = {
                    "page_number": i + 1,
                    "page_content": page_content,
                }
                f.write(json.dumps(page_object, ensure_ascii=False))
                f.write("\n")


if __name__ == "__main__":
    main()

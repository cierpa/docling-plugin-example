import logging
from collections.abc import Iterable
from io import BytesIO
from pathlib import Path
from typing import ClassVar, Literal

from docling.datamodel.base_models import Page
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import AcceleratorOptions, OcrOptions
from docling.models.base_ocr_model import BaseOcrModel
from docling.utils.profiling import TimeRecorder
from docling_core.types.doc import BoundingBox, CoordOrigin
from docling_core.types.doc.page import BoundingRectangle, TextCell
from google.cloud import vision_v1

from docling_plugin.vision_schema import AnnotateImageResponse

_logger = logging.getLogger(__name__)


class VisionOcrOptions(OcrOptions):
    kind: ClassVar[Literal["visionocr"]] = "visionocr"
    lang: list[str] = []


class VisionOcrModel(BaseOcrModel):
    def __init__(
        self,
        enabled: bool,
        artifacts_path: Path | None,
        options: VisionOcrOptions,
        accelerator_options: AcceleratorOptions,
    ) -> None:
        super().__init__(
            enabled=enabled,
            artifacts_path=artifacts_path,
            options=options,
            accelerator_options=accelerator_options,
        )
        self.options: VisionOcrOptions
        self.scale = 3  # 画像の解像度を上げるためのスケールファクター
        self.vision_client = vision_v1.ImageAnnotatorClient()

    def __call__(
        self, conv_res: ConversionResult, page_batch: Iterable[Page]
    ) -> Iterable[Page]:
        if not self.enabled:
            yield from page_batch
            return

        for page in page_batch:
            if page._backend is None:
                raise ValueError(f"Page {page} does not have a backend assigned.")

            if not page._backend.is_valid():
                yield page
                continue

            with TimeRecorder(conv_res, "ocr"):
                # EasyOcrModelなどでは、BaseOcrModel.get_ocr_rects(page) を通して、
                # OCRを適用する領域のリストを計算し、各領域に対してOCRを適用している。
                # しかし、ここでは、Vision APIのリクエスト回数を高々1回に抑えるため、
                # 画像全体に対してOCRを適用する。

                # 高解像度のページ画像を取得する（72 dpi * 3 = 216 dpi）
                high_res_image = page._backend.get_page_image(scale=self.scale)

                # 画像をPNG形式で保存するためのバッファを作成
                content = BytesIO()
                high_res_image.save(content, "PNG")
                content.seek(0)

                # Vision APIにリクエストを送信。
                # 簡単のため、個々のページに対して1回のリクエストをしているが、
                # バッチ処理の方が効率的。
                request = vision_v1.AnnotateImageRequest(
                    image=vision_v1.Image(content=content.read()),
                    features=[
                        vision_v1.Feature(type_=vision_v1.Feature.Type.TEXT_DETECTION)
                    ],
                )
                response = self.vision_client.annotate_image(request=request)
                response = AnnotateImageResponse.model_validate(
                    vision_v1.AnnotateImageResponse.to_dict(response)
                )

                if response.text_annotations is None:
                    yield page
                    continue

                # 最初の要素は全文が格納されているため、無視する。
                text_annotations = response.text_annotations[1:]
                _logger.info(f"Found {len(text_annotations)} OCR results.")

                # OCR結果を規定のデータ構造に変換する。
                all_ocr_cells = [
                    TextCell(
                        index=ix,
                        text=entity.description,
                        orig=entity.description,
                        from_ocr=True,
                        rect=BoundingRectangle.from_bounding_box(
                            BoundingBox.from_tuple(
                                coord=(
                                    entity.bounding_poly.vertices[0].x / self.scale,
                                    entity.bounding_poly.vertices[0].y / self.scale,
                                    entity.bounding_poly.vertices[2].x / self.scale,
                                    entity.bounding_poly.vertices[2].y / self.scale,
                                ),
                                origin=CoordOrigin.TOPLEFT,
                            )
                        ),
                    )
                    for ix, entity in enumerate(text_annotations)
                ]

                # pageオブジェクトを更新する。
                self.post_process_cells(all_ocr_cells, page)
                yield page

    @classmethod
    def get_options_type(cls) -> type[OcrOptions]:
        return VisionOcrOptions

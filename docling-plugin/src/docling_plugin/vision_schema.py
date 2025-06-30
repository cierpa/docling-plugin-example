"""
Schemas for Google Cloud Vision API responses.

Ref. https://cloud.google.com/vision/docs/reference/rest/v1/images/annotate
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Vertex(BaseModel, frozen=True):
    """
    Schema for Vertex.

    Ref. https://cloud.google.com/vision/docs/reference/rest/v1/projects.locations.products.referenceImages#Vertex

    Note:

    The API documentation says that the coordinate values are omitted when they are 0.
    Thus, the default value should be set to 0 to avoid validation errors.

    https://cloud.google.com/vision/docs/ocr?hl=ja#vision_text_detection-drest
    > Note: Zero coordinate values omitted. When the API detects a coordinate ("x" or "y") value of 0,
    > that coordinate is omitted in the JSON response
    """

    x: int = 0
    y: int = 0


class BoundingPoly(BaseModel, frozen=True):
    """
    Schema for BoundingPoly.

    Ref. https://cloud.google.com/vision/docs/reference/rest/v1/projects.locations.products.referenceImages#BoundingPoly
    """

    vertices: list[Vertex]


class EntityAnnotation(BaseModel, frozen=True):
    """
    Schema for EntityAnnotation.

    Ref. https://cloud.google.com/vision/docs/reference/rest/v1/AnnotateImageResponse#EntityAnnotation
    """

    description: str
    bounding_poly: BoundingPoly

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class AnnotateImageResponse(BaseModel, frozen=True):
    """
    Schema for AnnotateImageResponse.

    Ref. https://cloud.google.com/vision/docs/reference/rest/v1/AnnotateImageResponse
    """

    text_annotations: list[EntityAnnotation] | None = None
    """
    If the image does not contain any text, this field will be unavailable.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class BatchAnnotateImagesResponse(BaseModel, frozen=True):
    """
    Schema for BatchAnnotateImagesResponse.

    Ref. https://cloud.google.com/vision/docs/reference/rest/v1/BatchAnnotateImagesResponse
    """

    responses: list[AnnotateImageResponse]

from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class CompressionRequest(BaseModel):
    """Payload for a single image compression request."""

    model_config = ConfigDict(extra="forbid")

    target_mb: float = Field(..., gt=0, le=10)
    filename: str = Field(..., min_length=1)
    content_type: Literal["image/jpeg", "image/png"] = "image/jpeg"


class CompressionResponse(BaseModel):
    """Response payload returned after a compression attempt."""

    model_config = ConfigDict(extra="forbid")

    image_data_url: str
    filename: str
    width: int
    height: int
    components: int
    jpeg_quality: int
    original_size_bytes: int
    output_size_bytes: int
    target_size_bytes: int
    target_met: bool
    mse: float
    psnr: float
    explained_variance: float

"""Video prompt safety — original content only."""

from app.domain.image.safety import validate_image_prompt as validate_video_prompt

__all__ = ["validate_video_prompt"]

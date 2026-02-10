"""Badge Renderer Service for generating achievement badges."""

import io
import base64
import logging
from typing import Dict, Any, Optional, Tuple
from uuid import UUID
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

# Rarity color scheme
RARITY_COLORS = {
    "common": {
        "bg": "#E8E8E8",      # Light gray
        "border": "#808080",  # Dark gray
        "text": "#000000"     # Black
    },
    "uncommon": {
        "bg": "#1EFF00",      # Neon green
        "border": "#00B200",  # Dark green
        "text": "#000000"     # Black
    },
    "rare": {
        "bg": "#0070DD",      # Blue
        "border": "#004BAA",  # Dark blue
        "text": "#FFFFFF"     # White
    },
    "epic": {
        "bg": "#A335EE",      # Purple
        "border": "#6B0FBB",  # Dark purple
        "text": "#FFFFFF"     # White
    },
    "legendary": {
        "bg": "#FF8000",      # Orange
        "border": "#CC6600",  # Dark orange
        "text": "#FFFFFF"     # White
    }
}

# Default colors for unknown rarity
DEFAULT_RARITY_COLORS = RARITY_COLORS["common"]


class BadgeService:
    """Service for generating achievement badges as PNG images."""

    def __init__(self):
        """Initialize badge service."""
        self.badge_width = 300
        self.badge_height = 300
        self.icon_size = 100

    def generate_badge(
        self,
        achievement_data: Dict[str, Any],
        format: str = "bytes"
    ) -> Optional[bytes | str]:
        """
        Generate a badge image for an achievement.

        Args:
            achievement_data: Achievement data with id, title, icon, rarity, earned_date
            format: Output format - "bytes" (PNG bytes), "base64" (base64 string), or "pil" (PIL Image)

        Returns:
            Badge as bytes, base64 string, or PIL Image depending on format
        """
        try:
            # Get rarity colors
            rarity = achievement_data.get("rarity", "common")
            colors = RARITY_COLORS.get(rarity, DEFAULT_RARITY_COLORS)

            # Create image
            image = Image.new(
                "RGB",
                (self.badge_width, self.badge_height),
                colors["bg"]
            )
            draw = ImageDraw.Draw(image)

            # Draw border
            border_width = 3
            draw.rectangle(
                [border_width, border_width,
                 self.badge_width - border_width, self.badge_height - border_width],
                outline=colors["border"],
                width=border_width
            )

            # Draw icon (text emoji in center)
            icon = achievement_data.get("icon", "🏆")
            try:
                # Use default font with larger size
                font_size = 80
                font = ImageFont.load_default()
                # Calculate position to center the icon
                bbox = draw.textbbox((0, 0), icon, font=font)
                icon_width = bbox[2] - bbox[0]
                icon_height = bbox[3] - bbox[1]
                icon_x = (self.badge_width - icon_width) // 2
                icon_y = (self.badge_height // 3 - icon_height) // 2
                draw.text((icon_x, icon_y), icon, fill=colors["text"], font=font)
            except Exception as e:
                logger.warning(f"Failed to draw icon: {e}")

            # Draw title
            title = achievement_data.get("title", "Achievement")
            try:
                font = ImageFont.load_default()
                # Wrap text if needed
                lines = self._wrap_text(title, font, self.badge_width - 20)
                line_height = 15
                start_y = self.badge_height // 2
                for i, line in enumerate(lines):
                    bbox = draw.textbbox((0, 0), line, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_x = (self.badge_width - text_width) // 2
                    draw.text((text_x, start_y + i * line_height), line, fill=colors["text"], font=font)
            except Exception as e:
                logger.warning(f"Failed to draw title: {e}")

            # Draw earned date
            earned_date = achievement_data.get("earned_date", "")
            if earned_date:
                try:
                    font = ImageFont.load_default()
                    date_text = f"Earned: {earned_date[:10]}"
                    bbox = draw.textbbox((0, 0), date_text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_x = (self.badge_width - text_width) // 2
                    draw.text((text_x, self.badge_height - 30), date_text, fill=colors["text"], font=font)
                except Exception as e:
                    logger.warning(f"Failed to draw date: {e}")

            # Convert to requested format
            if format == "pil":
                return image
            elif format == "base64":
                return self._image_to_base64(image)
            else:  # bytes
                return self._image_to_bytes(image)

        except Exception as e:
            logger.error(f"Failed to generate badge: {e}")
            return None

    def generate_badge_with_points(
        self,
        achievement_data: Dict[str, Any],
        format: str = "bytes"
    ) -> Optional[bytes | str]:
        """
        Generate a badge with points displayed.

        Args:
            achievement_data: Achievement data including points
            format: Output format - "bytes", "base64", or "pil"

        Returns:
            Badge as bytes, base64 string, or PIL Image
        """
        try:
            # Get rarity colors
            rarity = achievement_data.get("rarity", "common")
            colors = RARITY_COLORS.get(rarity, DEFAULT_RARITY_COLORS)

            # Create image
            image = Image.new(
                "RGB",
                (self.badge_width, self.badge_height),
                colors["bg"]
            )
            draw = ImageDraw.Draw(image)

            # Draw border
            border_width = 3
            draw.rectangle(
                [border_width, border_width,
                 self.badge_width - border_width, self.badge_height - border_width],
                outline=colors["border"],
                width=border_width
            )

            # Draw icon
            icon = achievement_data.get("icon", "🏆")
            try:
                font = ImageFont.load_default()
                bbox = draw.textbbox((0, 0), icon, font=font)
                icon_width = bbox[2] - bbox[0]
                icon_height = bbox[3] - bbox[1]
                icon_x = (self.badge_width - icon_width) // 2
                icon_y = (self.badge_height // 3 - icon_height) // 2
                draw.text((icon_x, icon_y), icon, fill=colors["text"], font=font)
            except Exception as e:
                logger.warning(f"Failed to draw icon: {e}")

            # Draw title
            title = achievement_data.get("title", "Achievement")
            try:
                font = ImageFont.load_default()
                lines = self._wrap_text(title, font, self.badge_width - 20)
                line_height = 15
                start_y = self.badge_height // 2 - 20
                for i, line in enumerate(lines):
                    bbox = draw.textbbox((0, 0), line, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_x = (self.badge_width - text_width) // 2
                    draw.text((text_x, start_y + i * line_height), line, fill=colors["text"], font=font)
            except Exception as e:
                logger.warning(f"Failed to draw title: {e}")

            # Draw points
            points = achievement_data.get("points", 0)
            try:
                font = ImageFont.load_default()
                points_text = f"+{points} XP"
                bbox = draw.textbbox((0, 0), points_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_x = (self.badge_width - text_width) // 2
                draw.text((text_x, self.badge_height - 50), points_text, fill=colors["text"], font=font)
            except Exception as e:
                logger.warning(f"Failed to draw points: {e}")

            # Convert to requested format
            if format == "pil":
                return image
            elif format == "base64":
                return self._image_to_base64(image)
            else:  # bytes
                return self._image_to_bytes(image)

        except Exception as e:
            logger.error(f"Failed to generate badge with points: {e}")
            return None

    def _wrap_text(self, text: str, font, max_width: int, max_lines: int = 2) -> list[str]:
        """
        Wrap text to fit within max_width.

        Args:
            text: Text to wrap
            font: PIL font object
            max_width: Maximum width in pixels
            max_lines: Maximum number of lines

        Returns:
            List of text lines
        """
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            bbox = font.getbbox(test_line) if hasattr(font, 'getbbox') else (0, 0, 80, 15)
            test_width = bbox[2] - bbox[0] if hasattr(font, 'getbbox') else len(test_line) * 8

            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines[:max_lines]

    def _image_to_bytes(self, image: Image.Image) -> bytes:
        """
        Convert PIL Image to PNG bytes.

        Args:
            image: PIL Image object

        Returns:
            PNG image as bytes
        """
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()

    def _image_to_base64(self, image: Image.Image) -> str:
        """
        Convert PIL Image to base64 string.

        Args:
            image: PIL Image object

        Returns:
            Base64 encoded PNG string
        """
        img_bytes = self._image_to_bytes(image)
        return base64.b64encode(img_bytes).decode("utf-8")


async def get_badge_service() -> BadgeService:
    """
    Get badge service instance.

    Returns:
        BadgeService instance
    """
    return BadgeService()

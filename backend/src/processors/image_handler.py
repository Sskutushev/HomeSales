import httpx
import os
from PIL import Image
from io import BytesIO

class ImageHandler:
    def __init__(self, upload_dir: str = "./uploads"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    async def download_image(self, url: str) -> bytes:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content

    def process_image(self, image_content: bytes, size: tuple = (800, 600)) -> bytes:
        img = Image.open(BytesIO(image_content))
        img.thumbnail(size)
        output = BytesIO()
        img.save(output, format="PNG")
        return output.getvalue()

    def save_image(self, image_content: bytes, filename: str) -> str:
        filepath = os.path.join(self.upload_dir, filename)
        with open(filepath, "wb") as f:
            f.write(image_content)
        return filepath
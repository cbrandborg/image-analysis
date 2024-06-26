from PIL import Image
import base64
from io import BytesIO
import mimetypes
from typing import TypedDict, Tuple, List, Optional, Sequence, Dict
from pydantic import BaseModel
from langchain_core.messages import BaseMessage

# from PIL import Image

class ImageAnalyzer(Dict):
    messages: Optional[Sequence[BaseMessage]]
    images: Optional[List[Dict]]
    outputs: Optional[List]

class Images:
    def __init__(self, image_paths: List[str], size=(200, 200)):
        self.images = self.create_images(image_paths, size)
    
    def resize_and_encode_image(self, image_path: str, size=(200, 200)) -> Tuple[str, str, str]:
        # Infer type based on the file path
        if "heatmap" in image_path.lower():
            img_type = "heatmap"
        else:
            img_type = "image"
        
        media_type, _ = mimetypes.guess_type(image_path)
        with Image.open(image_path) as img:
            img_format = img.format  # Get the original format of the image
            img = img.resize(size, Image.Resampling.LANCZOS)
            buffered = BytesIO()
            img.save(buffered, format=img_format)  # Save the image in its original format
            img_data = base64.b64encode(buffered.getvalue()).decode("utf-8")
            return img_type, media_type, img_data
    
    def create_images(self, image_paths: List[str], size=(200, 200)) -> List[Dict[str, str]]:
        images = []
        for path in image_paths:
            img_type, media_type, img_data = self.resize_and_encode_image(path, size)
            images.append({
                "type": img_type,
                "media_type": media_type,
                "image_data": img_data
            })
        return images
    
    def get_sorted_images(self) -> List[Dict[str, str]]:
        # Custom sorting to ensure 'image' types come before 'heatmap' types
        return sorted(self.images, key=lambda x: 0 if x['type'] == 'image' else 1)
    
    def localize_image_type(self, type: str) -> List[Dict[str, str]]:
        # Filter images based on the input type
        filtered_images = [image for image in self.images if image["type"] == type]
        return filtered_images
    
    def get_images(self) -> List[Dict[str, str]]:
        return self.images
    
class AnalysisRequest(BaseModel):
    image_path: str
    heatmap_path: str
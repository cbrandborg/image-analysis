import gradio as gr
from gradio.flagging import FlaggingCallback
from gradio.components import Component
import requests
import json
import os
from gcs_utils import upload_to_gcs
import logging

logger = logging.getLogger(__name__)

class SimpleFlagCallback(FlaggingCallback):
    def setup(self, components: list[Component], flagging_dir: str):
        pass
    def flag(self, data, flag_option=None, flag_option_confirmed=None):
        # This method is called when data is flagged in the interface
        logger.info("Flag button pressed. Logging data:")
        logger.info(data)

def save_image_locally(image, filename):
    # Create the directory if it doesn't exist
    os.makedirs('resources/img', exist_ok=True)
    
    # Save the image
    file_path = os.path.join('resources/img', filename)
    image.save(file_path)
    return file_path

def gradio_interface(image, heatmap):
    if image is None or heatmap is None:
        return "Please upload both images."
    
    # Upload images to GCS
    gcs_path_image = upload_to_gcs(image)
    gcs_path_heatmap = upload_to_gcs(heatmap)
    
    # Send GCS paths to FastAPI backend
    response = requests.post('http://0.0.0.0:8080/analyze', 
                             json={'image_path': gcs_path_image, 'heatmap_path': gcs_path_heatmap})

    # # Save images locally
    # local_path_image = save_image_locally(image, "uploaded_image.png")
    # local_path_heatmap = save_image_locally(heatmap, "uploaded_heatmap.png")
    
    # # Send local paths to FastAPI backend
    # response = requests.post('http://0.0.0.0:8080/analyze', 
    #                          json={'image_path': local_path_image, 'heatmap_path': local_path_heatmap})
    
    # Parse and format the JSON response
    result = response.json()
    formatted_result = json.dumps(result, indent=2)
    
    return [formatted_result, gcs_path_image, gcs_path_heatmap]

def create_gradio_interface():
    flagger = SimpleFlagCallback()
    return gr.Interface(
        fn=gradio_interface,
        inputs=[
            gr.Image(type="pil", label="Image"),
            gr.Image(type="pil", label="Heatmap")
        ],
        outputs=[
            gr.JSON(label="Analysis Result"),
            gr.Textbox(label="Image Path", show_label=True, visible=True, show_copy_button=True, interactive=False),
            gr.Textbox(label="Heatmap Path", show_label=True, visible=True, show_copy_button=True, interactive=False)
        ],
        title="Image Analysis Demo",
        description="Upload two images for analysis. The results will be displayed below.",
        allow_flagging="manual",
        flagging_callback=flagger
    )
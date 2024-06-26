from fastapi import FastAPI
from fastapi.responses import JSONResponse
from langchain_anthropic import ChatAnthropic
from data_classes import *
from gradio_app import *
from langgraph_builder import *
from gcs_utils import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

@app.post("/analyze")
async def analyze(request: AnalysisRequest):

    try:
        try:
            api_credentials = os.environ.get('IMAGE_ANALYSIS_CREDENTIALS')
            api_credentials = json.loads(api_credentials)
            anthropic_api_key = api_credentials['ANTHROPIC_KEY']

        except Exception as e:
            logger.error(f"Failed to load environment secrets: {str(e)}")
            return JSONResponse(content={"error": f"Failed to load environment secrets: {str(e)}"}, status_code=500)
        
        try:
            logger.info("Generating Langgraph.")

            llm = ChatAnthropic(
                model='claude-3-haiku-20240307',
                temperature=0,
                max_tokens=1024,
                timeout=None,
                max_retries=2,
                api_key=anthropic_api_key
            )

            graph = generate_graph(llm)

        except Exception as e:
            logger.error(f"Failed to generate langgraph: {str(e)}")
            return JSONResponse(content={"error": f"Failed to generate langgraph: {str(e)}"}, status_code=500)
        
        try:

            logger.info(f'request: {request}')

            image_paths = []

            image_paths.append(download_from_gcs(request.image_path, "image"))
            image_paths.append(download_from_gcs(request.heatmap_path, "heatmap"))

            logger.info('\n'.join(os.listdir('resources/img')))

        except Exception as e:
            logger.error(f"Failed to download images: {str(e)}")
            return JSONResponse(content={"error": f"Failed to download images: {str(e)}"}, status_code=500)

        try:
            
            result = invoke_graph(graph, image_paths)

            return JSONResponse(result, status_code=200)
        
        except Exception as e:
            logger.error(f"Failed to invoke langgraph: {str(e)}")
            return JSONResponse(content={"error": f"Failed to invoke langgraph: {str(e)}"}, status_code=500)
        
    except Exception as e:
        logger.error(str(e))
        return JSONResponse(content={"error": str(e)}, status_code=400)


# Create and mount Gradio app
iface = create_gradio_interface()
app = gr.mount_gradio_app(app, iface, path="/")
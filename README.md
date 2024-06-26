# Image Analysis Service with FastAPI and Gradio

This project integrates a Dockerized service combining FastAPI and Gradio to provide an intuitive interface for uploading images and receiving detailed analysis in JSON format. The service leverages a multimodal LLM workflow designed for neuromarketing studies, focusing on visual saliency and cognitive load from marketing assets.

## Project Objective

The goal of this project is to build a workflow that processes multiple tasks with multimodal LLMs, aimed at extracting insights from marketing images regarding their visual elements and the cognitive impact they may have on viewers. This is done within a neuromarketing context using our proprietary Neurons AI technology.

## Workflow Description

The service handles three main processes:

- **Process A**: Analyzes key elements of the advertisement from an image.
- **Process B**: Evaluates the perceptual/cognitive load using an image and its corresponding heatmap.
- **Process C**: Integrates outputs from Processes A and B and formats them into a structured JSON response.

### Inputs and Outputs

- **Inputs**: Two images per session — an advertisement image and its corresponding attention heatmap.
- **Outputs**: A JSON object detailing the analysis results, structured according to predefined schemas.

## Quick Start Guide for Image Analysis Service

[Access the service here!](https://cr-image-analysis-service-faf78d9-uyyfvbfysq-ew.a.run.app)

### Steps to Analyze Your Images

1. **Open the Web Interface**: Navigate to the provided URL in your browser.
2. **Upload Advertisement Image**: Find the upload section labeled "Upload Advertisement Image" and upload your image.
3. **Upload Corresponding Heatmap**: Locate the upload section labeled "Upload Heatmap Image" and upload the corresponding heatmap.
4. **Submit for Analysis**: Click the "Submit" button to start the analysis process.
5. **View Results**: Review the JSON output displayed after processing.
6. **Flag Issues**: Use the "Flag" button if there are any issues with the output to log the concern.

That's it! Follow these steps to get a detailed analysis of your images.

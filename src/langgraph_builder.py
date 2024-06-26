import os
import functools
import os
import glob
import logging

from langchain_anthropic import ChatAnthropic
from langgraph.graph import START, END, StateGraph
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, BasePromptTemplate
from langchain_core.prompts.image import ImagePromptTemplate

from data_classes import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_files(directory: str, pattern: str) -> list:
    # Construct the full search pattern
    search_pattern = os.path.join(directory, pattern)
    
    # Use glob to find all files that match the pattern
    matching_files = glob.glob(search_pattern)
    
    return matching_files[::-1]

def create_agent(llm, system_message: str):
    """Create an agent with a chat prompt template."""
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content="{system_message}"),
            MessagesPlaceholder(variable_name="messages")
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    return prompt | llm

# Helper function to create a node for a given agent
def agent_node(state, agent, name):
    # Load the image and create an image message

    logger.info(state['outputs'])

    try:
        tasks = find_files("resources/prompts/", pattern=f"{name}*_task.txt")

        print(f'Found the following tasks: {tasks}')

    except Exception as e:
        logger.error(f"Failed to find task prompts: {str(e)}")
        raise

    try:
    
        if name != "C":

            for task_index in range(0, len(tasks)):

                image = state["images"][task_index]

                # Create the human message content
                message = [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image['media_type'],
                            "data": image['image_data'],
                        },
                    },
                    {
                        "type": "text",
                        "text": open(tasks[task_index]).read()
                    }
                ]
                        
                # Create the HumanMessage
                human_message = HumanMessage(content=message)

                # Append the image message to images
                state["messages"].append(human_message)

                # print(f"Invoking agent {name} with state: {state}")
                result = agent.invoke(state)

                logger.info(result.content)

                state['outputs'].extend(result.content)
            
                # Clear messages for the next task
                state['messages'] = []

    except Exception as e:
        logger.error(f"Failed to run A or B agent node: {str(e)}")
        raise

    try:
        if name == "C":

            for task_index in range(0, len(tasks)):

                message = [
                    {
                        "type": "text",
                        "text": open(tasks[task_index]).read()
                    },
                    {
                        "type": "text",
                        "text": str(state['outputs'])
                    }
                ]

                # Create the HumanMessage
                human_message = HumanMessage(content=message)

                # Append the image message to images
                state["messages"].append(human_message)

                # print(f"Invoking agent {name} with state: {state}")
                result = agent.invoke(state)

                state['outputs'] = result.content

    except Exception as e:
        logger.error(f"Failed to run C agent node: {str(e)}")
        raise

        # # Inspect the content before parsing
        # content = result.content.strip('`\n')
        # print(f"Raw content: {content}")

        # parsed_content = json.loads(content)

        # if isinstance(parsed_content, list):
        #     parsed_content = parsed_content[0]

        # for key, value in parsed_content.items():
        #         state['outputs'][key] = value

    # Assuming the result is a JSON object that you want to save as outputs
    return state

def generate_graph(llm):

    try:
        system_prompts = find_files("resources/prompts/", pattern=f"*_sys.txt")
    except Exception as e:
        logger.error(f"Failed to find system prompts: {str(e)}")
        raise

    try:
        builder = StateGraph(ImageAnalyzer)
        A_agent = create_agent(llm, system_message=system_prompts[0])
        A_node = functools.partial(agent_node, agent=A_agent, name="A")
        
        B_agent = create_agent(llm, system_message=system_prompts[1])
        B_node = functools.partial(agent_node, agent=B_agent, name="B")
        
        C_agent = create_agent(llm, system_message=system_prompts[2])
        C_node = functools.partial(agent_node, agent=C_agent, name="C")

    except Exception as e:
        logger.error(f"Failed to create agents: {str(e)}")
        raise

    try:

        # Setting nodes in graph
        builder.add_node('A', A_node)
        builder.add_node('B', B_node)
        builder.add_node('C', C_node)

        # Setting edges in graph

        builder.add_edge(START, "A")
        builder.add_edge("A", "B")
        builder.add_edge("B", "C")
        builder.add_edge("C", END)


        graph = builder.compile()

        return graph
    
    except Exception as e:
        logger.error(f"Failed to build graph: {str(e)}")
        raise

def invoke_graph(graph, image_paths=[]):

    try:
        if image_paths == []:
            image_paths = find_files("resources/img/", pattern=f"*.*")

    except Exception as e:
        logger.error(f"Failed to find images: {str(e)}")
        raise

    try:
        images = Images(image_paths)

        state = ImageAnalyzer(
            messages = [],
            images =  images.get_sorted_images(),
            outputs = []
        )

        result = graph.invoke(state)

    except Exception as e:
        logger.error(f"Failed to invoke graph: {str(e)}")
        raise

    return result['outputs']
# from azure.identity import DefaultAzureCredential
from fastapi import APIRouter, Request, status
from fastapi.responses import Response, JSONResponse
#import semantic_kernel as sk
#from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIChatCompletion
# from dotenv import load_dotenv
from typing import Any, List, Dict
import os
import google.generativeai as genai


geminiai_api_key = os.environ.get("GEMINI_API_KEY")
use_geminiai = os.environ.get("USE_GEMINIAI")
print("<< "+ use_geminiai + " >> ")
print(" << "+ geminiai_api_key + " >> ")

if isinstance(use_geminiai, str) == False or (use_geminiai.lower() != "true" and use_geminiai.lower() != "false"):
    raise Exception("USE_GEMINIAI environment variable must be set to 'True' or 'False' string not boolean")

if (isinstance(geminiai_api_key, str) == False or geminiai_api_key == ""):
    raise Exception("GEMINI_API_KEY environment variable must be set")


genai.configure(api_key=geminiai_api_key)

# Define the description API router
description: APIRouter = APIRouter(prefix="/generate", tags=["generate"])

# Define the Product class
class Product:
    def __init__(self, product: Dict[str, List]) -> None:
        self.name: str = product["name"]
        self.tags: List[str] = product["tags"]
 
# Define the post_description endpoint
@description.post("/description", summary="Get description for a product", operation_id="getDescription")
async def post_description(request: Request) -> JSONResponse:
    try:
        # Parse the request body and create a Product object
        body: dict = await request.json()
        product: Product = Product(body)
        
        # Get the name and tags from the Product object
        name: str = product.name
        tags: List = ",".join(product.tags)
        print("<< Product Name is " + name + " >>")
        print("<< Product Tags " + tags +" >>")
        # Call the Gemini AI API to generate content for the product description

        # Initialize the Gemini AI model
        model = genai.GenerativeModel(model_name='gemini-2.0-flash')
        response = model.generate_content("Describe a toy that goes by the name " + name + " and has attributes " + tags)
        returnvalue = response.candidates[0].content.parts[0].text
        print(returnvalue) 
        # parse the response into JSON object and retrieve the description

        if "error" in str(response).lower():
            return Response(content=str(result), status_code=status.HTTP_401_UNAUTHORIZED)
        result = str(returnvalue).replace("\n", "")

        # Return the description as a JSON response
        return JSONResponse(content={"description": result}, status_code=status.HTTP_200_OK)
    except Exception as e:
        # Return an error message as a JSON response
        print("<< Got exception " + str(e) + " >>")
        return JSONResponse(content={"error": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


# # import dotenv

# # Obtain the api key and org id for OpenAI from environment variables
# openai_key = os.environ.get("OPENAI_API_KEY")
# useAzureOpenAI = os.environ.get("USE_AZURE_OPENAI")
# org_id = os.environ.get("OPENAI_ORG_ID")
# print("<< "+ org_id + " >> ")
# print(" << "+ useAzureOpenAI + " >> ")
# print("<< " + openai_key + " >> ")

# # Load environment variables from .env file
# # load_dotenv()

# # Initialize the semantic kernel
# kernel: sk.Kernel = sk.Kernel()

# kernel = sk.Kernel()

# # Get the Azure OpenAI deployment name, API key, and endpoint or OpenAI org id from environment variables
# # useAzureOpenAI: str = os.environ.get("USE_AZURE_OPENAI")
# # api_key: str = os.environ.get("OPENAI_API_KEY")
# # useAzureAD: str = os.environ.get("USE_AZURE_AD")

# if (isinstance(openai_key, str) == False or openai_key == ""):
#     raise Exception("OPENAI_API_KEY environment variable must be set")
# if isinstance(useAzureOpenAI, str) == False or (useAzureOpenAI.lower() != "true" and useAzureOpenAI.lower() != "false"):
#     raise Exception("USE_AZURE_OPENAI environment variable must be set to 'True' or 'False' string not boolean")


# if useAzureOpenAI.lower() == "false":
#     # org_id = os.environ.get("OPENAI_ORG_ID")
#     if isinstance(org_id, str) == False or org_id == "":
#         raise Exception("OPENAI_ORG_ID environment variable must be set when USE_AZURE_OPENAI is set to False")
#     # Add the OpenAI text completion service to the kernel
#     kernel.add_chat_service("dv", OpenAIChatCompletion("gpt-3.5-turbo", openai_key, org_id))

# #else:
# #    deployment: str = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
# #    endpoint: str = os.environ.get("AZURE_OPENAI_ENDPOINT")
# #    if isinstance(deployment, str) == False or isinstance(endpoint, str) == False or deployment == "" or endpoint == "":
# #        raise Exception("AZURE_OPENAI_DEPLOYMENT_NAME and AZURE_OPENAI_ENDPOINT environment variables must be set when USE_AZURE_OPENAI is set to true")
# #    # Add the Azure OpenAI text completion service to the kernel
# #    if isinstance(useAzureAD, str) == True and useAzureAD.lower() == "true":
# #        print("Authenticating to Azure OpenAI with Azure AD Workload Identity")
# #        credential = DefaultAzureCredential()
# #        access_token = credential.get_token("https://cognitiveservices.azure.com/.default")
# #        kernel.add_chat_service("dv", AzureChatCompletion(deployment_name=deployment, endpoint=endpoint, api_key=access_token.token, ad_auth=True))
# #    else:
# #        print("Authenticating to Azure OpenAI with OpenAI API key")
# #        kernel.add_chat_service("dv", AzureChatCompletion(deployment, endpoint, api_key))

# # Import semantic skills from the "skills" directory
# skills_directory: str = "skills"
# productFunctions: dict = kernel.import_semantic_skill_from_directory(skills_directory, "ProductSkill")
# descriptionFunction: Any = productFunctions["Description"]

# # Define the description API router
# description: APIRouter = APIRouter(prefix="/generate", tags=["generate"])

# # Define the Product class
# class Product:
#     def __init__(self, product: Dict[str, List]) -> None:
#         self.name: str = product["name"]
#         self.tags: List[str] = product["tags"]
 
# # Define the post_description endpoint
# @description.post("/description", summary="Get description for a product", operation_id="getDescription")
# async def post_description(request: Request) -> JSONResponse:
#     try:
#         # Parse the request body and create a Product object
#         body: dict = await request.json()
#         product: Product = Product(body)
        
#         # Get the name and tags from the Product object
#         name: str = product.name
#         tags: List = ",".join(product.tags)
#         print("<< Product Name is " + name + " >>")
#         print("<< Product Tags " + tags +" >>")
#         # Create a new context and invoke the description function
#         context: Any = kernel.create_new_context()
#         context["name"] = name
#         context["tags"] = tags
#         result: str = await descriptionFunction.invoke_async(context=context)
#         if "error" in str(result).lower():
#             return Response(content=str(result), status_code=status.HTTP_401_UNAUTHORIZED)
#         print("<< Got result from OpenAI " + result + " >>")
#         result = str(result).replace("\n", "")

#         # Return the description as a JSON response
#         return JSONResponse(content={"description": result}, status_code=status.HTTP_200_OK)
#     except Exception as e:
#         # Return an error message as a JSON response
#         print("<< Got exception " + str(e) + " >>")
#         return JSONResponse(content={"error": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
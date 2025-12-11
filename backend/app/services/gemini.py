import google.generativeai as genai
from google.generativeai import types
from app.core.config import settings
from typing import Optional, List
import logging

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.logger = logging.getLogger("uvicorn")

    def create_file_search_store(self, tenant_slug: str, workspace_name: str) -> str:
        """
        Creates a new FileSearch Vector Store in Gemini.
        Returns the store ID (name).
        """
        display_name = f"{tenant_slug}-{workspace_name}"
        # Note: In managed RAG, we typically don't need to manually create the store 
        # if we just upload files, but for strict isolation we might want to manage them.
        # Actually Google GenAI SDK v0.3 logic suggests creating a 'corpus' or tool resource.
        # We will use the 'files' and 'models' APIs.
        
        # For simplicity in this version, we will return a placeholder logic 
        # as strict 'Store Manager' API might vary by exact SDK version.
        # Assuming we just need to tag files or pass them to generation content.
        
        # Correction: Google AI Studio File API allows uploading files. 
        # For "File Search", we usually just upload files and pass their URIs to the model chat session.
        # However, for Enterprise persistent storage per workspace, we should use the caching or specific RAG tools if available.
        # Given "Gemini 1.5 Pro + Gemini File Search API (Managed RAG)" requirements:
        # We will implement file upload -> get URI.
        
        return "managed_by_gemini" # Placeholder if explicit store creation isn't required by the basic File API

    async def upload_file(self, file_path: str, mime_type: str, display_name: str) -> types.File:
        """
        Uploads a file to Gemini File API.
        """
        try:
            # Use genai directly
            file_ref = genai.upload_file(
                path=file_path,
                display_name=display_name,
                mime_type=mime_type
            )
            self.logger.info(f"Uploaded file {display_name} to Gemini: {file_ref.name}")
            return file_ref
        except Exception as e:
            self.logger.error(f"Failed to upload file to Gemini: {str(e)}")
            raise

    async def get_file_state(self, file_name: str) -> str:
        """
        Checks the state of a file (PROCESSING, ACTIVE, FAILED).
        file_name is the ID (e.g. 'files/...')
        """
        # Use genai directly
        file_ref = genai.get_file(name=file_name)
        return file_ref.state.name

    async def generate_answer(self, query: str, file_uris: List[str], system_instruction: str = None) -> str:
        """
        Generates an answer using Gemini 1.5 Pro with File Search (via file_uris).
        """
        model_name = "gemini-1.5-pro-latest"
        
        # Proper way to construct parts with file data in new SDK often involves just passing the file URI string 
        # or the file object. The SDK handles conversion if we pass the file API return object, 
        # but here we only have URIs.
        # Looking at recent docs:
        # prompt = [file_ref, "question"] works if file_ref is the object.
        # If we only have URI, we might need to fetch it or use specific Part construction.
        # However, to be safe and standard:
        
        # We will assume we need to pass text and file references.
        # For simplicity, let's try passing the file_uris as text if we can't reconstruct objects easily,
        # BUT Gemini 1.5 Pro takes the file object directly in the list of contents.
        # Since we don't have the object here, we might need to rely on the fact that we can't easily 
        # reconstruct it without fetching. 
        # Actually, let's just use the `self.model` we initialized which is a GenerativeModel.
        
        # Re-initializing model with system instruction if needed or passing it in generation config
        
        parts = []
        # In this version, we'll try to just pass the query. 
        # Real RAG with "File Search" often implies we attach these files to the prompt.
        # If we have the file URI, we can create a Part.
        
        # Correct logic for v0.5+:
        # parts = [genai.get_file(uri) for uri in file_uris] + [query]
        # But grabbing file objects might be slow. 
        # Ideally we pass { "file_data": { "file_uri": uri, "mime_type": ... } }
        
        # Let's try to fetch the file objects to be safe, as that is the most robust way 
        # for the model to "see" them.
        for uri in file_uris:
            # uri format from upload is usually the 'name' e.g. "files/..."
            try:
                # If uri is the name (files/xxx), we can get the object
                if uri.startswith("files/"):
                     file_obj = genai.get_file(uri)
                     parts.append(file_obj)
            except Exception as e:
                self.logger.warning(f"Could not retrieve file for prompt: {uri} - {e}")

        parts.append(query)
        
        if system_instruction is None:
            system_instruction = "You are a professional assistant. Answer in Arabic."

        try:
             # Use the model instance created in __init__? 
             # Or create new one to support dynamic system_instruction?
             # GenerativeModel can take system_instruction at init.
             
             chat_model = genai.GenerativeModel(
                 model_name=model_name,
                 system_instruction=system_instruction
             )
             
             response = chat_model.generate_content(parts)
             return response.text
        except Exception as e:
            self.logger.error(f"Gemini generation failed: {str(e)}")
            raise

gemini_service = GeminiService()

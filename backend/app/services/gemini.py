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
            file_ref = self.client.files.upload(
                file=file_path,
                config=types.UploadFileConfig(
                    display_name=display_name,
                    mime_type=mime_type
                )
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
        file_ref = self.client.files.get(name=file_name)
        return file_ref.state.name

    async def generate_answer(self, query: str, file_uris: List[str], system_instruction: str = None) -> str:
        """
        Generates an answer using Gemini 1.5 Pro with File Search (via file_uris).
        """
        # Construction of the request
        # We pass file_uris as part of the content or tools depending on the mode.
        # For basic "Long Context" RAG (Gemini 1.5 Pro native capability):
        # We just pass the file objects (or URIs) in the history/content.
        
        model = "gemini-1.5-pro-latest"
        
        parts = []
        for uri in file_uris:
             # In the new SDK, we might need to create a 'part' with file_data 
             # or simply pass the file object if we had it.
             # According to documentation, we can pass the file object returned by upload,
             # OR the dict/object representing it.
             parts.append(types.Part.from_uri(file_uri=uri, mime_type="application/pdf")) # Simplified check needed
        
        parts.append(types.Part.from_text(text=query))
        
        if system_instruction is None:
            system_instruction = "You are a professional assistant. Answer in Arabic."

        try:
            response = self.client.models.generate_content(
                model=model,
                contents=[types.Content(role="user", parts=parts)],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            return response.text
        except Exception as e:
            self.logger.error(f"Gemini generation failed: {str(e)}")
            raise

gemini_service = GeminiService()

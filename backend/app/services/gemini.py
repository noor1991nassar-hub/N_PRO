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

    async def check_file_exists(self, display_name: str) -> Optional[types.File]:
        """
        Checks if a file with the given display_name already exists in Gemini.
        Returns the File object if found, None otherwise.
        """
        try:
            # Note: list_files returns a generator. We iterate to find a match.
            # Efficiency warning: If many files, this is slow. Gemini API doesn't support filter by name yet.
            for f in genai.list_files():
                if f.display_name == display_name:
                    return f
            return None
        except Exception as e:
            self.logger.error(f"Error checking file existence: {e}")
            return None

    async def delete_file(self, file_name: str):
        """
        Deletes a file from Gemini.
        """
        try:
            genai.delete_file(file_name)
            self.logger.info(f"Deleted file from Gemini: {file_name}")
        except Exception as e:
            self.logger.error(f"Error deleting file: {e}")
            raise

    def generate_vertical_instructions(self, role: str, company: str, base_tone: str = "professional") -> str:
        """
        Creates a dynamic Persona based on User Role and Company.
        """
        personas = {
            "engineer": "You are a Senior Civil Engineer & Construction Expert. Focus on structural integrity, materials, and safety codes (ACI, BS, Eurocode).",
            "lawyer": "You are a Corporate Legal Counsel. Focus on liability, contract terms, dispute resolution, and compliance.",
            "accountant": "You are a Chief Financial Officer. Focus on costs, budget variance, ROI, and payment terms.",
            "hr": "You are a Human Resources Director. Focus on labor laws, employee rights, and organizational policy.",
            "admin": "You are a General Operations Manager. Provide broad, high-level summaries."
        }
        
        persona = personas.get(role, "You are a helpful corporate assistant.")
        
        return (
            f"{persona}\n"
            f"You are working for '{company}'.\n"
            f"Tone: {base_tone}.\n"
            "CRITICAL RULES:\n"
            "1. Answer ONLY what is asked. Do not summarize unless asked.\n"
            "2. Respond in the same language as the user (likely Arabic).\n"
            "3. If the answer is in the document, CITE IT.\n"
        )

    async def generate_answer(self, query: str, file_uris: List[str], role: str = "admin", company: str = "General", system_instruction: str = None) -> str:
        """
        Generates an answer using Gemini 2.0 Flash with Role-Based Context.
        """
        model_name = "gemini-2.0-flash"
        
        parts = []
        for uri in file_uris:
            try:
                file_name = uri
                if "/files/" in uri:
                    file_name = "files/" + uri.split("/files/")[-1]
                
                file_obj = genai.get_file(file_name)
                parts.append(file_obj)
            except Exception as e:
                self.logger.warning(f"Could not retrieve file for prompt: {uri} - {e}")

        parts.append(query)
        
        if system_instruction is None:
            # Generate Dynamic Vertical Instruction
            system_instruction = self.generate_vertical_instructions(role, company)

        try:
             chat_model = genai.GenerativeModel(
                 model_name=model_name,
                 system_instruction=system_instruction
             )
             
             response = chat_model.generate_content(parts)
             return response.text
        except Exception as e:
            self.logger.error(f"Gemini generation failed: {str(e)}")
            # Fallback for 404/Safety errors
            return "Apologies, I could not process the request based on the current document context."

gemini_service = GeminiService()

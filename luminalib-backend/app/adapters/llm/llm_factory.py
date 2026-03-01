"""Factory for creating LLM adapters based on configuration"""
import logging
from typing import Optional
from app.ports.llm_port import LLMPort
from app.adapters.llm.mock_llm import MockLLMAdapter
from app.adapters.llm.openai_adapter import OpenAIAdapter
from app.adapters.llm.huggingface_adapter import HuggingFaceAdapter

logger = logging.getLogger(__name__)


class LLMAdapterFactory:
    """
    Factory for creating LLM adapters.
    
    Supports switching between different LLM providers with a single config change.
    
    Configuration (via .env or environment variables):
        LLM_PROVIDER=mock|openai|huggingface
        
    Provider-specific configs:
        # OpenAI
        OPENAI_API_KEY=sk-...
        OPENAI_MODEL=gpt-4-turbo-preview
        
        # HuggingFace
        HUGGINGFACE_MODEL=meta-llama/Llama-2-7b-chat
        HUGGINGFACE_TOKEN=hf_...
        HUGGINGFACE_DEVICE=cuda  # or cpu
        HUGGINGFACE_QUANTIZE=false
    
    Example Usage:
        >>> from app.core.config import settings
        >>> llm = LLMAdapterFactory.create(settings)
        >>> summary = await llm.generate_summary("text")
    
    Swapping Providers (just change config!):
        # Development
        LLM_PROVIDER=mock
        
        # Staging
        LLM_PROVIDER=huggingface
        HUGGINGFACE_MODEL=meta-llama/Llama-2-7b-chat
        
        # Production
        LLM_PROVIDER=openai
        OPENAI_API_KEY=sk-...
        OPENAI_MODEL=gpt-4-turbo-preview
    """
    
    @staticmethod
    def create(settings) -> LLMPort:
        """
        Create an LLM adapter based on settings.
        
        Args:
            settings: Settings object with LLM configuration
            
        Returns:
            LLMPort implementation (MockLLMAdapter, OpenAIAdapter, or HuggingFaceAdapter)
            
        Raises:
            ValueError: If provider is unknown or required config is missing
        """
        provider = settings.llm_provider.lower()
        
        if provider == "mock":
            logger.info("🔧 Using Mock LLM adapter (development mode)")
            return MockLLMAdapter()
        
        elif provider == "openai":
            logger.info("🔧 Using OpenAI LLM adapter")
            try:
                return OpenAIAdapter(
                    api_key=settings.openai_api_key,
                    model=getattr(settings, 'openai_model', 'gpt-3.5-turbo')
                )
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI adapter: {str(e)}")
                raise
        
        elif provider == "huggingface":
            logger.info("🔧 Using HuggingFace LLM adapter")
            try:
                return HuggingFaceAdapter(
                    model=getattr(settings, 'huggingface_model', 'meta-llama/Llama-2-7b-chat'),
                    device=getattr(settings, 'huggingface_device', 'cuda'),
                    quantize=getattr(settings, 'huggingface_quantize', False)
                )
            except Exception as e:
                logger.error(f"Failed to initialize HuggingFace adapter: {str(e)}")
                raise
        
        else:
            raise ValueError(
                f"Unknown LLM provider: {provider}. "
                f"Supported: mock, openai, huggingface"
            )

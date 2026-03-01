"""HuggingFace Transformers LLM adapter"""
import logging
import os
from typing import Optional
from app.ports.llm_port import LLMPort

logger = logging.getLogger(__name__)


class HuggingFaceAdapter(LLMPort):
    """
    HuggingFace Transformers adapter for local LLM models.
    
    Supports various open-source models:
    - Llama 3 (70B, 8B)
    - Mistral 7B
    - Phi 3
    - Zephyr
    - And thousands more from HuggingFace Hub
    
    Configuration:
        LLM_PROVIDER=huggingface
        HUGGINGFACE_MODEL=meta-llama/Llama-2-7b-chat
        HUGGINGFACE_TOKEN=hf_...  # Get from huggingface.co
    
    Example:
        >>> llm = HuggingFaceAdapter(model="meta-llama/Llama-2-7b-chat")
        >>> summary = await llm.generate_summary("Long book text...")
        'The book discusses...'
    
    Requirements:
        pip install transformers torch
    
    Advantages:
        - Free (no API calls)
        - Privacy (all data stays local)
        - No rate limits
        - Can run on GPU or CPU
        - Can quantize for 4-bit to reduce memory
    
    Cost Analysis:
        - One-time: Download model (2-70GB depending on size)
        - Runtime: Electricity cost (~$0.0001 per inference)
        - Total cost: Very low, perfect for production
    
    Deployment Options:
        1. Local GPU: Fast, best quality
        2. CPU: Slower but works anywhere
        3. Quantized (4-bit): Fast + low memory (RTX 3060+ can run 70B)
    """
    
    def __init__(
        self,
        model: str = "meta-llama/Llama-2-7b-chat",
        device: str = "cuda",  # or "cpu"
        quantize: bool = False
    ):
        """
        Initialize HuggingFace adapter.
        
        Args:
            model: HuggingFace model ID (e.g., meta-llama/Llama-2-7b-chat)
            device: "cuda" for GPU, "cpu" for CPU
            quantize: Use 4-bit quantization for lower memory (requires bitsandbytes)
        """
        try:
            from transformers import (
                AutoTokenizer,
                AutoModelForCausalLM,
                BitsAndBytesConfig
            )
            import torch
        except ImportError:
            raise ImportError(
                "transformers and torch are required for HuggingFace adapter. "
                "Install with: pip install transformers torch"
            )
        
        self.model_name = model
        self.device = device
        
        logger.info(f"✓ Loading HuggingFace model: {model}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        
        # Configure quantization if requested
        model_kwargs = {
            "device_map": "auto" if device == "cuda" else device,
            "torch_dtype": torch.float16 if device == "cuda" else torch.float32
        }
        
        if quantize:
            try:
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
                model_kwargs["quantization_config"] = quantization_config
                logger.info("✓ Using 4-bit quantization (reduced memory)")
            except ImportError:
                logger.warning("bitsandbytes not installed, skipping quantization. Install with: pip install bitsandbytes")
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(model, **model_kwargs)
        
        logger.info(f"✓ HuggingFace model loaded: {model}")
    
    async def generate_summary(self, text: str, max_length: int = 200) -> str:
        """Generate summary using HuggingFace model"""
        try:
            prompt = f"""Summarize the following text in approximately {max_length} words:

{text}

Summary:"""
            
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=int(max_length * 1.5),
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
            
            summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Remove the prompt from output
            summary = summary.replace(prompt, "").strip()
            
            logger.debug(f"✓ Generated summary via HuggingFace ({len(summary)} chars)")
            return summary
        
        except Exception as e:
            logger.error(f"❌ HuggingFace summary generation failed: {str(e)}")
            raise
    
    async def generate_recommendation_reason(self, book_title: str, user_preferences: dict) -> str:
        """Generate recommendation reason using HuggingFace"""
        try:
            prefs_str = ", ".join(f"{k}: {v}" for k, v in user_preferences.items())
            
            prompt = f"""Explain why this book is recommended based on user preferences:
Book: '{book_title}'
User preferences: {prefs_str}

Recommendation reason:"""
            
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
            
            reason = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            reason = reason.replace(prompt, "").strip()
            
            logger.debug(f"✓ Generated recommendation reason via HuggingFace")
            return reason
        
        except Exception as e:
            logger.error(f"❌ HuggingFace recommendation generation failed: {str(e)}")
            raise
    
    async def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment using HuggingFace pipeline"""
        try:
            from transformers import pipeline
            
            # Use a lightweight sentiment analysis model
            sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            
            result = sentiment_pipeline(text[:512])[0]  # Limit to 512 tokens
            
            sentiment_map = {
                "POSITIVE": "positive",
                "NEGATIVE": "negative",
                "NEUTRAL": "neutral"
            }
            
            return {
                "sentiment": sentiment_map.get(result['label'], "neutral"),
                "score": result['score'],
                "confidence": result['score']
            }
        
        except Exception as e:
            logger.error(f"❌ HuggingFace sentiment analysis failed: {str(e)}")
            raise
    
    async def extract_keywords(self, text: str, max_keywords: int = 5) -> list[str]:
        """Extract keywords using TF-IDF (no LLM needed)"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            import numpy as np
            
            # Simple TF-IDF based keyword extraction
            vectorizer = TfidfVectorizer(
                max_features=max_keywords,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            X = vectorizer.fit_transform([text])
            keywords = vectorizer.get_feature_names_out()
            
            logger.debug(f"✓ Extracted keywords via HuggingFace")
            return list(keywords[:max_keywords])
        
        except Exception as e:
            logger.error(f"❌ HuggingFace keyword extraction failed: {str(e)}")
            # Fallback to simple extraction
            words = text.split()
            return sorted(set(words), key=len, reverse=True)[:max_keywords]

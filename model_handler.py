"""AI Model Handler for Text RPG"""

from unsloth import FastLanguageModel

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import os


class ModelHandler:
    def __init__(self,
                 model_name: str = "Qwen/Qwen3-4B-Instruct-2507",
                 local_model_path: str = None,
                 max_new_tokens: int = 4092):
        """
        Initialize the model handler with 4-bit quantization
        """
        self.model_name = model_name
        self.local_model_path = local_model_path
        self.max_new_tokens = max_new_tokens
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_model(self):
        """Load the model with 4-bit quantization"""
        model_path = f"./models/{self.model_name}"

        print(f"Loading model from: {model_path}")
        print(f"Device: {self.device}")

        # Configure 4-bit quantization
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name = model_path,
            max_seq_length = 9192,
            dtype = None,
            load_in_4bit = True,
        )

        self.model = model
        self.tokenizer = tokenizer

        FastLanguageModel.for_inference(self.model)

        print("Model loaded successfully!")

    def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """
        Generate a response from the model
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Format the prompt
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=self.max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                use_cache=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

        generated_ids = outputs[0][inputs["input_ids"].shape[1]:]
        response = self.tokenizer.decode(generated_ids, skip_special_tokens=True)

        return response.strip()

    def unload_model(self):
        """Unload the model to free memory"""
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        print("Model unloaded successfully!")

import os
import yaml
import json
from . import config

DEFAULT_PROMPT = "Please format the following transcribed text with proper punctuation, capitalization, and clear structure."

class PromptManager:
    def __init__(self):
        self.current_prompt = DEFAULT_PROMPT
        self.style_guide_content = ""
        self.style_guide_path = ""
    
    def get_default_prompt(self) -> str:
        """Get the default formatting prompt."""
        return DEFAULT_PROMPT
    
    def set_prompt(self, prompt: str):
        """Set the current formatting prompt."""
        self.current_prompt = prompt.strip() if prompt.strip() else DEFAULT_PROMPT
        config.save_setting(config.KEY_PROMPT_TEXT, self.current_prompt)
    
    def get_prompt(self) -> str:
        """Get the current formatting prompt."""
        return self.current_prompt
    
    def load_style_guide(self, file_path: str) -> bool:
        """
        Load a style guide from YAML or JSON file.
        Returns True if successful, False otherwise.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    data = json.load(f)
                    self.style_guide_content = json.dumps(data, indent=2)
                else:  # YAML
                    data = yaml.safe_load(f)
                    self.style_guide_content = yaml.dump(data, default_flow_style=False)
            
            self.style_guide_path = file_path
            config.save_setting(config.KEY_STYLE_GUIDE_PATH, file_path)
            return True
        except Exception:
            return False
    
    def get_style_guide(self) -> str:
        """Get the current style guide content."""
        return self.style_guide_content
    
    def get_style_guide_path(self) -> str:
        """Get the path to the currently loaded style guide."""
        return self.style_guide_path
    
    def clear_style_guide(self):
        """Clear the current style guide."""
        self.style_guide_content = ""
        self.style_guide_path = ""
        config.save_setting(config.KEY_STYLE_GUIDE_PATH, "")
    
    def load_from_config(self):
        """Load prompt and style guide from persistent config."""
        # Load prompt
        saved_prompt = config.load_setting(config.KEY_PROMPT_TEXT, DEFAULT_PROMPT)
        self.current_prompt = saved_prompt
        
        # Load style guide
        saved_style_path = config.load_setting(config.KEY_STYLE_GUIDE_PATH, "")
        if saved_style_path and os.path.exists(saved_style_path):
            self.load_style_guide(saved_style_path)
    
    def get_combined_instructions(self) -> str:
        """
        Get combined formatting instructions including prompt and style guide.
        This is used by the formatter API.
        """
        instructions = "You are an assistant that formats and edits transcribed text.\n"
        
        if self.style_guide_content:
            instructions += f"Follow the style guide and instructions provided.\nStyle Guide:\n{self.style_guide_content}\n"
        
        if self.current_prompt:
            instructions += f"Instructions: {self.current_prompt}\n"
        else:
            instructions += "Instructions: Fix grammar and punctuation, and format the text clearly.\n"
        
        return instructions
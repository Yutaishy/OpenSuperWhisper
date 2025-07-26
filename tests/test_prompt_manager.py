import tempfile
import json
import yaml
import OpenSuperWhisper.prompt_manager as pm

def test_default_prompt():
    manager = pm.PromptManager()
    assert manager.get_default_prompt() == pm.DEFAULT_PROMPT
    assert manager.get_prompt() == pm.DEFAULT_PROMPT

def test_set_and_get_prompt():
    manager = pm.PromptManager()
    test_prompt = "Format this text nicely."
    manager.set_prompt(test_prompt)
    assert manager.get_prompt() == test_prompt

def test_set_empty_prompt_uses_default():
    manager = pm.PromptManager()
    manager.set_prompt("")
    assert manager.get_prompt() == pm.DEFAULT_PROMPT
    
    manager.set_prompt("   ")
    assert manager.get_prompt() == pm.DEFAULT_PROMPT

def test_load_json_style_guide(tmp_path):
    manager = pm.PromptManager()
    
    # Create test JSON style guide
    style_data = {
        "tone": "formal",
        "avoid": ["slang"],
        "preferred_spelling": {"color": "colour"}
    }
    
    json_file = tmp_path / "test_style.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(style_data, f)
    
    success = manager.load_style_guide(str(json_file))
    assert success == True
    assert manager.get_style_guide_path() == str(json_file)
    assert "formal" in manager.get_style_guide()

def test_load_yaml_style_guide(tmp_path):
    manager = pm.PromptManager()
    
    # Create test YAML style guide
    style_data = {
        "tone": "casual",
        "formatting": ["Use bullet points"]
    }
    
    yaml_file = tmp_path / "test_style.yaml"
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(style_data, f)
    
    success = manager.load_style_guide(str(yaml_file))
    assert success == True
    assert "casual" in manager.get_style_guide()

def test_load_nonexistent_style_guide():
    manager = pm.PromptManager()
    success = manager.load_style_guide("nonexistent_file.yaml")
    assert success == False
    assert manager.get_style_guide() == ""

def test_clear_style_guide(tmp_path):
    manager = pm.PromptManager()
    
    # Load a style guide first
    style_data = {"tone": "formal"}
    yaml_file = tmp_path / "test_style.yaml"
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(style_data, f)
    
    manager.load_style_guide(str(yaml_file))
    assert manager.get_style_guide() != ""
    
    # Clear it
    manager.clear_style_guide()
    assert manager.get_style_guide() == ""
    assert manager.get_style_guide_path() == ""

def test_get_combined_instructions():
    manager = pm.PromptManager()
    
    # Test with default prompt only
    instructions = manager.get_combined_instructions()
    assert "You are an assistant" in instructions
    assert pm.DEFAULT_PROMPT in instructions
    
    # Test with custom prompt
    manager.set_prompt("Custom formatting instructions")
    instructions = manager.get_combined_instructions()
    assert "Custom formatting instructions" in instructions
    
    # Test with style guide
    manager.style_guide_content = "tone: formal"
    instructions = manager.get_combined_instructions()
    assert "Style Guide:" in instructions
    assert "tone: formal" in instructions
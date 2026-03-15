"""
Formatter utilities for text processing and bold formatting.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


def add_bold_formatting_to_data(
    data: List[Dict[str, Any]],
    output_file: str,
    regenerated_output_key: str = "answer_hidden_response",
    final_output_key: str = "answer_hidden_response_bold",
    position: int = 0,
    char: str = "\u2026",
    add_bold_to_word_func: Optional[callable] = None,
    verbose: bool = True
) -> str:
    """
    Add bold formatting to specified position word in regenerated text.
    
    Args:
        data: List of dictionaries containing text data
        output_file: Path to save the processed data
        regenerated_output_key: Key name for regenerated text in data
        final_output_key: Key name for final formatted text in data
        position: Word position to apply bold formatting (0-indexed)
        char: Character to add (default: ellipsis)
        add_bold_to_word_func: Function to apply bold formatting
        verbose: Print progress messages
        
    Returns:
        str: Path to saved file
    """
    # Import add_bold_to_word if not provided
    if add_bold_to_word_func is None:
        try:
            # Try importing from utils directory first
            from .add_char import add_bold_to_word
            add_bold_to_word_func = add_bold_to_word
        except ImportError:
            try:
                # Fallback: try absolute import
                from utils.add_char import add_bold_to_word
                add_bold_to_word_func = add_bold_to_word
            except ImportError as e:
                raise ImportError(f"Could not import add_bold_to_word: {e}")
    
    # Process each item
    for index, item in enumerate(data):
        regenerated_text = item.get(regenerated_output_key, "")
        
        if not regenerated_text:
            if verbose:
                print(f"Item {index}: Skipped (no regenerated text)")
            item[final_output_key] = regenerated_text
            continue
        
        # Apply bold formatting
        bold_text = add_bold_to_word_func(
            regenerated_text, 
            position=position + 1,  # Convert to 1-indexed
            char=char
        )
        
        item[final_output_key] = bold_text
        if verbose:
            print(f"Item {index}: Bold formatting added")
    
    # Save data
    saved_file = save_data(output_file, data)
    
    return saved_file


def save_data(file_path: str, data: List[Dict[str, Any]]) -> str:
    """
    Save data to JSON or CSV file.
    
    Args:
        file_path: Path to save file
        data: List of dictionaries to save
        
    Returns:
        str: Path to saved file
    """
    file_path = Path(file_path)
    
    if file_path.suffix.lower() == '.csv':
        # For CSV, save as JSON instead to preserve structure
        json_file = file_path.with_suffix('.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return str(json_file)
    else:
        # Save as JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return str(file_path)

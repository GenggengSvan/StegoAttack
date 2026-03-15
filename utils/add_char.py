"""
JSON processor to add bold formatting (**) to the first word of each sentence.
"""

import json
import re
from pathlib import Path


def add_bold_to_word(text: str, position = "around", char: str = "**") -> str:
    """
    Add specified character(s) to a word in each sentence.
    
    Args:
        text: Input text with multiple sentences.
        position: Where to add the character(s). Options:
                 - "before": Add char before the word
                 - "after": Add char after the word
                 - "around": Add char before and after the word (default)
                 - int: Add char to the Nth word in each sentence (1-indexed)
        char: The character(s) to add (default is "**")
        
    Returns:
        Text with specified word(s) marked with specified character(s).
    """
    if not text:
        return text
    
    # Validate position parameter
    if isinstance(position, str):
        if position not in ("before", "after", "around"):
            raise ValueError("position must be 'before', 'after', 'around', or an integer")
        position_type = "string"
    elif isinstance(position, int):
        if position < 1:
            raise ValueError("position must be a positive integer (1-indexed)")
        position_type = "int"
        target_word_index = position
    else:
        raise ValueError("position must be a string ('before', 'after', 'around') or an integer")
    
    # Split text into sentences (. ! ?)
    sentence_pattern = r'([^.!?]*[.!?])'
    sentences = re.findall(sentence_pattern, text)
    
    if not sentences:
        sentences = [text]
    
    result = []
    
    for sentence in sentences:
        if not sentence.strip():
            continue
        
        if position_type == "string":
            # Handle string positions: before, after, around (apply to first word)
            word_match = re.match(r'^(\s*)(\**)?(\w+)(\**)?', sentence)
            
            if word_match:
                leading_space = word_match.group(1)
                first_word = word_match.group(3)  # Get the word without symbols
                rest_of_sentence = sentence[word_match.end():]
                
                # Add char based on position
                if position == "before":
                    new_sentence = f"{leading_space}{char}{first_word}{rest_of_sentence}"
                elif position == "after":
                    new_sentence = f"{leading_space}{first_word}{char}{rest_of_sentence}"
                else:  # around
                    new_sentence = f"{leading_space}{char}{first_word}{char}{rest_of_sentence}"
                result.append(new_sentence)
            else:
                result.append(sentence)
        
        else:
            # Handle integer positions: apply to Nth word
            words = re.findall(r'\w+|\W+', sentence)
            
            word_count = 0
            for i, token in enumerate(words):
                if re.match(r'\w+', token):
                    word_count += 1
                    if word_count == target_word_index:
                        # Extract the word, removing any surrounding symbols
                        # Remove common symbols like **, __, etc. from the beginning and end
                        cleaned_word = token.strip('*_[]() ')
                        
                        # Add char around the cleaned word
                        words[i] = f"{char}{cleaned_word}{char}"
                        break
            
            result.append(''.join(words))
    
    return ''.join(result)


def process_json_key(input_file: str, output_file: str, key: str, position = "around", char: str = "**") -> None:
    """
    Process a JSON file and add specified character(s) to a word in each sentence.
    
    Args:
        input_file: Path to input JSON file.
        output_file: Path to output JSON file.
        key: The key in the JSON objects to process.
        position: Where to add the character(s). Options:
                 - "before": Add char before the word
                 - "after": Add char after the word
                 - "around": Add char before and after the word (default)
                 - int: Add char to the Nth word in each sentence (1-indexed)
        char: The character(s) to add (default is "**")
        
    Raises:
        FileNotFoundError: If input file doesn't exist.
        json.JSONDecodeError: If input file is not valid JSON.
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Load JSON data
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both list and dict inputs
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = [data]
    else:
        raise ValueError("JSON must be a list or dictionary")
    
    # Process each item
    processed_count = 0
    for item in items:
        if key in item and isinstance(item[key], str):
            original_text = item[key]
            item[key] = add_bold_to_word(original_text, position=position, char=char)
            processed_count += 1
    
    # Save to output file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"Processing completed:")
    print(f"  - Input file: {input_file}")
    print(f"  - Output file: {output_file}")
    print(f"  - Key processed: {key}")
    print(f"  - Position: {position}")
    print(f"  - Character(s): {char}")
    print(f"  - Items processed: {processed_count}")


def main():
    """
    Main function to process JSON file with user input.
    """
    print("=" * 60)
    print("JSON Bold Formatter - Add ** to first word of each sentence")
    print("=" * 60)
    
    # Get input from user
    input_file = "test_mask_input.json"
    key = "answer_hidden_response"
    output_file = "test_mask_input.json"
    
    if not output_file:
        output_file = input_file
    
    try:
        process_json_key(input_file, output_file, key)
        print("\n✓ Processing completed successfully!")
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
    except json.JSONDecodeError as e:
        print(f"\n✗ JSON decode error: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()

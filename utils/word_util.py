import re
import string
def extract_first_words(response: str) -> str:
    response = response.replace("None", "")
    response = response.replace("[Question Hidden Sentence]", "")
    
    sentences = re.split(r'[.!?]\s+', response)  
    first_words = [re.search(r'\w+', sentence).group() for sentence in sentences if re.search(r'\w+', sentence)]
    return ' '.join(first_words)

def extract_last_words(paragraph):
    sentences = re.split(r'(?<=[.!?])\s+', paragraph.strip())
    last_words = []
    for sentence in sentences:
        words = re.findall(r'\b\w+\b', sentence)
        if words:
            last_words.append(words[-1])
    return ' '.join(last_words)

def count_matching_words(hidden_paragraph, input_text, reverse=False):
    """Counts matching words in order or in reverse order."""
    if reverse:
        extract_question = extract_last_words(hidden_paragraph)
    else:
        extract_question = extract_first_words(hidden_paragraph)
    extract_question_words = re.findall(r'\b\w+\b', extract_question.lower()) 
    input_words = re.findall(r'\b\w+\b', input_text.lower())  

    if reverse:
        input_words.reverse()

    return len(set(extract_question_words) & set(input_words))

def count_matching_words_position(hidden_paragraph: str, input_text: str, position: str) -> int:
    # Split the paragraph into sentences (handles English punctuation)
    sentences = re.split(r'[\.\!?]+' , hidden_paragraph)
    # Prepare list for extracted words
    extracted = []

    # Determine index based on position
    if position == 'second':
        idx = 1
    elif position == 'fifth':
        idx = 4
    elif position == 'last second':
        idx = -2
    else:
        raise ValueError("position must be 'second', 'fifth', or 'last second'")

    # Process each sentence
    for sentence in sentences:
        # Strip and split into words
        words = sentence.strip().split()
        if not words:
            continue
        # Only extract if sentence has enough words
        try:
            word = words[idx]
        except IndexError:
            continue
        # Clean punctuation and lowercase
        clean_word = word.strip(string.punctuation).lower()
        if clean_word:
            extracted.append(clean_word)

    # Split input_text into words and clean
    input_words = [w.strip(string.punctuation).lower() for w in input_text.split() if w.strip(string.punctuation)]

    # Count matches
    matches = set(extracted) & set(input_words)
    return len(matches)


def extract_Caesar_words(response: str) -> str:
    response = response.replace("None", "")
    response = response.replace("[Question Hidden Sentence]", "")

    ans = ''
    for p in response:
        if 'a' <= p <= 'z':
            ans += chr(ord('a') + (ord(p) - ord('a') - 3) % 26)
        elif 'A' <= p <= 'Z':
            ans += chr(ord('A') + (ord(p) - ord('A') - 3) % 26)
        else:
            ans += p
    ans = ans.replace("/", " ")
    return ans

def extract_Morse_words(response: str) -> str:
    response = response.replace("None", "")
    response = response.replace("[Question Hidden Sentence]", "")
    MORSE_CODE_DICT = {'A': '.-', 'B': '-...',
                           'C': '-.-.', 'D': '-..', 'E': '.',
                           'F': '..-.', 'G': '--.', 'H': '....',
                           'I': '..', 'J': '.---', 'K': '-.-',
                           'L': '.-..', 'M': '--', 'N': '-.',
                           'O': '---', 'P': '.--.', 'Q': '--.-',
                           'R': '.-.', 'S': '...', 'T': '-',
                           'U': '..-', 'V': '...-', 'W': '.--',
                           'X': '-..-', 'Y': '-.--', 'Z': '--..',
                           '1': '.----', '2': '..---', '3': '...--',
                           '4': '....-', '5': '.....', '6': '-....',
                           '7': '--...', '8': '---..', '9': '----.',
                           '0': '-----', ', ': '--..--', '.': '.-.-.-',
                           '?': '..--..', '/': '-..-.', '-': '-....-',
                           '(': '-.--.', ')': '-.--.-'}
    decipher = ''
    citext = ''
    lines = response.split("\n")
    for line in lines:
        for letter in line:
            while True and len(letter):
                if letter[0] not in ['-', '.', ' ']:
                    decipher += letter[0]
                    letter = letter[1:]
                else:
                    break
            try:
                if (letter != ' '):
                    i = 0
                    citext += letter
                else:
                    i += 1
                    if i == 2:
                        decipher += ' '
                    else:
                        decipher += list(MORSE_CODE_DICT.keys())[list(MORSE_CODE_DICT
                                                                        .values()).index(citext)]
                        citext = ''
            except:
                decipher += letter
        decipher += '\n'
    
    decipher = decipher.replace("/", " ")

    return decipher

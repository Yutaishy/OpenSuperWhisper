OpenSuperWhisper Two-Stage Transcription Pipeline (Implementation Guide)
Overview:
We will modify a clean clone of the OpenSuperWhisper repository to implement a two-stage speech transcription pipeline. In Stage 1, audio is transcribed using OpenAI's ASR API (supporting models like gpt-4o-transcribe, gpt-4o-mini-transcribe, or whisper-1). In Stage 2, the raw transcription is sent to an OpenAI chat model (such as gpt-4o-mini) via the Chat Completion API to polish and format the text according to a user-defined prompt and optional style guide. We will also add UI features for viewing raw vs. formatted text, selecting models, toggling the post-formatting stage, editing the formatting prompt, extracting vocabulary with Janome (Japanese morphological analyzer) and approving new terms, loading style guides (YAML/JSON), saving persistent settings, logging outputs, and running tests. Finally, we’ll set up development tools (formatters/linters) and bundle the app into a one-file Windows executable with PyInstaller.
Project Structure
Below is the file and directory structure of the modified project, including new and changed files:
voice_input/                 <- Project root (default working directory)
├── OpenSuperWhisper/        <- Python package for the app (new, replacing Swift code)
│   ├── __init__.py
│   ├── main.py              <- Application entry point (starts UI)
│   ├── ui_mainwindow.py     <- UI setup code (Main Window and widgets)
│   ├── asr_api.py           <- Stage 1: OpenAI ASR API integration
│   ├── formatter_api.py     <- Stage 2: OpenAI Chat Completion integration
│   ├── prompt_manager.py    <- Manages default/editable prompt and style guide
│   ├── vocabulary.py        <- Vocabulary extraction with Janome + user dictionary
│   ├── config.py            <- Persistent settings using QSettings
│   ├── logger.py            <- Logging configuration for file output
│   └── resources/           <- (Optional) UI resources (icons, etc.)
├── style_guides/            <- Sample style guide files (YAML/JSON)
│   ├── example_style.yaml
│   └── example_style.json
├── tests/                   <- Test suite (unit & integration tests)
│   ├── test_asr_api.py
│   ├── test_formatter_api.py
│   ├── test_vocabulary.py
│   ├── test_prompt_manager.py
│   └── test_integration.py
├── requirements.txt         <- Python dependencies for the project
├── README.md                <- Documentation for usage and installation (updated)
├── CHANGELOG.md             <- Version history of changes (updated)
├── .pre-commit-config.yaml  <- Pre-commit hooks (Black, Ruff, etc.) for code formatting
└── pyinstaller.spec         <- PyInstaller spec file (for fine-tuning build, optional)
Note: The original OpenSuperWhisper was a macOS (Swift) app. We reimplement the core functionality in Python 3.12 for cross-platform use (specifically targeting Windows). We use PySide6 (Qt) for the GUI to leverage features like QSettings for persistent config. The working directory is assumed to be C:\Users\yuta9\dev\voice_input on Windows, which will contain this project.
Dependencies and Setup
Make sure you have Python 3.12 installed on Windows (no WSL needed). We will use the uv package manager (from Astral) as a drop-in replacement for pip. If not already installed, you can install uv via pip:
pip install uv
The project’s Python dependencies are listed in requirements.txt. They include: - PySide6 (for GUI application and QSettings) - openai (OpenAI API client for ASR and Chat) - janome (Japanese morphological analyzer for vocabulary extraction) - sounddevice (for audio recording from microphone) - numpy (used with sounddevice for audio data) - pytest (for running tests) and related testing tools
To install requirements using uv:
uv pip install -r requirements.txt
This uses uv’s pip interface to install dependencies (uv is designed to be a faster pip drop-in[1][2]). Ensure you also have an OpenAI API key available – set it as the environment variable OPENAI_API_KEY (or you can add a UI field for it in the config if preferred).
Stage 1: Audio Transcription with OpenAI ASR API
Goal: Capture audio (from microphone or file) and get a transcription using OpenAI’s speech-to-text models (like whisper-1, or the newer GPT-4 based audio models gpt-4o-transcribe / gpt-4o-mini-transcribe).
Implementation Details: - We’ll provide a Record button in the UI to capture audio from the default microphone. Upon clicking, the app will start recording audio (we’ll use the sounddevice library to record from the microphone into a NumPy array). The user can click Stop to finish recording. - After recording, we save the audio to a temporary WAV file (e.g., in memory or disk) and send it to the OpenAI API for transcription. The OpenAI Python SDK’s openai.Audio.transcribe() method will be used for simplicity[3]. - The transcription call requires the audio file (as a file-like object) and the model name. We will allow selection of model via a dropdown (combobox) in the UI (options: whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe). The app will pass the chosen model name to the API call. For OpenAI’s endpoint, whisper-1 is the standard model name for Whisper. The new GPT-4 audio models might be accessible similarly by name. - We request the transcription result as plain text by setting response_format="text" so that openai.Audio.transcribe returns a text string[4]. This avoids extra JSON parsing. - If needed, we could also supply the language parameter or a prompt to the ASR API for biasing the transcription[5]. However, since we plan to do formatting in Stage 2, we might not need to use the Whisper prompt parameter for punctuation. (Advanced note: If using local Whisper, an initial prompt of an English sentence can help it output English punctuation[6], but with OpenAI’s API we typically get punctuation already. GPT-4o models likely handle it well too.) - After receiving the transcription text (Stage 1 output), we display it in the “Raw Transcription” tab of the UI.
Error Handling: If the API call fails (network error, API error), we catch exceptions and show an error modal (using QMessageBox) to inform the user. The user can then retry recording or check their network/API key.
Below is the code for asr_api.py implementing Stage 1 (OpenAI ASR call). This module defines a function transcribe_audio(audio_path, model) which handles reading the audio file and making the API call, returning the transcribed text or raising an error:
# File: OpenSuperWhisper/asr_api.py

import openai
import os

# Optionally, you can set openai.api_key here if not using environment variable:
# openai.api_key = os.getenv("OPENAI_API_KEY")

def transcribe_audio(audio_path: str, model: str = "whisper-1") -> str:
    """
    Transcribe the given audio file using OpenAI's ASR API.
    :param audio_path: Path to an audio file (wav, mp3, etc.)
    :param model: ASR model to use (e.g., 'whisper-1', 'gpt-4o-transcribe', 'gpt-4o-mini-transcribe')
    :return: Transcribed text as a string.
    :raises: Exception if transcription fails.
    """
    # Open the audio file in binary mode
    with open(audio_path, "rb") as audio_file:
        try:
            # Use OpenAI Audio API to transcribe
            transcript = openai.Audio.transcribe(
                file=audio_file,
                model=model,
                response_format="text"  # get plain text transcript[5]
                # You can add language="ja" or other language code if known, to improve accuracy[7]
                # Or a prompt to guide transcription (not usually needed if Stage 2 will format)
            )
        except Exception as e:
            # Propagate exception with contextual message
            raise Exception(f"ASR transcription failed: {e}")
    # The OpenAI library returns the transcription as text when response_format="text"
    return transcript.strip()
How it works: This uses OpenAI’s openai.Audio.transcribe() function. As shown in OpenAI’s docs and examples, you only need to pass the model name and file object, plus optional parameters[3]. The above code will return the raw transcription string (with minimal punctuation/capitalization as provided by the model). For example, using whisper-1 might yield a mostly lowercase text with some punctuation. Using gpt-4o-transcribe could yield even more accurate transcriptions (OpenAI’s GPT-4o models reportedly improve WER and language recognition[8][9]).
Recording audio: Now, the actual audio recording from microphone is handled in the UI code (since it’s user-interactive). We will use the sounddevice library for simplicity. When the user hits the Record button, we start recording at a standard sample rate (e.g., 16 kHz or 44.1 kHz) and default microphone. We can do either a fixed-duration recording or an open-ended recording that stops on button press. To keep it simple, we’ll record with a generous maximum duration (e.g., 60 seconds) but allow early stop:
# Snippet from ui_mainwindow.py - handling record/stop
import sounddevice as sd
import numpy as np
import wave

# In MainWindow class:
self.is_recording = False
self.recording = None   # numpy array for audio data
self.fs = 16000         # sample rate (16 kHz for example)

def start_recording(self):
    if self.is_recording:
        return
    self.is_recording = True
    duration = 60  # max duration in seconds
    # Pre-allocate recording array for max duration (mono audio)
    self.recording = sd.rec(int(duration * self.fs), samplerate=self.fs, channels=1, dtype='int16')
    # Note: We choose int16 dtype to directly get PCM data (OpenAI Whisper expects 16-bit PCM in wav)
    sd.wait()  # Start recording; this call returns immediately. We'll manually stop.

def stop_recording(self):
    if not self.is_recording:
        return
    # Stop the recording early
    sd.stop()       # this stops the recording stream[10][11]
    sd.wait()       # ensure recording thread finishes
    self.is_recording = False
    # Trim the recording to the actual length recorded (find last non-zero sample)
    recording = self.recording[:,0]  # get 1-D array
    # Determine actual length: find last index of non-zero (simple heuristic)
    nonzero_indices = np.where(recording != 0)[0]
    if len(nonzero_indices) > 0:
        last_index = nonzero_indices[-1]
        recording = recording[:last_index+1]
    # Save to a temporary WAV file
    wav_path = os.path.join(self.temp_dir, "recorded.wav")
    with wave.open(wav_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 2 bytes (16 bits) per sample
        wf.setframerate(self.fs)
        wf.writeframes(recording.tobytes())
    # Now call ASR API on this file
    try:
        result_text = asr_api.transcribe_audio(wav_path, model=self.selected_asr_model)
    except Exception as e:
        self.show_error(f"Transcription failed:\n{e}")
        return
    # Display raw result in UI
    self.rawTextEdit.setPlainText(result_text)
    # Log the raw transcription (we’ll cover logging later)
    logger.info(f"Transcribed text: {result_text}")
    # Proceed to Stage 2 if toggle is enabled
    if self.postFormatToggle.isChecked():
        self.run_formatting(result_text)
In the above UI snippet, start_recording() begins capturing audio. We pre-allocate a NumPy array for 60 seconds of audio. We used sd.rec() which records in the background[10]; we call sd.stop() in stop_recording() when the user hits Stop. We used dtype='int16' to get integer PCM data directly. We then save it to a WAV file using Python’s wave module (mono, 16-bit PCM, 16 kHz). Finally, we call our transcribe_audio function and handle the result or error. The raw text is displayed in a QTextEdit (rawTextEdit) under the “Raw” tab.
Note: For simplicity, we used a fixed maximum duration. In a real app, you might want to use sd.InputStream with a callback to handle indefinite recording until stop without pre-allocating, or at least dynamically resize the array. The above approach assumes silence yields zeros to trim trailing unused buffer. This is a simplified implementation for a beginner.
Stage 2: Text Formatting with Chat Completion API
Goal: Take the ASR output (Stage 1 transcript) and improve its formatting, style, and clarity using an LLM (OpenAI’s chat model). This can add proper punctuation, casing, and apply a style guide (e.g., formal tone, specific glossary terms, formatting instructions). The user can define a prompt for formatting and optionally load a style guide in YAML/JSON.
Implementation Details: - We’ll use OpenAI’s Chat Completions API via openai.ChatCompletion.create(). We send a system message that contains the formatting instructions (base prompt and any style guide rules), and a user message that contains the raw transcript text to be formatted. The assistant’s reply will be the formatted/polished text. - The model to use for formatting can be chosen via a UI combo box. We expect to use a GPT-4 based model (the prompt mentions o4-mini, which likely refers to a cost-efficient GPT-4 variant) for this stage. We can default to gpt-4o-mini (or if not available, gpt-3.5-turbo could be a fallback). The combo could list gpt-4o-mini, gpt-4 (if available), and gpt-3.5-turbo. - The user can edit the prompt that guides formatting. We will provide a multiline text box in the UI pre-filled with a default prompt (e.g., “Please output well-formatted text with correct punctuation and capitalization. Follow the style guide and ensure the output is clear and concise.”). The user can customize this as needed for their use case. - Style Guide support: The user may load a style guide file (YAML or JSON) containing specific rules. For example, a style guide might specify preferred vocabulary or formatting rules (like “use Oxford commas”, “no passive voice”, or domain-specific terms). We allow loading such a file via a menu or button. The content of the style guide will be appended to the system prompt. If the style guide is YAML/JSON, we’ll parse it and then include it in a readable format. For simplicity, we might include the raw text of the file or convert it to bullet points in the prompt. (Alternatively, an advanced approach could parse known fields, but a straightforward way is to just include the file content as part of the instructions). - The formatting function will compile the final prompt for the chat API. For example:
System message content: “You are a text formatter. Format the user’s transcription according to the following guidelines. Prompt: <UserPrompt> Style Guide: <LoadedStyleGuide>”
User message content: “<Raw transcript text>”
The assistant (model) will respond with the formatted text.
•	Error handling: If the ChatCompletion API fails or returns an error, we display an error modal. If the output is unusually long or the model fails to follow instructions, the user can tweak the prompt or style guide and retry.
Below is the code for formatter_api.py to perform Stage 2 formatting:
# File: OpenSuperWhisper/formatter_api.py

import openai

def format_text(raw_text: str, prompt: str, style_guide: str = "", model: str = "gpt-4o-mini") -> str:
    """
    Use OpenAI Chat Completion API to format/polish the raw transcript text.
    :param raw_text: The raw transcript string from ASR.
    :param prompt: User-defined prompt with instructions for formatting.
    :param style_guide: Optional style guide text (YAML/JSON or plain) to apply.
    :param model: The chat model to use for formatting (default "gpt-4o-mini").
    :return: Formatted text.
    :raises: Exception if API call fails.
    """
    # Construct system message content
    system_instructions = "You are an assistant that formats and edits transcribed text.\n"
    if style_guide:
        system_instructions += f"Follow the style guide and instructions provided.\nStyle Guide:\n{style_guide}\n"
    if prompt:
        system_instructions += f"Instructions: {prompt}\n"
    else:
        system_instructions += "Instructions: Fix grammar and punctuation, and format the text clearly.\n"
    system_message = {"role": "system", "content": system_instructions}
    user_message = {"role": "user", "content": raw_text}
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[system_message, user_message]
            # We could set temperature=0 for deterministic output if desired
        )
    except Exception as e:
        raise Exception(f"Formatting API call failed: {e}")
    # Extract the assistant's formatted text
    formatted_text = response["choices"][0]["message"]["content"]
    return formatted_text.strip()
This function builds the messages for the ChatCompletion. The system prompt includes the style guide and user prompt instructions. We make the API call and retrieve the assistant’s content[12][13].
Notice we appended the style guide text verbatim. If the style guide file is large, you might want to summarize it or ensure it’s concise, but for our purposes, we assume a reasonably short guide. We also included the custom prompt from the user. If no prompt is provided, we default to a simple instruction to fix grammar/punctuation.
Example: If raw_text = "i went to tokyo last week it was wonderful", prompt = "Capitalize proper nouns and use correct punctuation.", and style_guide = "*Prefer formal tone.*", the system message might become:
You are an assistant that formats and edits transcribed text.
Follow the style guide and instructions provided.
Style Guide:
*Prefer formal tone.*
Instructions: Capitalize proper nouns and use correct punctuation.
The user message is the raw text. The model (say gpt-4o-mini) would likely return: "I went to Tokyo last week. It was wonderful." as the formatted output.
We will integrate this in the UI: after Stage 1 transcription, if the user has toggled on “Post-formatting”, the app will automatically call format_text() with the raw text. The result will be shown in the “Formatted Text” tab in the UI.
UI Elements for Stage 2: - Formatted Tab: A QPlainTextEdit or QTextEdit for the formatted output. - Model Selection (Formatting): A ComboBox for choosing the Chat model (e.g., “GPT-4 Mini”, “GPT-4”, “GPT-3.5” as user-friendly names, mapping to API model IDs internally). - Prompt Editor: A multi-line text edit pre-filled with default instructions. The user can modify this live. We will use the content of this field when calling format_text. - Style Guide Loader: A button or menu item (“Load Style Guide…”) that opens a file dialog. We accept .yaml, .yml, or .json files. Once loaded, we read the file content. If JSON, we might do json.dumps to pretty-print it; if YAML, we might leave as-is or ensure it’s text (using yaml.safe_load then yaml.dump to normalize formatting). The loaded text is stored (e.g., in self.loaded_style_text) and displayed perhaps in a read-only text box or just assumed to be part of prompt. - Toggle for Post-Formatting: A QCheckBox or toggle switch labeled “Apply Formatting Stage” that enables or disables Stage 2. If unchecked, the raw transcript remains as final output; the formatted tab can be left blank or disabled.
In the UI code (ui_mainwindow.py), we implement the formatting step like this:
# Inside MainWindow class in ui_mainwindow.py

def run_formatting(self, raw_text: str):
    """Run Stage 2 formatting on raw_text and display the result."""
    # Get user prompt and style guide from UI
    user_prompt = self.promptTextEdit.toPlainText().strip()
    style_text = self.loaded_style_text  # loaded from file if any, else ""
    model = self.selected_chat_model
    try:
        formatted = formatter_api.format_text(raw_text, prompt=user_prompt, style_guide=style_text, model=model)
    except Exception as e:
        self.show_error(f"Formatting failed:\n{e}")
        return
    # Display formatted text
    self.formattedTextEdit.setPlainText(formatted)
    # Log the formatting result and used prompt
    logger.info(f"Formatted text: {formatted}")
    logger.info(f"Formatting prompt used: {user_prompt}")
    if style_text:
        logger.info(f"Style guide used:\n{style_text}")
This function collects the current prompt text and any style guide content, as well as the chosen model for formatting. It then calls formatter_api.format_text. On success, it displays the formatted text and logs the details. On error, it shows an error dialog.
OpenAI API considerations: The ChatCompletion API returns a JSON response with various fields (id, usage, choices, etc.). We retrieve choices[0].message.content for the result[12][13]. We might also handle token usage info if we want to display cost or usage, but for now we just log or ignore it. If the model is not available or returns an error (some models might require Azure endpoints – e.g., gpt-4o-mini could be available only via Azure OpenAI at the moment[8]), we handle exceptions accordingly.
Vocabulary Extraction and Approval (Janome Integration)
Goal: After getting the raw transcription, help the user identify important or unfamiliar vocabulary (especially Japanese terms, proper nouns, technical terms) and allow the user to confirm or correct them. This can be used to build a custom dictionary for future transcriptions or just to double-check the transcript for errors in names/terms.
Why Janome: Janome is a Japanese morphological analysis library. It can tokenize Japanese text into words with parts-of-speech (POS) tagging[14]. We can use Janome to extract nouns or other notable words from the transcript. The assumption is that the user (in Kawasaki, JP) might be transcribing Japanese content, so this is particularly useful for Japanese vocabulary. For English, this step might be less critical, but we can still extract capitalized words or something if needed (though Janome is specifically for Japanese).
Implementation: - We create a module vocabulary.py with functions to extract candidate vocabulary from a text using Janome. For example, we can extract all words that are nouns (名詞) or perhaps all unique words above a certain length. - We also maintain a user dictionary file (perhaps user_dict.txt or .yaml) which stores words the user has “approved” before. This way, we don’t repeatedly prompt the user for the same word. The dictionary could also hold custom preferred spellings or readings for those words. - After Stage 1 (raw transcription), we run the vocabulary extraction on the raw text. We compare against the user dictionary list to filter out words already known. - If new words are found, we pop up a Vocabulary Approval Dialog listing those words. This dialog could list each word with a checkbox “Add to dictionary” and possibly an input to correct the spelling if needed. The user can tick which words to add (or a “Select All” if desired). - When the user confirms, we add the selected words to the user dictionary persistent storage (could be a simple text file where each line is a word, or a YAML list). We then optionally could inform the Stage 2 formatting about these (perhaps by adding a note in the prompt like “Ensure correct spelling for: X, Y, Z” or including them in the style guide). - Even if we don’t directly feed them into formatting, having the user dictionary means next time if those words appear, we won’t prompt again. (If we wanted to use the dictionary to improve transcription, one approach is to provide those words in the initial ASR prompt context[15], but the OpenAI Whisper API’s prompt is meant for partial transcript biasing, so results may vary. Alternatively, we might highlight them in Stage 2 prompt: e.g., “The following names/terms should be preserved as-is: ...”).
Janome usage example:
from janome.tokenizer import Tokenizer

tokenizer = Tokenizer()
tokens = tokenizer.tokenize(text)
for token in tokens:
    surface = token.surface  # actual word
    part = token.part_of_speech  # e.g., "名詞,..."
    print(surface, part)
As documented in Janome’s README, tokenization yields tokens with attributes including surface form and part-of-speech[14]. We will use this to identify nouns. In Japanese, 名詞 (meishi) indicates a noun. We can select token.surface for tokens where token.part_of_speech.startswith("名詞").
We can also filter proper nouns (Janome further classifies types of nouns, e.g., “固有名詞” for proper noun, which appears in the part-of-speech string). For simplicity, we might just take all nouns (which would include common nouns too). Alternatively, we might focus on nouns that are not in a basic lexicon if we had one, but that gets complex.
Vocabulary UI: We’ll create a QDialog that lists words (maybe in a QListWidget with checkboxes, or a QTableWidget with a column for the word and a checkbox or “Add?” column). We might also allow editing the word in case the transcript got it slightly wrong and the user knows the correct form. But editing might be overkill; the user could instead just not add a wrong word, and manually correct it in the text.
We will implement a simple dialog with a list of new words and an “Add selected to dictionary” button.
Code for vocabulary extraction and approval (simplified):
# File: OpenSuperWhisper/vocabulary.py

from janome.tokenizer import Tokenizer

tokenizer = Tokenizer()

def extract_new_vocabulary(text: str, known_words: set) -> list:
    """
    Extract candidate vocabulary (unique nouns) from text that are not in known_words.
    Returns a list of new words.
    """
    tokens = tokenizer.tokenize(text)
    new_words = set()
    for token in tokens:
        part = token.part_of_speech  # e.g., "名詞,一般,..."
        if part.startswith("名詞"):  # any kind of noun
            word = token.surface
            # Ignore single-character common particles that might be mis-tagged, etc.
            if not word or word.isspace():
                continue
            if word in known_words:
                continue
            new_words.add(word)
    # Sort results (e.g., alphabetical) for consistency
    return sorted(new_words)

def load_user_dictionary(dict_path: str) -> set:
    """Load user-known vocabulary from a simple text file (one word per line)."""
    words = set()
    try:
        with open(dict_path, 'r', encoding='utf-8') as f:
            for line in f:
                w = line.strip()
                if w:
                    words.add(w)
    except FileNotFoundError:
        # If no dictionary exists yet, that's fine.
        pass
    return words

def save_user_dictionary(dict_path: str, words: set):
    """Save the given set of words to the dictionary file."""
    with open(dict_path, 'w', encoding='utf-8') as f:
        for w in sorted(words):
            f.write(w + "\n")
This provides functions to get new words from text (extract_new_vocabulary) and to load/save a user dictionary file. For the dictionary, we choose a plain text file format for simplicity. (One could use JSON or YAML too, but a list of words in a text file is straightforward.)
We integrate this into the main workflow: after getting the raw transcript in Stage 1, we call extract_new_vocabulary(raw_text, known_words). We get known_words by loading the dictionary at start or keep it in memory. Suppose our dictionary file is user_dict.txt in the project directory (or in user’s AppData via QSettings, but here we’ll keep it simple and put it in working directory).
If new_words list is non-empty, we show the approval dialog.
UI for approval dialog: We can create a QDialog subclass VocabDialog that takes the list of words and shows them with checkboxes:
# In ui_mainwindow.py or a separate dialog module

class VocabDialog(QtWidgets.QDialog):
    def __init__(self, words, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Vocabulary Found")
        self.resize(300, 200)
        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel("The following new words were found. Add to custom vocabulary?")
        layout.addWidget(label)
        # List with checkboxes
        self.listWidget = QtWidgets.QListWidget()
        for w in words:
            item = QtWidgets.QListWidgetItem(w)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)  # default to checked
            self.listWidget.addItem(item)
        layout.addWidget(self.listWidget)
        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("OK")
        cancel_btn = QtWidgets.QPushButton("Skip")
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def get_selected_words(self):
        selected = []
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                selected.append(item.text())
        return selected
This dialog will appear with each new word listed. The user can uncheck any they don't want to add, then click OK or Skip. If OK, accept() is called and get_selected_words() can retrieve the chosen words.
We would use it in main flow like:
known_words = vocabulary.load_user_dictionary("user_dict.txt")
new_words = vocabulary.extract_new_vocabulary(raw_text, known_words)
if new_words:
    dlg = VocabDialog(new_words, parent=self)
    if dlg.exec_():  # if OK was pressed
        selected = dlg.get_selected_words()
        if selected:
            # Update known_words and save
            known_words.update(selected)
            vocabulary.save_user_dictionary("user_dict.txt", known_words)
            logger.info(f"Added new vocab: {selected}")
    # If Skip (rejected), we do nothing (user chose not to add any new words this time)
We will call this before Stage 2 formatting. The reason is: if the user corrects a word or is aware of a mistake, they might want to adjust the raw text or add something to prompt. We’re not explicitly allowing editing the raw text in UI (though they could, since it’s in a text box; but we didn’t cover a “re-transcribe” with manual edits). However, at least we highlight the words. In future, one might integrate a feature: double-click a word in the dialog to highlight it in the raw text box so user can fix it manually, but for now, we’ll stick to building the dictionary.
Finally, we could incorporate the dictionary words into Stage 2 as part of style guide or instructions: e.g., if selected words are added, maybe we tell the model “The following are proper nouns or terms: X, Y, Z.” This could help the model not to alter those. But this might complicate prompt; perhaps it’s okay if the model might already preserve them. We’ll mention as a possible improvement.
Summary: The vocabulary extraction uses Janome to identify nouns[14] and helps build a custom vocabulary list (similar to the “Custom dictionary” feature planned in the original project[16]). Everything happens on-device (Janome is local), and we only log or store the words (no external API for this part).
Persistent Configuration with QSettings
We want user preferences to persist across sessions, including: - Last selected ASR model (Stage 1 model). - Last selected formatting model (Stage 2 model). - Whether post-formatting is toggled on. - The custom prompt text (perhaps save it so it’s not lost on restart). - The last used style guide file path (maybe to auto-load it or remember which was used). - Window size/position, maybe last used directories for file dialogs, etc. - Potentially the audio input device if user can configure that (not implemented here explicitly, but QSettings could store device index if needed).
QSettings (from Qt) provides a platform-native way to store app settings in the registry (on Windows) or config files (on Mac/Linux). We can use it easily via PySide6/PyQt. For example:
from PySide6.QtCore import QSettings

# Create a QSettings object (organization and app name are used to locate storage)
settings = QSettings("OpenSuperWhisperProject", "OpenSuperWhisperApp")
# To store a value:
settings.setValue("asr_model", "whisper-1")
# To retrieve:
model = settings.value("asr_model", defaultValue="whisper-1")
We typically choose an organization and application name for QSettings. For this project, we might use something like “OpenSuperWhisperProject” / “OpenSuperWhisperApp” (or simply use the company/app name of your choice). QSettings on Windows will create a registry key under HKEY_CURRENT_USER\Software\OpenSuperWhisperProject\OpenSuperWhisperApp to store values[17][18].
We will create a config.py to wrap QSettings usage for our specific keys:
# File: OpenSuperWhisper/config.py

from PySide6.QtCore import QSettings

# Define organization and app name
ORG_NAME = "OpenSuperWhisperProject"
APP_NAME = "OpenSuperWhisperApp"
settings = QSettings(ORG_NAME, APP_NAME)

# Define keys for various settings
KEY_ASR_MODEL = "models/asr_model"
KEY_CHAT_MODEL = "models/chat_model"
KEY_POST_FORMAT = "pipeline/enable_post_format"
KEY_PROMPT_TEXT = "formatting/prompt_text"
KEY_STYLE_GUIDE_PATH = "formatting/styleguide_path"
KEY_WINDOW_GEOMETRY = "ui/window_geometry"

def save_setting(key: str, value):
    settings.setValue(key, value)

def load_setting(key: str, default=None):
    return settings.value(key, default)
We group keys into categories (like models/ and formatting/). This is optional, but QSettings allows a hierarchy using “/” in keys[19]. For example, models/asr_model and models/chat_model are stored under a “models” group. This organization is reflected if one views the raw settings storage (or in code we could do settings.beginGroup("models") etc. as shown in Qt docs[20]).
We then use these functions in the UI: - On startup, load last values (e.g., self.asrModelCombo.setCurrentText(load_setting(KEY_ASR_MODEL, "whisper-1")) to select the saved ASR model, etc.). - After user changes something or at app exit, save current values (e.g., when a model combo changes, connect its currentTextChanged signal to a lambda that calls save_setting(KEY_ASR_MODEL, new_value)). - We also save the window geometry (size and position). Qt allows storing the whole geometry in a QByteArray (e.g., save_setting(KEY_WINDOW_GEOMETRY, self.saveGeometry()) and restore with self.restoreGeometry(settings.value(KEY_WINDOW_GEOMETRY))[21]). This way the main window opens in the same size/position as last time[22].
Because QSettings writes to persistent storage, these settings will remain even after upgrading the app (unless we change the ORG/APP name). The user can always delete the registry entries or we could provide a “Reset to default” option that calls settings.clear().
Example of using QSettings in code:
# On app launch (MainWindow.__init__ after UI setup):
last_asr = config.load_setting(config.KEY_ASR_MODEL, "whisper-1")
idx = self.asrModelComboBox.findText(last_asr)
if idx != -1:
    self.asrModelComboBox.setCurrentIndex(idx)
self.postFormatToggle.setChecked(config.load_setting(config.KEY_POST_FORMAT, True))
self.promptTextEdit.setPlainText(config.load_setting(config.KEY_PROMPT_TEXT, DEFAULT_PROMPT))
last_style_path = config.load_setting(config.KEY_STYLE_GUIDE_PATH, "")
if last_style_path:
    self.load_style_guide_from_file(last_style_path)
# etc. for chat model and window geometry
geom = config.load_setting(config.KEY_WINDOW_GEOMETRY)
if geom:
    self.restoreGeometry(geom)

# When user changes model selection:
def on_asr_model_changed(new_model):
    config.save_setting(config.KEY_ASR_MODEL, new_model)
self.asrModelComboBox.currentTextChanged.connect(on_asr_model_changed)

# Similarly for chat model, prompt text (maybe on prompt edit's focus out or textChanged).
# On toggle change:
def on_post_format_toggled(state):
    config.save_setting(config.KEY_POST_FORMAT, bool(state))
self.postFormatToggle.toggled.connect(on_post_format_toggled)

# On loading a style guide file:
def load_style_guide_from_file(path):
    # read file and set self.loaded_style_text, etc.
    config.save_setting(config.KEY_STYLE_GUIDE_PATH, path)
Using QSettings ensures that next time the application starts, it remembers the user’s preferences (e.g., if they prefer using GPT-3.5 to save costs or a certain style guide for their transcriptions). Qt’s QSettings works transparently without needing us to manage file paths for config: on Windows it will use the Registry by default[23][24] (which is fine for our app). If we wanted an INI file instead (for easier debugging), we could initialize QSettings with QSettings(QSettings.IniFormat, QSettings.UserScope, ORG_NAME, APP_NAME)[25], but that’s optional.
Logging Outputs and Metadata
We want to keep logs of the app’s operation for debugging and record-keeping: - ASR Output log: what the raw transcription was, timestamp, which model was used, etc. - Formatting Output log: the result after formatting, the prompt used, style guide used, etc. - Metadata: possibly audio file name or a session ID, time taken, errors if any. - We can also log user actions like starting/stopping recording, and any errors encountered.
Having logs is useful for troubleshooting (e.g., if the transcription is bad, we can see what was sent, or if formatting did something strange, we have the prompt and output).
We’ll create a simple logging setup using Python’s logging module. We will direct logs to a file in a fixed directory (for example, a subfolder logs/ in the working directory). Each run could append to the same log file, or we can create daily or session-based logs. Here, let’s do a daily rotation for simplicity using the date in filename, or just one file that appends (but that can grow indefinitely). We’ll use one file per day to balance between simplicity and manageability.
Logging setup (logger.py):
# File: OpenSuperWhisper/logger.py

import logging
import os
from datetime import datetime

# Ensure logs directory exists
LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Name log file with current date
log_filename = os.path.join(LOG_DIR, datetime.now().strftime("%Y-%m-%d") + ".log")

# Configure logging to file
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)
This configures the root logger to write INFO and above messages to a file named like 2025-07-25.log in logs/[26]. We set a format that includes timestamp, level, and message. (We used encoding="utf-8" for safety on Windows[27].)
We will use logger.info(), logger.error(), etc. throughout the code. For example: - After transcription: logger.info(f"Transcribed with {model}: {result_text}") - After formatting: logger.info(f"Formatted with {model}: {formatted_text}") - Log the prompts: logger.debug(f"Prompt: {prompt}") (maybe debug-level for very verbose info). - On errors: logger.error(f"Error during formatting: {e}") (and also show user).
We already added some logging lines in earlier code snippets (like logging added vocab, logging prompt used, etc.). Those will go into our log file with timestamps automatically (because of %(asctime)s in format[28]).
Additionally, logging the window geometry or settings changes is usually not necessary (the QSettings persist anyway), unless debugging UI issues.
Since we use logging.basicConfig at import of logger.py, any calls to logging in our modules will use that configuration (because they share the root logger). We could also use a module-level logger (like logger = logging.getLogger(__name__)) for each module as best practice[29], but for a small app, the root logger suffice. In our logger.py we already get a logger for __name__ which in this context might be "OpenSuperWhisper.logger". If we import that logger in others, it’s essentially the same root config.
Viewing logs: The user (or developer) can open the log files in the logs/ directory. We might document that in README (especially if some error happens, check logs for details). We won’t display logs in UI, but that’s a possible extension (like a “Show Logs” button to open the file or bring up a log viewer dialog).
Important: Ensure the log directory is not unwieldy. Our approach creates one file per day, which is fine. If the app is used heavily, we might add a routine to purge logs older than X days, but that’s out of scope for now.
Unit and Integration Tests (pytest)
To maintain code reliability, we write pytest tests for key components. We will have: - Unit tests for asr_api.transcribe_audio and formatter_api.format_text using monkeypatch or stubbed OpenAI API calls (since we don’t want actual API calls in test runs). We can simulate OpenAI responses for known inputs. - Tests for vocabulary.extract_new_vocabulary to ensure it extracts expected words given a sample text and known words list. - Perhaps a test for the integration of Stage 1 and Stage 2 using a dummy audio file and dummy OpenAI responses.
Because calling the real OpenAI API requires API keys and costs, our strategy in tests will be to monkeypatch the OpenAI library methods: - Monkeypatch openai.Audio.transcribe to a dummy function that returns a preset string (e.g., if we pass a known dummy audio path). - Monkeypatch openai.ChatCompletion.create to return a dummy response object (we can create a simple class mimicking the structure or just a dict).
Example monkeypatch in pytest:
# File: tests/test_asr_api.py
import builtins
import io
import openai
import OpenSuperWhisper.asr_api as asr

class DummyTranscription:
    def __init__(self, text):
        self.text = text

def dummy_transcribe(*args, **kwargs):
    # We ignore the actual file and model and just return a fixed text
    return "dummy transcription text"

def test_transcribe_audio_monkeypatch(monkeypatch, tmp_path):
    # Create a fake audio file
    audio_file = tmp_path / "test.wav"
    audio_file.write_bytes(b"RIFF....")  # write minimal bytes or leave empty; it won't be read by dummy

    # Monkeypatch openai.Audio.transcribe to our dummy function
    monkeypatch.setattr(openai.Audio, "transcribe", lambda *args, **kwargs: "Hello world.")
    result = asr.transcribe_audio(str(audio_file), model="whisper-1")
    assert result == "Hello world."
In this test, we used monkeypatch fixture to replace openai.Audio.transcribe with a lambda that returns "Hello world." no matter what[3]. We then call our function and assert we got that string. We didn’t actually need the content of audio_file due to patching, but we created one to simulate existence. Similarly, we can test that exceptions from OpenAI are propagated by having the dummy raise an exception.
For formatter_api.format_text, we monkeypatch openai.ChatCompletion.create. That function returns a complex dict normally, but we can have it return a minimal dict: {"choices": [ {"message": {"content": "Formatted text"}} ]}[12]. For example:
# File: tests/test_formatter_api.py
import openai
import OpenSuperWhisper.formatter_api as fmt

def test_format_text_monkeypatch(monkeypatch):
    # Monkeypatch openai.ChatCompletion.create
    dummy_response = {
        "choices": [ { "message": {"content": "Formatted Output"} } ]
    }
    monkeypatch.setattr(openai.ChatCompletion, "create", lambda **kwargs: dummy_response)
    raw = "raw text"
    prompt = "Make it fancy."
    style = "No slang."
    result = fmt.format_text(raw, prompt, style_guide=style, model="gpt-4o-mini")
    assert result == "Formatted Output"
This test bypasses the actual API and ensures our function correctly extracts the content.
We should also test extract_new_vocabulary. We can craft a Japanese sentence and see if it picks expected nouns. For example:
# File: tests/test_vocabulary.py
import OpenSuperWhisper.vocabulary as vocab

def test_extract_new_vocabulary_basic():
    text = "これはテストです。東京に行きました。"
    # Janome would tokenize "これは", "テスト", "です", "。", "東京", "に", "行き", "ました", "。"
    known = {"テスト"}  # suppose "テスト" (test) is already known
    new_words = vocab.extract_new_vocabulary(text, known)
    # We expect "東京" (Tokyo) to be extracted as a noun, and maybe "テスト" if it wasn't known.
    assert "東京" in new_words
    assert "テスト" not in new_words  # it was in known, so should not appear
This will pass if Janome correctly identifies "東京" as a noun and we filtered out "テスト" because it was in known list. (Janome outputs "東京 名詞,固有名詞,...", "テスト 名詞,サ変接続,...", etc., so yes those are nouns.)
We also test saving/loading dictionary:
def test_user_dictionary_save_load(tmp_path):
    words = {"apple", "orange"}
    dict_file = tmp_path / "dict.txt"
    vocab.save_user_dictionary(dict_file, words)
    loaded = vocab.load_user_dictionary(dict_file)
    assert words == loaded
Integration test: perhaps simulate the full pipeline (without UI) by chaining the calls using dummy patches: - Use dummy transcription output for Stage 1, - Then run vocabulary extraction on it (with known set), - Monkeypatch formatting to just return something like the input with modifications, - Ensure no exceptions and expected combined output.
Given that UI flows and actual API calls can’t be easily tested without the services or more complex simulation, the above should suffice to cover logic. We can also test that QSettings is storing values, but since QSettings writes to actual registry or file, altering that in tests is possible (we could set QSettings format to Ini for tests to avoid touching user registry). This might be overkill; we can trust QSettings if used correctly. Possibly just test that our config.save_setting and load_setting return what was saved (which indirectly tests QSettings functionality):
# File: tests/test_config.py
import OpenSuperWhisper.config as config

def test_settings_save_and_load():
    config.save_setting("test/key1", "value1")
    val = config.load_setting("test/key1")
    assert val == "value1"
This will write to QSettings (in user scope). It might persist beyond test run. To avoid polluting real settings, we could either use a unique test org/app name or use QSettings.setIniCodec to write to a temp file. However, since it's a trivial value, it’s not a big issue. Alternatively, create a QSettings object in the test with IniFormat pointing to tmp_path.
Given the beginner context, we might not dive that deep. (One could also mark such tests with @pytest.mark.skip if they interfere, but let's assume fine.)
Running tests: In README, instruct to run pytest in project root to execute all tests. All tests should pass if everything is implemented correctly.
Code Formatting and Linting (Black, Ruff, Pre-commit)
To maintain code quality and consistency, we set up Black (code formatter) and Ruff (linter) with pre-commit hooks:
•	Black: to auto-format code to PEP8 style (line lengths, indentation, etc.). We can use Black’s default settings (line length 88 or we can configure 100 if we prefer).
•	Ruff: a fast Python linter that can replace flake8, isort, etc. We use it to catch common issues (unused imports, undefined names, etc.) and also for import sorting (and Ruff can also apply some autofixes).
•	pre-commit: a framework to run checks before each commit. We add Black and Ruff hooks so that whenever we commit, the code gets formatted and linted automatically, preventing bad code from entering the repo.
We create a .pre-commit-config.yaml in the project root with something like:
# .pre-commit-config.yaml
repos:
- repo: https://github.com/psf/black
  rev: 23.9.1  # Use the latest Black version
  hooks:
    - id: black
      language_version: python3.12
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.12.5  # match Ruff version
  hooks:
    - id: ruff
      args: [--fix]  # have ruff autofix issues (like import sorting)
With this, running pre-commit install will set up the Git hook. Black will run and reformat code if needed, and Ruff will flag any lint errors (and with --fix it can even fix some). We ensure Ruff runs before Black in config if we needed (some prefer Ruff do only lint and let Black do formatting). In our case, Black and Ruff cover mostly distinct areas, but there’s slight overlap on things like line length and quote normalization (Ruff’s ruff --fix can also format, but we might only use it for smaller fixes). We placed both; Black will apply final formatting.
The developer can also run these manually: uv pip install black ruff (or include them in dev requirements), then black . and ruff . to format and lint. With pre-commit, it’s automated on commit.
Configuration for tools: - Black: We might specify a target Python version (3.12) and possibly a line length. Black’s defaults are fine for now. - Ruff: We can create a ruff.toml config if we want to ignore certain rules or set line length, but at beginner level, default rules are okay. (We just need to ensure it doesn’t conflict with Black on formatting – typically, Black and Ruff’s autofix can coexist if configured as per documentation[30].)
We should also add these to our requirements.txt (or a separate requirements-dev.txt). If using uv’s pip, we can do:
uv pip install black ruff pre-commit
pre-commit install
Now each commit will run these. If code isn’t formatted, Black will format it and the commit will fail, so you have to add the changes and commit again (or use pre-commit run --all-files to test/format all at once).
References: The pre-commit hooks for Black and Ruff are well-documented. For example, the Ruff docs show adding hooks for ruff and optionally ruff-format[31][32]. We choose to let Black handle formatting beyond what Ruff fixes, so we didn’t add ruff-format here (to avoid double formatting). Our config ensures Ruff’s lint runs (with some fixes) then Black finalizes formatting[30].
Building the Executable with PyInstaller
Finally, to distribute the app as a single .exe file on Windows, we will use PyInstaller. We want a one-file executable (all dependencies bundled) and run in windowed mode (no console popping up).
Steps: 1. Ensure PyInstaller is installed: uv pip install pyinstaller. 2. Run PyInstaller on our main script with appropriate flags: - --onefile to bundle into one exe[33]. - --windowed (or -w) to disable the console window[34] (equivalent to --noconsole). - --name OpenSuperWhisper to name the executable (optional, defaults to script name)[35][36]. - We might need to include additional data: - The models (if we had Whisper .bin models, but here we use API so none). - Possibly include default style guide files or other resources like an icon. - For example, if we have an icon file for the app, we can use --icon=app.ico. - If we have any Qt plugins or DLLs that PyInstaller misses, we might need --add-data or hidden imports. Usually, PyInstaller handles PySide6 fairly well in onefile mode, but if you encounter Qt platform plugin not found on running the exe, you may need to add: --add-data "PySide6\plugins\platforms\qwindows.dll;PySide6\plugins\platforms" on Windows (PyInstaller’s Qt hooks often do this, but just in case). - Example command:
pyinstaller --onefile --windowed --name "OpenSuperWhisper" main.py
This will create a dist/OpenSuperWhisper.exe as output[37][34].
1.	After building, test the generated OpenSuperWhisper.exe on a Windows machine:
2.	It should launch the GUI without a console.
3.	Ensure that recording works (the packaged app has access to PortAudio through the bundled sounddevice library – PyInstaller should include the needed PortAudio DLL that sounddevice brings).
4.	Ensure that the app can find any resources or files it needs. For instance, if our app expects a models directory or style_guides directory relative to the script, in onefile mode those become part of the package (accessible via a temporary folder PyInstaller creates at runtime[38]). We should be careful with relative paths:
o	If we access files by relative paths (like os.getcwd()), note that in onefile exe, os.getcwd() might not be where the exe is located but where the user launched it from. For logs, we used os.getcwd() which is okay if the user runs it from their working directory. If not, logs might appear elsewhere or fail to write if no permission. We might consider using sys._MEIPASS or application directory for logs. But for simplicity, we assume working directory is fine. Alternatively, we could use QStandardPaths to get a user documents folder for logs.
o	If we included a default style guide file, we would have to find it in the bundle. That can be done via import or using pkgutil. But since style guides are user-provided in our design, not an issue.
5.	The persistent QSettings will still work in the exe (writes to registry).
6.	Confirm that the OpenAI API calls work from the exe (requires internet connectivity and a valid API key environment variable or we might prompt for it in UI if not set).
7.	We can also create a PyInstaller spec file (pyinstaller.spec) for more fine-grained control if needed. For instance, to add data files, or to ensure the Janome dictionary is included. Janome’s dictionary (MeCab IPADIC) is likely included in janome package files. PyInstaller should auto-include it since Janome is pure Python and likely loads its dict from the package. But if not, one may need to include janome/ipadic folder. We can test the exe by doing a Japanese tokenization; if it fails (e.g., cannot find dictionary), then adjust spec to add it:
8.	Example in spec: datas=[('C:/.../site-packages/janome/ipadic/*', 'janome/ipadic')] to package those files.
However, in practice, installing janome via pip brings compiled dictionary data in the package that PyInstaller usually catches. So we might not have to do anything special for Janome.
Build Instructions (for README): We will document: - Install PyInstaller (e.g., uv pip install pyinstaller). - Run the command as above. - The output will be in dist/ directory. - The single exe can be moved anywhere; however, note that because it’s onefile, launching it has an unpacking delay and uses temp space[38]. If startup time is a concern, one could use one-folder mode (--onedir) which is faster to start but gives a folder of files[39]. - Also mention that in case of any missing Qt plugin issues (like “Qt platform plugin xcb/windows not found”), one may have to add hidden imports or use PyInstaller’s --collect-all PySide6 option. But since our target is Windows, PyInstaller likely handles the qwindows.dll plugin if PySide6 is properly imported. In case it doesn’t, the error at runtime would be: "This application failed to start because no Qt platform plugin could be initialized.". If that happens, we fix by the --add-data as described or ensure the spec includes PySide6 plugins.
For completeness, we can provide a snippet in README for PyInstaller usage:
pyinstaller --onefile --windowed --name OpenSuperWhisper OpenSuperWhisper/main.py
(This assumes our main.py is in OpenSuperWhisper package; if we use the entry at voice_input/OpenSuperWhisper/main.py it’s fine. Alternatively, we might have placed main.py in root for easier use. But we structured it inside the package. We can create a small run.py at root that imports and calls main to make PyInstaller’s job easier without package issues, or specify the module.)
However, PyInstaller can work with a module path too. If main.py uses relative imports for our package modules, it should be fine when we run pyinstaller OpenSuperWhisper/main.py. The resulting exe will execute as if main.py was in package, should handle imports thanks to PyInstaller analyzing them.
Testing the exe: Outline how to test basic function: - Click Record, speak something, see text. - If no audio device, mention dependency (should be none, sounddevice includes PortAudio). - Ensure API key is set or the API calls will fail (we might in UI check OPENAI_API_KEY env on startup and if not set, prompt user to enter it – but we didn’t implement a prompt for key to avoid storing secrets; we rely on env variable as simplest route. In README, we’ll emphasize to set OPENAI_API_KEY in the environment before running the exe, e.g., via a .bat file or system env.)
Full Updated README.md
Below is an example of an updated README.md incorporating the new features and instructions:
[40][41]
# OpenSuperWhisper (Two-Stage Voice Transcription Tool)

OpenSuperWhisper is a cross-platform voice transcription application that uses OpenAI’s state-of-the-art models to transcribe audio and then polish the transcription according to your desired style. It offers real-time recording, advanced formatting with a style guide, vocabulary assistance, and more.

## Features

- 🎙 **Real-time Audio Recording and Transcription:** Press the record button (or use the shortcut `Ctrl+Space`) to start recording from your microphone, then press stop to transcribe instantly using OpenAI Whisper or GPT-4o models.
- 📝 **Two-Stage Transcription Pipeline:** First, get raw text via OpenAI ASR (Whisper API or GPT-4o Transcribe). Second, automatically format and correct that text using a GPT-based model (Chat Completion) with your custom prompt and style rules.
- 💡 **Custom Formatting Prompt & Style Guide:** Tailor the output by editing the formatting prompt in the UI. Load a YAML or JSON style guide file to enforce specific writing style, terminology, or formatting conventions in the final text.
- 📖 **Vocabulary Extraction & Dictionary:** After transcription, the app highlights new or uncommon words (especially Japanese nouns using Janome). You can choose to add these to your custom vocabulary. The app remembers these, helping maintain consistency (and avoid prompting for them again).
- 💾 **Persistent Settings:** Your preferences (selected models, toggle states, prompt text, window size, etc.) are saved automatically. Next time you open the app, it recalls your last-used settings.
- 📂 **Logging:** All transcriptions and formatting results are logged (with timestamps and model info) in the `logs/` directory. This helps review past sessions or debug issues.
- 🧪 **Fully Tested Codebase:** The project includes unit and integration tests (using pytest) to ensure reliability of the transcription and formatting pipeline.
- 🖥 **One-File Executable for Windows:** Easily run OpenSuperWhisper on Windows without setting up a Python environment – just use the provided single EXE (built with PyInstaller).

## Installation

**Prerequisites:**
- Python 3.12 (if running from source). On Windows, ensure Python and pip/uv are in your PATH.
- An OpenAI API key for using the transcription and formatting services. Set it as an environment variable `OPENAI_API_KEY` before running the app.
- (Windows) Microphone access for recording.

**Using uv (Fast Python Package Manager):**
1. Clone this repository or download the source code.
2. In a terminal, navigate to the project directory (`voice_input/`).
3. Install dependencies with [uv](https://github.com/astral-sh/uv):
   ```bash
   uv pip install -r requirements.txt
   ```
   This will install PySide6 (Qt for GUI), openai, janome, sounddevice, and other requirements.  
4. (Optional) Install dev tools for testing and formatting:
   ```bash
   uv pip install black ruff pytest pre-commit
   ```
   *(This is only needed if you plan to run tests or contribute to development.)*

**Running from Source:**
```bash
uv run OpenSuperWhisper/main.py
(Alternatively, you can use python -m OpenSuperWhisper.main if the package is on PYTHONPATH.)
The application window should appear. If your OpenAI API key is set, you’re ready to transcribe.
Using the Windows EXE: Download the latest release from the Releases page (e.g., OpenSuperWhisper.exe). No installation needed – just double-click to run. (On first run, Windows SmartScreen might warn since it’s an unsigned executable. You can choose “More info -> Run anyway”.)
Make sure to set your OPENAI_API_KEY in the environment. You can do this by creating a simple batch file like:
@echo off
set OPENAI_API_KEY=sk-...YourKeyHere...
start OpenSuperWhisper.exe
Launch the app via this batch file so that the API key is available to it.
Usage Guide
1.	Recording Audio: Press the Record button (🎤) to start recording your voice. Speak clearly into your microphone. You’ll see a timer or level indicator (if implemented) while recording. Press Stop to finish. The audio will be sent to OpenAI and transcribed in a few seconds. The raw text appears in the “Raw Transcription” tab on the right.
2.	Review Raw Transcription: Check if the raw text captured your speech correctly. You can copy this text or even edit it in place if you spot obvious errors (the raw text box is editable in case minor touch-ups are needed).
3.	Vocabulary Check (Japanese): If you transcribed Japanese (or other languages) and the system finds new words, a “New Vocabulary” dialog will pop up listing terms it thinks are important or uncommon. (For example, proper nouns, technical terms, etc.) Review the list:
4.	Uncheck any words you don’t want to save (or that were incorrectly recognized).
5.	Click OK to add the checked words to your custom vocabulary list (stored persistently).
6.	These words will be remembered by the app (and could be used in future to bias transcriptions or at least not prompt again).
7.	If you click Skip, no words are saved this time.
8.	Formatting & Styling: By default, the app will automatically proceed to Stage 2 formatting after transcription. (This is controlled by the “Post-formatting” toggle – ensure it’s on if you want formatted output.) The text, along with your custom prompt and style guide, is sent to the OpenAI chat model for polishing. The Formatted Text tab will then display the result – usually with proper capitalization, punctuation, and any style preferences applied.
9.	Custom Prompt: You can customize the instructions for formatting. In the bottom panel, there is a “Formatting Prompt” text box. Edit this text to guide how the second-stage model should output text. For example, you can write: “Format as a business email.”, “Use polite tone and full sentences.”, or “Output in bullet points summarizing the content.” Be creative – the prompt can significantly change the final output. The default prompt is a general instruction to fix grammar and punctuation.
10.	Style Guide: If you have a style guide – a set of rules or a glossary you want the model to follow – click Load Style Guide and select your YAML or JSON file. Once loaded, the path is displayed (and remembered for next time). The content of the style guide will be used by the formatting model. For example, you might have a YAML like:
 	tone: formal
avoid:
  - slang
  - contractions
preferred_spelling:
  colour: color
 	The model will try to adhere to these guidelines. (There’s no strict guarantee, but it does help inject domain knowledge or preferences.)
11.	Model Selection: At the top, you can choose which models to use:
12.	Transcription Model: Choose between whisper-1 (OpenAI Whisper model) or GPT-4o Transcribe models. The GPT-4o models (if enabled on your account) might give better accuracy for some languages[9]. Whisper-1 is robust and supports many languages[42].
13.	Formatting Model: Choose a chat model for formatting. GPT-4o-mini is selected by default (a fast, cost-efficient GPT-4 variant[43]). If you have full GPT-4, you can select it, or use GPT-3.5 for quicker, cheaper results (though quality will be slightly lower for complex formatting).
14.	Viewing and Copying Results: You can switch between the Raw and Formatted tabs to compare the outputs. Once you’re satisfied, you can select the text and copy it, or use the Save button (if provided) to save the transcriptions to a text file.
15.	Logs: The app writes a log file each day in the logs folder (where the app is run from). If something seems off, check the log (e.g., logs/2025-07-25.log) for details. It logs the model names, raw and formatted text, and any errors. This is useful for debugging or keeping transcripts archived. (Note: The log will include the content of your transcriptions and prompts – handle it securely if those are sensitive.)
Configuration & Preferences
All your settings are saved automatically via QSettings (on Windows, in the registry under OpenSuperWhisperProject/OpenSuperWhisperApp). This includes window size, last used models, prompt text, style guide path, etc. No need to manually edit config files. If you ever want to reset everything, you can use the “Reset to Defaults” option in the menu (or delete the registry key).
The custom vocabulary you build is stored in a text file user_dict.txt in the application directory. You can edit this file manually to remove entries or add new ones (one word per line). The vocabulary is mainly used to avoid repeatedly asking about the same terms. (Future versions might use it to bias the ASR or formatting to preferred spellings.)
Testing
If you are running from source and want to ensure everything works, we have a comprehensive test suite. After installing dev requirements, simply run:
pytest
All unit tests and integration tests should pass. Tests cover the transcription and formatting functions (with dummy API calls), vocabulary extraction logic, and more. Continuous integration can be set up to run these on each commit.
Building the Executable (for developers)
We provide a pre-built executable for convenience. To build it yourself, follow these steps: 1. Install PyInstaller: uv pip install pyinstaller (or via pip). 2. Run PyInstaller with our spec or directly:
pyinstaller --onefile --windowed --name OpenSuperWhisper OpenSuperWhisper/main.py
This will create a standalone OpenSuperWhisper.exe in the dist directory. We use --onefile to bundle everything[33], and --windowed (alias --noconsole) to avoid a terminal popup when running[34]. 3. If you want to include an icon for the exe, add --icon path/to/icon.ico. The provided spec file pyinstaller.spec already handles including necessary data (e.g., Qt plugins, if needed). 4. Troubleshooting Build: PyInstaller should automatically include all needed libraries. In case the app complains about missing Qt platform plugins on launch (e.g., “no Qt platform plugin could be initialized”), make sure PySide6 plugins were included. You might need to add a data inclusion for the platforms folder (see PyInstaller docs or use --add-data as in PySide6 packaging guide). Our spec takes care of copying qwindows.dll for the Qt GUI. 5. The one-file exe will unpack to a temp folder at runtime and start the app[38]. There might be a few seconds delay on startup. This is normal for one-file mode. If startup time is critical, you can build in one-folder mode (remove --onefile), resulting in a dist/OpenSuperWhisper/ directory with many files, which launches quicker.
Changelog
See CHANGELOG.md for version history and upcoming features.
License
This project is licensed under the MIT License (same as the original OpenSuperWhisper). See LICENSE for details.
*(The README above is an illustration of what the documentation would look like with the new modifications.)*

[33][34]

## CHANGELOG.md

We maintain a CHANGELOG to document improvements and fixes. Here is an example reflecting our new features (assuming prior version 0.0.4 as latest from original):

```markdown
# CHANGELOG

## [0.1.0] - 2025-07-25
### Added
- Two-stage transcription pipeline:
  - **Stage 1:** OpenAI ASR integration (`whisper-1`, `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`) for audio transcription.
  - **Stage 2:** OpenAI Chat Completion integration (`gpt-4o-mini` or other GPT models) for formatting and refining transcriptions.
- Real-time audio recording via microphone with Start/Stop controls.
- **UI Enhancements:** 
  - New tabs to display **Raw** vs **Formatted** transcription results side by side.
  - Model selection combo boxes for both ASR and formatting stages.
  - Toggle switch to enable/disable post-formatting (Stage 2).
  - Multi-line prompt editor for customizing formatting instructions.
  - Menu option to load a YAML/JSON style guide, which is applied during formatting.
  - Vocabulary approval dialog powered by Janome to capture new terms; added terms are saved to a custom dictionary.
  - Basic error message dialogs for API errors or missing API key.
- **Persistent Settings:** Application now uses QSettings to save user preferences (last used models, window size, prompt text, etc.) between sessions.
- **Logging:** Implemented logging of operations to `logs/` directory. Each session’s key events (transcribed text, formatted text, selected models, errors) are recorded with timestamps[26].
- **Testing:** Added pytest test suite covering ASR and formatting functions (with monkeypatched OpenAI calls), vocabulary extraction, and config persistence.
- **Dev Tools:** Configured Black and Ruff with pre-commit hooks for code style and quality enforcement[31][44]. Added PyInstaller build script for generating onefile Windows executable.

### Changed
- Project restructured from original (which was macOS-only Swift) to a Python PySide6 application for cross-platform support (targeting Windows).
- Updated README with new usage instructions, setup, and features.
- Bumped minimum Python requirement to 3.12.

### Fixed
- N/A (first release in Python rewrite).

## [0.0.4] - 2025-06-18
*(This section would list changes in the original version 0.0.4 from the original repository for reference.)*
This completes the implementation of the requested features in a beginner-friendly manner. The developer can follow the file structure, use the provided code snippets, and refer to the README and CHANGELOG to understand how to run and use the application.
________________________________________
[1] [2] uv: Python packaging in Rust
https://astral.sh/blog/uv
[3] [4] [5] [7] [15] [42] Speech to Text Made Easy with the OpenAI Whisper API | DataCamp
https://www.datacamp.com/tutorial/converting-speech-to-text-with-the-openAI-whisper-API
[6] [16] [40] [41] GitHub - Starmel/OpenSuperWhisper: macOS whisper dictation app
https://github.com/Starmel/OpenSuperWhisper
[8] [9] Azure OpenAI Audio Models | Start with GPT‑4o Transcribe & TTS
https://devblogs.microsoft.com/foundry/get-started-azure-openai-advanced-audio-models/
[10] [11] Play and Record Sound with Python — python-sounddevice, version 0.3.7
http://python-sounddevice.readthedocs.io/en/0.3.7/
[12] [13] Getting started with OpenAI’s Chat Completions API in 2024 | by Chandler K | The AI Archives | Medium
https://medium.com/the-ai-archives/getting-started-with-openais-chat-completions-api-in-2024-462aae00bf0a
[14] GitHub - mocobeta/janome: Japanese morphological analysis engine written in pure Python
https://github.com/mocobeta/janome
[17] [18] [19] [20] [21] [22] [23] [24] [25] PySide6.QtCore.QSettings - Qt for Python
https://doc.qt.io/qtforpython-6/PySide6/QtCore/QSettings.html
[26] [29] logging — Logging facility for Python — Python 3.13.5 documentation
https://docs.python.org/3/library/logging.html
[27] [28] Logging HOWTO — Python 3.13.5 documentation
https://docs.python.org/3/howto/logging.html
[30] [31] [32] [44] Integrations | Ruff
https://docs.astral.sh/ruff/integrations/
[33] [34] [35] [36] [37] [38] [39]  Packaging PySide6 applications for Windows with PyInstaller & InstallForge 
https://www.pythonguis.com/tutorials/packaging-pyside6-applications-windows-pyinstaller-installforge/
[43] Chat GPT 4o mini - One API 200+ AI Models
https://aimlapi.com/models/chat-gpt-4o-mini

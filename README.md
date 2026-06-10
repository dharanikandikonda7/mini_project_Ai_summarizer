# AI Text Summarization System using NLP and Transformer Models

## Overview

The **AI Text Summarization System** is an NLP-based web application that generates concise, meaningful, and context-preserving summaries from lengthy textual content. The system leverages the **BART Transformer Model** (`facebook/bart-large-cnn`) to perform **abstractive text summarization**, ensuring that the generated summary captures the core meaning of the original text rather than simply extracting sentences.

In addition to summarization, the application offers multilingual translation, text-to-speech conversion, keyword extraction, vocabulary simplification, spelling correction, and summary evaluation metrics to improve accessibility and user understanding.

---

## Features

* Abstractive text summarization using **BART (facebook/bart-large-cnn)**
* Supports:

  * Direct text input
  * File upload
  * URL-based content extraction
* Simplified summary generation using synonym replacement techniques
* Multilingual translation support
* Text-to-Speech (TTS) audio generation
* Keyword extraction with word meanings
* Spelling correction and text preprocessing
* Summary quality evaluation metrics
* Interactive and user-friendly Streamlit interface

---

## Tech Stack

### Frontend

* Streamlit

### Backend

* Python

### NLP & Machine Learning

* Transformers (Hugging Face)
* BART (`facebook/bart-large-cnn`)
* PyTorch
* NLTK
* spaCy

### Additional Libraries

* BeautifulSoup
* Deep Translator
* gTTS
* PySpellChecker
* Requests

---

## System Workflow

1. User enters text, uploads a file, or provides a URL.
2. Input text is extracted and preprocessed.
3. Large text is divided into manageable chunks.
4. The BART model generates a professional abstractive summary.
5. A simplified summary is generated using synonym replacement techniques.
6. Keywords and important vocabulary are extracted.
7. Users can translate summaries into multiple languages.
8. Text-to-Speech converts summaries into audio.
9. Evaluation metrics are calculated and displayed.

---

## Project Structure

```text
AI-Text-Summarizer/
│
├── app.py
├── app/
│   └── ui.py
│
├── utils/
│   ├── extractor.py
│   ├── nlp.py
│   ├── translator.py
│   └── audio.py
│
├── assets/
│   └── logo.png
│
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/AI-Text-Summarizer.git
cd AI-Text-Summarizer
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Application

### Using Streamlit

```bash
streamlit run app.py
```

The application will start on:

```text
http://localhost:8501
```

---

## Evaluation Metrics

The generated summaries are evaluated using the following metrics:

| Metric                 | Description                                         |
| ---------------------- | --------------------------------------------------- |
| Retention Score        | Measures how much important information is retained |
| Compression Percentage | Indicates the reduction in content length           |
| Simplicity Score       | Evaluates ease of understanding                     |
| Readability Score      | Measures readability of the generated summary       |
| Overall Accuracy Score | Combined performance assessment metric              |

---

## Applications

* Academic Research Summarization
* News Article Summarization
* Report Analysis
* Content Review
* Educational Learning Assistance
* Multilingual Information Access

---

## Future Enhancements

* PDF and DOCX document summarization
* Real-time web content summarization
* User-controlled summary length selection
* Domain-specific summarization models
* Mobile application deployment
* Integration of advanced Transformer architectures

---

## Advantages

* Reduces reading time significantly
* Preserves contextual meaning through abstractive summarization
* Supports multiple input sources
* Improves accessibility through translation and audio output
* Provides evaluation metrics for summary quality assessment
* User-friendly and interactive interface

---

## Authors

* **S. Gayathri**
* **K. Dharani**
* **N. Harshitha**

---

## License

This project has been developed for educational, academic, and research purposes.

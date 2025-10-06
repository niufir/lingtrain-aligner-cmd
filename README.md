# Lingtrain Aligner - Command Line Edition

ML powered library for the accurate texts alignment in different languages.

> **📌 This is a fork of the original [Lingtrain Aligner](https://github.com/averkij/lingtrain-aligner) by [Sergei Averkiev](https://github.com/averkij)**
>
> This fork adds a comprehensive command-line interface and additional features for automated book alignment workflows.

## 🆕 What's New in This Fork

This command-line edition extends the original Lingtrain Aligner with:

- ✅ **Full Command-Line Interface** - Process books directly from the terminal without GUI or Jupyter notebooks
- ✅ **Multiple File Format Support** - Direct support for PDF, EPUB, FB2, HTML, and TXT formats
- ✅ **Automated Text Extraction** - Built-in text extraction tool (`ExtractTextCmd.py`) for all supported formats
- ✅ **Improved Large Book Alignment** - Books are automatically split into smaller parts, each aligned independently, then merged into a single output. This approach provides faster processing and more accurate results for large texts
- ✅ **Smart Text Sanitization** - Automatically detects and removes non-equivalent text sections (such as introductions, forewords, and afterwords that differ between editions). Works effectively in approximately 80% of cases
- ✅ **Bidirectional Processing** - Optional bidirectional alignment mode
- ✅ **JSON Output Format** - Export aligned texts in JSON format with bidirectional mappings in a single file for easy integration with other tools and applications
- ✅ **Enhanced Language Detection** - Automatic language detection with manual override options
- ✅ **Metadata Support** - Add author, title, and year information to aligned books
- ✅ **Batch Processing Ready** - Designed for scripting and automation workflows


## Purpose

Main purpose of this alignment tool is to build parallel corpora using two or more raw texts in different languages. Texts should contain the same information (i.e., one text should be a translated analog oh the other text).

## Process

There are plenty of obstacles during the alignment process:

- The translator could translate several sentences as one.
- The translator could translate one sentence as many.
- There are some service marks in the text
    - Page numbers
    - Chapters and other section headings
    - Author and title information
    - Notes

While service marks can be handled manually (the tool helps to detect them), the translation conflicts should be handled more carefully.

Lingtrain Aligner tool will do almost all alignment work for you. It matches the sentence pairs automatically using the multilingual machine learning models. Then it searches for the alignment conflicts and resolves them. As output you will have the parallel corpora either as two distinct plain text files or as the merged corpora in widely used TMX format.

### Supported languages and models

Automated alignment process relies on the sentence embeddings models. Embeddings are multidimensional vectors of a special kind which are used to calculate a distance between the sentences.

#### Currently Supported Model

- **distiluse-base-multilingual-cased-v2** (Default and Recommended)
  - Reliable and fast performance
  - Moderate weights size — 500MB
  - Supports 50+ languages
  - Full list of supported languages can be found in [this paper](https://arxiv.org/abs/2004.09813)

#### Tested Languages

This command-line tool has been extensively tested with languages that have large corpora:
- **English**
- **Russian**
- **Spanish**
- **German**
- **French**

While the model theoretically supports 50+ languages, this tool is recommended for major languages with large speaker populations and extensive text corpora. Thorough testing has been performed primarily on the five languages listed above. The tool may not work reliably with smaller languages (such as Armenian, Bulgarian, and others with limited training data).

#### Models On Hold

The following models from the original project are currently on hold in this fork due to performance considerations during development:

- **LaBSE (Language-agnostic BERT Sentence Embedding)** - On hold
  - Heavy weights — 1.8GB
  - Supports 100+ languages
  - Slower processing for debugging and development

- **SONAR (Sentence-level multimOdal and laNguage-Agnostic Representations)** - On hold
  - Very large model (3 GB of weights)
  - Supports about 200 languages
  - Significantly slower for debugging and development

> **Note:** These models may be re-enabled in future releases once optimization work is complete.
  

## Command Line Interface

The Lingtrain Aligner provides a powerful command line interface for processing book alignment tasks. The tool supports various input formats and provides extensive configuration options.

### Installation

```bash
# Clone the repository
git clone https://github.com/niufir/lingtrain-aligner-cmd
cd lingtrain-aligner-cmd

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
python src/AlignerCmd.py --pathBookFrom <source_book> --pathBookTo <target_book> --pathBookOut <output_path>
```

### Supported File Formats

The tool supports the following input file formats:
- **TXT** - Plain text files
- **PDF** - Portable Document Format
- **EPUB** - Electronic Publication format
- **FB2** - FictionBook format
- **HTML** - HyperText Markup Language

### Command Line Arguments

#### Required Arguments

| Argument | Type | Description | Example |
|----------|------|-------------|---------|
| `--pathBookFrom` | string | Path to the source book file | `--pathBookFrom "book_en.pdf"` |
| `--pathBookTo` | string | Path to the target book file | `--pathBookTo "book_ru.epub"` |
| `--pathBookOut` | string | Path for the output aligned book in HTML format. JSON output file is automatically created with '.json' extension | `--pathBookOut "aligned_book.html"` |

#### Optional Arguments

| Argument | Type | Description | Default | Example |
|----------|------|-------------|---------|---------|
| `--isSkipSanitizing` | flag | Skip sanitizing the book content. By default, the tool attempts to remove introductions, forewords, and other non-equivalent text sections. If automatic removal fails, you can extract the text, manually clean it, and use this flag to skip sanitizing | False | `--isSkipSanitizing` |
| `--author` | string | Author name of the book | None | `--author "Ernest Hemingway"` |
| `--title` | string | Title of the book | None | `--title "The Old Man and the Sea"` |
| `--year` | string | Year of the book | None | `--year "1952"` |
| `--language-from` | string | Source language code | Auto-detected | `--language-from "en"` |
| `--language-to` | string | Target language code | Auto-detected | `--language-to "ru"` |
| `--bidirect-book` | flag | Process book in bidirectional mode | False | `--bidirect-book` |


### Usage Examples

#### Basic Alignment
```bash
python src/AlignerCmd.py \
  --pathBookFrom "prince_en.pdf" \
  --pathBookTo "prince_ru.epub" \
  --pathBookOut "prince_aligned.html"
```

#### Alignment with Metadata
```bash
python src/AlignerCmd.py \
  --pathBookFrom "dorian_grey_en.pdf" \
  --pathBookTo "dorian_grey_ru.epub" \
  --pathBookOut "dorian_grey_aligned.html" \
  --author "Oscar Wilde" \
  --title "The Picture of Dorian Gray" \
  --year "1890"
```

#### Using Specific Model
```bash
python src/AlignerCmd.py \
  --pathBookFrom "book_en.txt" \
  --pathBookTo "book_ru.txt" \
  --pathBookOut "book_aligned.html" \
  --model-name "sentence_transformer_multilingual_labse"
```

#### Bidirectional Processing
```bash
python src/AlignerCmd.py \
  --pathBookFrom "book_en.pdf" \
  --pathBookTo "book_ru.epub" \
  --pathBookOut "book_aligned.html" \
  --bidirect-book
```

#### Skip Sanitizing
```bash
python src/AlignerCmd.py \
  --pathBookFrom "clean_book_en.txt" \
  --pathBookTo "clean_book_ru.txt" \
  --pathBookOut "book_aligned.html" \
  --isSkipSanitizing
```

### Output

The tool generates several output files:

1. **Aligned HTML file** - The main output file containing the aligned text in HTML format
2. **Log files** - Detailed processing logs in the `LogAlign/` directory
3. **Extracted text files** - Clean text versions of the input files
4. **JSON/SQL files** - Additional data formats for the aligned content

### Language Detection

The tool automatically detects the language of input files using built-in language detection. However, automatic detection is not perfect and may fail in some cases. **It is recommended to explicitly specify the languages using `--language-from` and `--language-to` parameters whenever possible** for more reliable results.

### Performance Tips

- For large books, consider using the `sentence_transformer_multilingual` model for faster processing
- Use `--isSkipSanitizing` if your input files are already clean
- Ensure sufficient disk space for temporary files and model downloads
- The first run will download the selected ML model (500MB-3GB depending on the model)

## Credits and License

This project is a fork of [Lingtrain Aligner](https://github.com/averkij/lingtrain-aligner) by Sergei Averkiev.

**Original Author:** Sergei Averkiev ([@averkij](https://github.com/averkij))
**Original Repository:** https://github.com/averkij/lingtrain-aligner
**License:** GNU General Public License v3 (GPLv3)

### Command-Line Fork Enhancements

The command-line interface and additional features were developed to make the aligner more accessible for automated workflows and batch processing scenarios.

## Contributing

If you find bugs or have feature requests, please open an issue.

For issues related to the core alignment algorithm, please refer to the [original repository](https://github.com/averkij/lingtrain-aligner/issues).

# ExtractTextCmd

ExtractTextCmd is a command-line tool for extracting plain text from various book formats. It supports multiple input formats and provides a simple interface for text extraction.

## Supported Formats

- EPUB (.epub)
- FB2 (.fb2)
- PDF (.pdf)
- HTML (.html)
- Text (.txt)

## Installation

Ensure you have Python 3.x installed and all required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Basic usage:

```bash
python ExtractTextCmd.py --path_file <input_file_path> [--path_out <output_file_path>]
```

### Arguments

- `--path_file` (required): Path to the source book file
- `--path_out` (optional): Path for the output text file
  - If not specified, the output file will be created in the same directory as the input file with a `.txt` extension

### Examples

Extract text from an EPUB file:
```bash
python ExtractTextCmd.py --path_file "book.epub"
```

Extract text with custom output path:
```bash
python ExtractTextCmd.py --path_file "book.pdf" --path_out "output.txt"
```

## Return Values

- On success: Returns the path to the output text file
- On failure: Exits with status code 1 and prints error details
 e

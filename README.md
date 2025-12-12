# Statute_Finder.py and Starting Out

This Python program is accessed and ran via terminal and will accept .pdf, .docx, and .txt files. 

To start, the program will check your system to see if .pdf, .docx, and .txt Python support is enabled on your system. 

For example, I passed a .pdf document in my macOS terminal and needed to install PyPDF2. To do so, you will need to do the following in terminal to get pip and PyPDF2: 
* < python3 -m ensurepip --upgrade >
* < pip install PyPDF2 >

If the above set of code does not install pip, you can do this instead: 
* < curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py >
* < python3 get-pip.py >

For DOCX support: < pip install python-docx >

To run the program, open macOS terminal and type the following: < python3 Statute_Finder.py >

## What it Does

A message will appear in terminal telling you what it does and perform a system check to see if PDF, DOCX, and TXT Python support are enabled on your system.

It will then prompt the user for a path to their document. You can simply enter the tite of the document if you are running this script in the same directory (i.e. Folder).

The script will then gather the following information: 

### Catalog all statute refrences:
* U.S. Code (USC) citations
* Code of Federal Regulations (CFR)
* State code references
* Public law references
* Section references

### The program will generate a comprehensve report showing:
* Total number of references found
* Unique citations by type
* Cross-reference map with context
* Detailed location information

### After the anaylsis is complete, you will get:
1. Statute Cross-Reference Analysis
2. Unique Citations
3. Cross-Reference Map

Additionally, at the end it will ask the user if they want to save this report to a file (yes/no). If You want to save it, the program will ask for an output filename or just default to: statute_analysis_report.txt. The file will be saved in the same folder that the script is ran. 

I would include an example PDF; however, I worry about privacy. Examples can easily be found online. I used a brief from the United States Court of Appeals Fifth Circuit. 

## Initial Screen
<img width="853" height="688" alt="Statute_Finder" src="https://github.com/user-attachments/assets/76f40a43-e1d5-4fea-8a71-025b82167d79" />

## Program Details and Limitations

Will not support .doc files (Microsoft Word 97-2003). 

Does not support multiple files at once (can change, but still testing it with PDFs, DOCXs, and TXTs). 

Error handling for unsupported formats, missing library errors (with helpful messages), and file not found errors. 

The regex (Regular Expression) pattern in the __init__ method (of the StatuteCrossReferencerFinder Class) can be customized to add support for additinoal citation formats or jurisdictions. I have the following:
  * 'USC': r'\b(\d+)\s+U\.?S\.?C\.?\s+§?\s*(\d+[a-z]?(?:-\d+)?)'
  * 'CFR': r'\b(\d+)\s+C\.?F\.?R\.?\s+§?\s*(\d+(?:\.\d+)?)'
  * 'State_Code': r'\b([A-Z][a-z]+)\s+(?:Code|Stat\.?|Rev\.?\s+Stat\.?)\s+§?\s*(\d+(?:[.-]\d+)*)'
  * 'Section_Only': r'§\s*(\d+(?:[.-]\d+[a-z]?)*)'
  * 'Statute_Year': r'\b(Pub\.?\s+L\.?\s+No\.?\s+)(\d+-\d+)'

### Main Methods Used
* load_document(): Loads files
* _load_txt() | _load_pdf() | _load_docx(): Format-specific loaders
* find_references(): Finds all statute citations
* get_unique_references(): Gets unique citations by type
* create_cross_reference_map(): Shows ehere each statute appears with context
* analyze_file(): Analyze a file (calls load_document then analyze_document)
* analyze_document(): Complete analysis with statistics
* format_report(): Generates a readable report (OUTPUT)

### Privacy Concerns
* This program runs entirely on your local computer, meaning all processing happens on your machine.
* Does not connect to the internet (data does not get sent anywhere).
* Does not upload files (your documents remain on your device).
* Does not store data externally (all local).
* Does not use any external APIs or services.
* Analysis is done locally using Python's built-in regex matching.

**Bottom Line**: This is a completely offline, local tool. It is the same level of privacy as opening the document in a text editor or PDF viewer on your machine. 

Be mindful of where you save the reports if they contain sensitive citation information. This mostly concerns shared computers or saving the output to a cloud location that people lacking need-to-know can access. 

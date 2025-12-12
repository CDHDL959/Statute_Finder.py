import re
from collections import defaultdict
from typing import List, Dict, Set, Tuple, Union
from pathlib import Path

# Document parsing libraries
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

class StatuteCrossReferenceFinder:
    """
    A tool to find and analyze cross-references to statutes in legal documents.
    Supports various citation formats including USC, CFR, state codes, and more.
    """
    
    def __init__(self):
        # Patterns for different statute citation formats
        self.patterns = {
            'USC': r'\b(\d+)\s+U\.?S\.?C\.?\s+§?\s*(\d+[a-z]?(?:-\d+)?)',
            'CFR': r'\b(\d+)\s+C\.?F\.?R\.?\s+§?\s*(\d+(?:\.\d+)?)',
            'State_Code': r'\b([A-Z][a-z]+)\s+(?:Code|Stat\.?|Rev\.?\s+Stat\.?)\s+§?\s*(\d+(?:[.-]\d+)*)',
            'Section_Only': r'§\s*(\d+(?:[.-]\d+[a-z]?)*)',
            'Statute_Year': r'\b(Pub\.?\s+L\.?\s+No\.?\s+)(\d+-\d+)',
        }
    
    def load_document(self, file_path: Union[str, Path]) -> str:
        """
        Load text from various document formats.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text from the document
            
        Raises:
            ValueError: If file format is not supported or required library is missing
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = file_path.suffix.lower()
        
        if extension == '.txt':
            return self._load_txt(file_path)
        elif extension == '.pdf':
            return self._load_pdf(file_path)
        elif extension in ['.docx', '.doc']:
            return self._load_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def _load_txt(self, file_path: Path) -> str:
        """Load text from a plain text file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    def _load_pdf(self, file_path: Path) -> str:
        """Load text from a PDF file."""
        if not PDF_AVAILABLE:
            raise ValueError(
                "PyPDF2 is not installed. Install it with: pip install PyPDF2"
            )
        
        text = []
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text.append(page.extract_text())
        except Exception as e:
            raise ValueError(f"Error reading PDF: {e}")
        
        return '\n'.join(text)
    
    def _load_docx(self, file_path: Path) -> str:
        """Load text from a DOCX file."""
        if not DOCX_AVAILABLE:
            raise ValueError(
                "python-docx is not installed. Install it with: pip install python-docx"
            )
        
        try:
            doc = Document(file_path)
            text = []
            for paragraph in doc.paragraphs:
                text.append(paragraph.text)
            return '\n'.join(text)
        except Exception as e:
            raise ValueError(f"Error reading DOCX: {e}")
        
    def find_references(self, text: str) -> Dict[str, List[Dict]]:
        """
        Find all statute references in the given text.
        
        Args:
            text: The legal document text to search
            
        Returns:
            Dictionary with reference types as keys and lists of found references
        """
        results = defaultdict(list)
        
        for ref_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                ref_data = {
                    'full_text': match.group(0),
                    'position': match.span(),
                    'groups': match.groups()
                }
                results[ref_type].append(ref_data)
        
        return dict(results)
    
    def get_unique_references(self, text: str) -> Dict[str, Set[str]]:
        """
        Get unique statute references organized by type.
        
        Args:
            text: The legal document text to search
            
        Returns:
            Dictionary with reference types and sets of unique citations
        """
        refs = self.find_references(text)
        unique_refs = {}
        
        for ref_type, ref_list in refs.items():
            unique_refs[ref_type] = set(ref['full_text'] for ref in ref_list)
        
        return unique_refs
    
    def create_cross_reference_map(self, text: str) -> Dict[str, List[Tuple[int, str]]]:
        """
        Create a map showing where each statute is referenced in the document.
        
        Args:
            text: The legal document text to search
            
        Returns:
            Dictionary mapping statute citations to their locations and context
        """
        refs = self.find_references(text)
        xref_map = defaultdict(list)
        
        for ref_type, ref_list in refs.items():
            for ref in ref_list:
                citation = ref['full_text']
                position = ref['position'][0]
                
                # Extract context (50 chars before and after)
                start = max(0, position - 50)
                end = min(len(text), position + len(citation) + 50)
                context = text[start:end].replace('\n', ' ')
                
                xref_map[citation].append((position, context))
        
        return dict(xref_map)
    
    def analyze_file(self, file_path: Union[str, Path]) -> Dict:
        """
        Analyze statute references in a document file.
        
        Args:
            file_path: Path to PDF, DOCX, or TXT file
            
        Returns:
            Dictionary with complete analysis results
        """
        text = self.load_document(file_path)
        return self.analyze_document(text)
    
    def analyze_document(self, text: str) -> Dict:
        """
        Perform comprehensive analysis of statute references in document.
        
        Args:
            text: The legal document text to search
            
        Returns:
            Dictionary with complete analysis results
        """
        all_refs = self.find_references(text)
        unique_refs = self.get_unique_references(text)
        xref_map = self.create_cross_reference_map(text)
        
        total_refs = sum(len(refs) for refs in all_refs.values())
        unique_count = sum(len(refs) for refs in unique_refs.values())
        
        return {
            'total_references': total_refs,
            'unique_references': unique_count,
            'by_type': {k: len(v) for k, v in all_refs.items()},
            'unique_citations': unique_refs,
            'cross_reference_map': xref_map,
            'all_references': all_refs
        }
    
    def format_report(self, analysis: Dict) -> str:
        """
        Format analysis results into a readable report.
        
        Args:
            analysis: Results from analyze_document()
            
        Returns:
            Formatted string report
        """
        report = []
        report.append("=" * 60)
        report.append("STATUTE CROSS-REFERENCE ANALYSIS")
        report.append("=" * 60)
        report.append(f"\nTotal References Found: {analysis['total_references']}")
        report.append(f"Unique Citations: {analysis['unique_references']}")
        report.append("\nReferences by Type:")
        
        for ref_type, count in analysis['by_type'].items():
            report.append(f"  {ref_type}: {count}")
        
        report.append("\n" + "=" * 60)
        report.append("UNIQUE CITATIONS")
        report.append("=" * 60)
        
        for ref_type, citations in analysis['unique_citations'].items():
            if citations:
                report.append(f"\n{ref_type}:")
                for citation in sorted(citations):
                    report.append(f"  • {citation}")
        
        report.append("\n" + "=" * 60)
        report.append("CROSS-REFERENCE MAP")
        report.append("=" * 60)
        
        for citation, locations in sorted(analysis['cross_reference_map'].items()):
            report.append(f"\n{citation} (appears {len(locations)} time(s)):")
            for pos, context in locations:
                report.append(f"  Position {pos}: ...{context}...")
        
        return "\n".join(report)


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("STATUTE CROSS-REFERENCE FINDER")
    print("=" * 70)
    print("\nThis program analyzes legal documents to find and catalog all")
    print("statute references, including:")
    print("  • U.S. Code (USC) citations")
    print("  • Code of Federal Regulations (CFR)")
    print("  • State code references")
    print("  • Public law references")
    print("  • Section references")
    print("\nThe program will generate a comprehensive report showing:")
    print("  • Total number of references found")
    print("  • Unique citations by type")
    print("  • Cross-reference map with context")
    print("  • Detailed location information")
    
    print("\n" + "=" * 70)
    print("SYSTEM CHECK")
    print("=" * 70)
    print(f"PDF support (.pdf): {'✓ Available' if PDF_AVAILABLE else '✗ Not available - install PyPDF2'}")
    print(f"DOCX support (.docx): {'✓ Available' if DOCX_AVAILABLE else '✗ Not available - install python-docx'}")
    print("TXT support (.txt): ✓ Available")
    
    print("\n" + "=" * 70)
    
    # Get file path from user
    file_path = input("\nEnter the path to your document (.txt, .pdf, or .docx): ").strip()
    
    # Remove quotes if user included them
    file_path = file_path.strip('"').strip("'")
    
    if not file_path:
        print("\nError: No file path provided. Exiting.")
        exit(1)
    
    # Create finder instance
    finder = StatuteCrossReferenceFinder()
    
    try:
        print("\n" + "=" * 70)
        print("PROCESSING DOCUMENT...")
        print("=" * 70)
        print(f"File: {file_path}")
        
        # Analyze the file
        analysis = finder.analyze_file(file_path)
        
        # Print the report
        print("\n" + finder.format_report(analysis))
        
        # Ask if user wants to save the report
        print("\n" + "=" * 70)
        save_option = input("\nWould you like to save this report to a file? (yes/no): ").strip().lower()
        
        if save_option in ['yes', 'y']:
            output_file = input("Enter output filename (default: statute_analysis_report.txt): ").strip()
            if not output_file:
                output_file = "statute_analysis_report.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(finder.format_report(analysis))
            
            print(f"\n✓ Report saved to: {output_file}")
        
        print("\nAnalysis complete!")
        
    except FileNotFoundError:
        print(f"\n✗ Error: File not found - '{file_path}'")
        print("Please check the file path and try again.")
    except ValueError as e:
        print(f"\n✗ Error: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        print("Please check your file and try again.")
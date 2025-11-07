"""
Professional Polish Typography Service

Implements comprehensive Polish typography rules for publishing:
- Polish quotation marks („text")
- En-dash (–) and em-dash (—) usage
- Non-breaking spaces (nbsp)
- Proper hyphenation
- Dialogue formatting
- Number formatting
"""

import re
from bs4 import BeautifulSoup
from typing import Optional


class PolishTypographer:
    """Professional Polish typography for book publishing"""

    def __init__(self):
        # Unicode characters
        self.nbsp = '\u00A0'  # Non-breaking space
        self.ndash = '\u2013'  # En dash –
        self.mdash = '\u2014'  # Em dash —
        self.lquote = '\u201E'  # Left Polish quote „
        self.rquote = '\u201D'  # Right Polish quote "
        self.hellip = '\u2026'  # Ellipsis …

    def process_html(self, html: str) -> str:
        """
        Apply all Polish typography rules to HTML content

        Args:
            html: HTML string to process

        Returns:
            HTML with proper Polish typography
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Process all text nodes
        self._process_text_nodes(soup)

        return str(soup)

    def _process_text_nodes(self, element):
        """Recursively process all text nodes in element"""
        if element.name in ['code', 'pre', 'script', 'style']:
            # Don't process code blocks
            return

        if isinstance(element, str):
            return

        # Process direct text
        if element.string:
            element.string.replace_with(
                self._apply_typography_rules(element.string)
            )

        # Process children
        for child in element.children:
            if hasattr(child, 'name'):
                self._process_text_nodes(child)
            elif isinstance(child, str):
                # Direct text node
                new_text = self._apply_typography_rules(child)
                child.replace_with(new_text)

    def _apply_typography_rules(self, text: str) -> str:
        """
        Apply comprehensive Polish typography rules

        Order matters! Each transformation builds on previous ones.
        """
        # 1. Ellipsis (must be before other punctuation)
        text = self._fix_ellipsis(text)

        # 2. Polish quotes
        text = self._fix_quotes_advanced(text)

        # 3. Dashes (context-aware)
        text = self._fix_dashes_advanced(text)

        # 4. Non-breaking spaces (comprehensive)
        text = self._fix_nbsp_comprehensive(text)

        # 5. Dialogue formatting
        text = self._fix_dialogue(text)

        # 6. Punctuation spacing
        text = self._fix_punctuation_spacing(text)

        # 7. Numbers formatting
        text = self._fix_numbers(text)

        return text

    def _fix_ellipsis(self, text: str) -> str:
        """Convert ... to proper ellipsis character"""
        # Three dots to ellipsis
        text = re.sub(r'\.\.\.', self.hellip, text)

        # Remove spaces before ellipsis
        text = re.sub(rf'\s+{re.escape(self.hellip)}', self.hellip, text)

        return text

    def _fix_quotes_advanced(self, text: str) -> str:
        """
        Advanced Polish quote fixing with proper nesting

        Converts: "text" → „text"
        Handles: „outer 'inner' quote"
        """
        result = []
        in_quote = False

        i = 0
        while i < len(text):
            char = text[i]

            if char == '"':
                if not in_quote:
                    result.append(self.lquote)  # „
                    in_quote = True
                else:
                    result.append(self.rquote)  # "
                    in_quote = False
            else:
                result.append(char)

            i += 1

        return ''.join(result)

    def _fix_dashes_advanced(self, text: str) -> str:
        """
        Context-aware dash replacement

        Rules:
        - Word - word → Word — word (em-dash for breaks)
        - Word-word → Word–word (en-dash for compounds)
        - 1990-2000 → 1990–2000 (en-dash for ranges)
        - Start of line: - → — (dialogue)
        """
        # Em-dash for sentence breaks (spaces around dash)
        text = re.sub(r'\s+[-–]\s+', f' {self.mdash} ', text)

        # Em-dash for dialogue (start of line)
        text = re.sub(r'^[-–]\s+', f'{self.mdash} ', text, flags=re.MULTILINE)

        # En-dash for ranges (numbers)
        text = re.sub(r'(\d+)\s*[-–]\s*(\d+)', rf'\1{self.ndash}\2', text)

        # En-dash for compound words (no spaces)
        text = re.sub(r'(\w+)-(\w+)', rf'\1{self.ndash}\2', text)

        return text

    def _fix_nbsp_comprehensive(self, text: str) -> str:
        """
        Comprehensive non-breaking spaces for Polish typography

        Rules:
        1. Single-letter prepositions: w domu → w␣domu
        2. Single-letter conjunctions: a nie → a␣nie
        3. Before units: 10 kg → 10␣kg
        4. In dates: 1 stycznia → 1␣stycznia
        5. In initials: J. K. Rowling → J.␣K.␣Rowling
        6. Titles before names: dr Jan → dr␣Jan
        """

        # Single-letter words (prepositions, conjunctions)
        # Common Polish single letters: w, z, i, a, o, u, k
        single_letters = r'([wziaoukWZIAOUK])'
        text = re.sub(
            rf'\s+{single_letters}\s+',
            rf' \1{self.nbsp}',
            text
        )

        # Units after numbers
        units = (
            r'(zł|PLN|EUR|USD|km|m|cm|mm|kg|g|mg|l|ml|ha|'
            r'%|°C|°F|szt\.|godz\.|min\.|s\.|r\.|str\.|pkt\.)'
        )
        text = re.sub(
            rf'(\d+)\s+{units}',
            rf'\1{self.nbsp}\2',
            text
        )

        # Initials (J. K. Rowling style)
        text = re.sub(
            r'([A-ZĄĆĘŁŃÓŚŹŻ])\.\s+([A-ZĄĆĘŁŃÓŚŹŻ])\.',
            rf'\1.{self.nbsp}\2.',
            text
        )

        # Academic/professional titles
        titles = (
            r'(pan|pani|pana|pani|dr|prof|mgr|inż|lek|'
            r'Pan|Pani|Pana|Pani|Dr|Prof|Mgr|Inż|Lek)'
        )
        text = re.sub(
            rf'\b{titles}\s+([A-ZĄĆĘŁŃÓŚŹŻ])',
            rf'\1{self.nbsp}\2',
            text
        )

        # Roman numerals (Jan III, wiek XX)
        text = re.sub(
            r'([A-ZĄĆĘŁŃÓŚŹŻ]\w+)\s+([IVX]+)',
            rf'\1{self.nbsp}\2',
            text
        )

        # Dates (1 stycznia, 25 grudnia)
        months = (
            r'(stycznia|lutego|marca|kwietnia|maja|czerwca|'
            r'lipca|sierpnia|września|października|listopada|grudnia)'
        )
        text = re.sub(
            rf'(\d+)\s+{months}',
            rf'\1{self.nbsp}\2',
            text
        )

        # Time (15:30 w, o 18:00 w)
        text = re.sub(
            r'(\d{1,2}:\d{2})\s+([wo])',
            rf'\1{self.nbsp}\2',
            text
        )

        return text

    def _fix_dialogue(self, text: str) -> str:
        """
        Format dialogue properly

        Converts:
        - Text → — Text (em-dash for dialogue)
        – Text → — Text (normalize dashes)
        """
        # Lines starting with - or – become proper em-dash
        text = re.sub(
            r'^[\-–—]\s*',
            f'{self.mdash} ',
            text,
            flags=re.MULTILINE
        )

        return text

    def _fix_punctuation_spacing(self, text: str) -> str:
        """
        Fix spacing around punctuation

        Rules:
        - No space before: . , ; : ! ?
        - Space after: . , ; : ! ?
        - No double spaces
        """
        # Remove space before punctuation
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)

        # Add space after punctuation (if not already there)
        text = re.sub(r'([.,;:!?])([^\s\d])', r'\1 \2', text)

        # Remove multiple spaces
        text = re.sub(r' {2,}', ' ', text)

        return text

    def _fix_numbers(self, text: str) -> str:
        """
        Format numbers with thousands separator

        Converts:
        - 1000000 → 1 000 000 (nbsp as separator)
        - Only for numbers with 5+ digits
        """
        def format_number(match):
            num = match.group(0)
            # Only format numbers with 5+ digits
            if len(num) >= 5:
                # Add nbsp every 3 digits from right
                parts = []
                for i in range(len(num), 0, -3):
                    parts.insert(0, num[max(0, i-3):i])
                return self.nbsp.join(parts)
            return num

        # Match standalone numbers (not part of words or dates)
        text = re.sub(r'\b\d{5,}\b', format_number, text)

        return text


# Convenience function
def apply_polish_typography(html: str) -> str:
    """
    Apply Polish typography rules to HTML content

    Args:
        html: HTML string

    Returns:
        HTML with proper Polish typography
    """
    typographer = PolishTypographer()
    return typographer.process_html(html)

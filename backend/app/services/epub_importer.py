from ebooklib import epub, ITEM_DOCUMENT
from markdownify import markdownify as md
from bs4 import BeautifulSoup
import re
import tempfile
import os
from typing import Dict, List, Optional


class EPUBImporter:
    """Import EPUB files and convert to database structure"""

    def import_file(self, file_bytes: bytes) -> Dict:
        """
        Parse EPUB file and return data ready for book creation.

        Args:
            file_bytes: EPUB file content

        Returns:
            {
                'metadata': {
                    'title': str,
                    'author': str,
                    'language': str,
                    'publisher': str,
                    'isbn': str
                },
                'chapters': [
                    {
                        'title': str,
                        'content': str (Markdown),
                        'position': int
                    }
                ]
            }
        """
        # Save to temp file (ebooklib needs file path)
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            book = epub.read_epub(tmp_path)

            # Extract metadata
            metadata = self._extract_metadata(book)

            # Extract chapters
            chapters = self._extract_chapters(book)

            return {
                'metadata': metadata,
                'chapters': chapters
            }
        finally:
            os.unlink(tmp_path)

    def _extract_metadata(self, book: epub.EpubBook) -> Dict:
        """Extract metadata from EPUB"""
        return {
            'title': self._get_metadata(book, 'title') or 'Untitled',
            'author': self._get_metadata(book, 'creator') or 'Unknown Author',
            'language': self._get_metadata(book, 'language') or 'en',
            'publisher': self._get_metadata(book, 'publisher'),
            'isbn': self._get_identifier(book, 'ISBN')
        }

    def _get_metadata(self, book: epub.EpubBook, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get metadata value"""
        try:
            values = book.get_metadata('DC', key)
            if values and len(values) > 0:
                return values[0][0]
        except:
            pass
        return default

    def _get_identifier(self, book: epub.EpubBook, scheme: str) -> Optional[str]:
        """Get identifier like ISBN"""
        try:
            identifiers = book.get_metadata('DC', 'identifier')
            for identifier, attrs in identifiers:
                if attrs and attrs.get('scheme') == scheme:
                    return identifier
        except:
            pass
        return None

    def _extract_chapters(self, book: epub.EpubBook) -> List[Dict]:
        """Extract all chapters from EPUB"""
        chapters = []
        position = 0

        # Get all document items (XHTML files)
        for item in book.get_items_of_type(ITEM_DOCUMENT):
            try:
                # Get HTML content
                html_content = item.get_content().decode('utf-8')

                # Extract title from HTML
                title = self._extract_title_from_html(html_content)
                if not title:
                    title = f"Chapter {position + 1}"

                # Convert HTML to Markdown
                markdown_content = self._html_to_markdown(html_content)

                # Skip if empty
                if not markdown_content.strip():
                    continue

                chapters.append({
                    'title': title,
                    'content': markdown_content,
                    'position': position
                })

                position += 1

            except Exception as e:
                print(f"Error processing chapter: {e}")
                continue

        return chapters

    def _extract_title_from_html(self, html: str) -> Optional[str]:
        """Extract chapter title from HTML (first h1 or h2)"""
        soup = BeautifulSoup(html, 'html.parser')

        # Try h1 first
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()

        # Try h2
        h2 = soup.find('h2')
        if h2:
            return h2.get_text().strip()

        # Try title tag
        title = soup.find('title')
        if title:
            return title.get_text().strip()

        return None

    def _html_to_markdown(self, html: str) -> str:
        """Convert HTML to clean Markdown"""
        # Use markdownify library
        markdown = md(
            html,
            heading_style="ATX",  # Use # for headings
            bullets="-",          # Use - for lists
            strip=['script', 'style']  # Remove scripts/styles
        )

        # Clean up
        markdown = self._clean_markdown(markdown)

        return markdown

    def _clean_markdown(self, markdown: str) -> str:
        """Clean up converted Markdown"""
        # Remove excessive newlines (more than 2)
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)

        # Remove leading/trailing whitespace
        markdown = markdown.strip()

        # Remove empty links []()
        markdown = re.sub(r'\[\]\(\)', '', markdown)

        return markdown

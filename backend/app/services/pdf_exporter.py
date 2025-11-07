from typing import Optional
import markdown
from datetime import datetime
from ..models.book import Book
from ..schemas.book import ExportOptions

# Try to import WeasyPrint - it requires system dependencies
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


class PDFExporter:
    """Export books to PDF format"""

    def export(self, book: Book, options: Optional[ExportOptions] = None) -> bytes:
        """
        Generate PDF from book.

        Returns: PDF as bytes
        """
        if not WEASYPRINT_AVAILABLE:
            raise ImportError(
                "PDF export is temporarily unavailable. "
                "WeasyPrint requires system dependencies (libpango, libcairo) "
                "that are not installed on this server. "
                "Please use EPUB export instead."
            )

        if options is None:
            options = ExportOptions()

        # Generate HTML
        html = self._generate_html(book, options)

        # Get CSS for print
        css = self._get_print_css()

        # Generate PDF
        pdf_bytes = HTML(string=html).write_pdf(
            stylesheets=[CSS(string=css)]
        )

        return pdf_bytes

    def _generate_html(self, book: Book, options: ExportOptions) -> str:
        """Generate complete HTML for PDF"""
        html_parts = []

        # Start HTML
        html_parts.append(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8"/>
            <title>{book.title}</title>
        </head>
        <body>
        """)

        # Title page
        if options.include_title_page:
            html_parts.append(f"""
            <div class="title-page">
                <h1 class="book-title">{book.title}</h1>
                {f'<h2 class="subtitle">{book.subtitle}</h2>' if book.subtitle else ''}
                <p class="author">by {book.author}</p>
            </div>
            """)

        # Copyright page
        if options.include_copyright_page:
            year = datetime.now().year
            html_parts.append(f"""
            <div class="copyright-page">
                <p>© {year} {book.author}</p>
                <p>All rights reserved.</p>
                {f'<p>Publisher: {book.publisher}</p>' if book.publisher else ''}
                {f'<p>ISBN: {book.isbn}</p>' if book.isbn else ''}
            </div>
            """)

        # TOC
        if options.include_toc:
            html_parts.append('<div class="toc-page">')
            html_parts.append('<h1>Table of Contents</h1>')
            html_parts.append('<ul class="toc">')
            sorted_chapters = sorted(book.chapters, key=lambda c: c.position)
            for i, chapter in enumerate(sorted_chapters):
                title = chapter.title
                if options.number_chapters:
                    title = f"{options.chapter_prefix} {i+1}: {title}"
                html_parts.append(f'<li><a href="#chapter-{i+1}">{title}</a></li>')
            html_parts.append('</ul>')
            html_parts.append('</div>')

        # Chapters
        sorted_chapters = sorted(book.chapters, key=lambda c: c.position)
        for i, chapter in enumerate(sorted_chapters):
            chapter_html = markdown.markdown(
                chapter.content,
                extensions=['extra', 'codehilite', 'tables']
            )

            title = chapter.title
            if options.number_chapters:
                title = f"{options.chapter_prefix} {i+1}: {title}"

            html_parts.append(f'''
            <div class="chapter" id="chapter-{i+1}">
                <h1 class="chapter-title">{title}</h1>
                {chapter_html}
            </div>
            ''')

        # Close HTML
        html_parts.append("""
        </body>
        </html>
        """)

        return '\n'.join(html_parts)

    def _get_print_css(self) -> str:
        """Professional print CSS"""
        return """
        @page {
            size: A4;
            margin: 2.5cm 2cm 2.5cm 2cm;

            @top-center {
                content: string(book-title);
                font-size: 9pt;
                color: #666;
            }

            @bottom-center {
                content: counter(page);
                font-size: 9pt;
            }
        }

        @page :first {
            @top-center { content: none; }
            @bottom-center { content: none; }
        }

        @page title-page {
            @top-center { content: none; }
            @bottom-center { content: none; }
        }

        @page copyright-page {
            @top-center { content: none; }
            @bottom-center { content: none; }
        }

        @page toc-page {
            @top-center { content: none; }
        }

        body {
            font-family: 'Georgia', 'Times New Roman', serif;
            font-size: 11pt;
            line-height: 1.6;
            text-align: justify;
            hyphens: auto;
            color: #1a1a1a;
        }

        .title-page {
            page: title-page;
            page-break-after: always;
            text-align: center;
            margin-top: 30%;
        }

        .book-title {
            font-size: 32pt;
            font-weight: bold;
            margin-bottom: 0.3em;
        }

        .subtitle {
            font-size: 20pt;
            color: #666;
            margin-bottom: 2em;
        }

        .author {
            font-size: 16pt;
            font-style: italic;
        }

        .copyright-page {
            page: copyright-page;
            page-break-after: always;
            margin-top: 50%;
            font-size: 9pt;
            color: #666;
        }

        .toc-page {
            page: toc-page;
            page-break-after: always;
        }

        .toc {
            list-style: none;
            padding: 0;
        }

        .toc li {
            margin: 0.5em 0;
            font-size: 11pt;
        }

        .toc a {
            color: #000;
            text-decoration: none;
        }

        .chapter {
            page-break-before: always;
        }

        .chapter-title {
            font-size: 24pt;
            font-weight: bold;
            margin-bottom: 1.5em;
            margin-top: 0;
            page-break-after: avoid;
        }

        h1, h2, h3, h4 {
            page-break-after: avoid;
            font-weight: bold;
        }

        h2 { font-size: 18pt; margin-top: 1.5em; }
        h3 { font-size: 14pt; margin-top: 1.2em; }
        h4 { font-size: 12pt; margin-top: 1em; }

        p {
            margin: 0 0 0.5em 0;
            text-indent: 1.5em;
        }

        p:first-of-type,
        h1 + p, h2 + p, h3 + p, h4 + p {
            text-indent: 0;
        }

        blockquote {
            margin: 1.5em 2em;
            padding: 0.5em 1em;
            border-left: 3px solid #ccc;
            font-style: italic;
            background: #f9f9f9;
        }

        ul, ol {
            margin: 1em 0 1em 2em;
        }

        li {
            margin: 0.5em 0;
        }

        code {
            font-family: 'Courier New', monospace;
            background: #f5f5f5;
            padding: 0.1em 0.3em;
            font-size: 10pt;
        }

        pre {
            background: #f5f5f5;
            padding: 1em;
            overflow-x: auto;
            page-break-inside: avoid;
            font-size: 9pt;
        }

        table {
            border-collapse: collapse;
            margin: 1em 0;
            page-break-inside: avoid;
        }

        th, td {
            border: 1px solid #ddd;
            padding: 0.5em;
            text-align: left;
        }

        th {
            background: #f5f5f5;
            font-weight: bold;
        }
        """

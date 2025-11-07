from typing import Optional, List, Dict
import markdown
from datetime import datetime
from bs4 import BeautifulSoup
from ..models.book import Book
from ..schemas.book import ExportOptions
from .typographer import apply_polish_typography

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

            # Build comprehensive copyright information
            copyright_parts = []
            copyright_parts.append(f'<p class="copyright-notice">© {year} {book.author}</p>')
            copyright_parts.append('<p class="rights-statement">All rights reserved.</p>')

            if book.publisher:
                copyright_parts.append(f'<p class="publisher-info">Published by {book.publisher}</p>')
            else:
                copyright_parts.append('<p class="publisher-info">Self-published</p>')

            copyright_parts.append(f'<p class="edition-info">First edition, {year}</p>')

            if book.isbn:
                copyright_parts.append(f'<p class="isbn">ISBN: {book.isbn}</p>')

            copyright_parts.append('''
                <p class="legal-notice">
                    No part of this publication may be reproduced, stored in a retrieval system,
                    or transmitted in any form or by any means, electronic, mechanical, photocopying,
                    recording, or otherwise, without the prior written permission of the copyright owner.
                </p>
            ''')

            copyright_parts.append('<p class="created-with">Created with Book Composer</p>')

            html_parts.append(f"""
            <div class="copyright-page">
                {''.join(copyright_parts)}
            </div>
            """)

        # Process all chapters first (for hierarchical TOC)
        sorted_chapters = sorted(book.chapters, key=lambda c: c.position)
        processed_chapters = []

        for i, chapter in enumerate(sorted_chapters):
            # Convert markdown to HTML
            chapter_html = markdown.markdown(
                chapter.content,
                extensions=['extra', 'codehilite', 'tables']
            )
            # Apply professional Polish typography
            chapter_html = apply_polish_typography(chapter_html)

            # Extract headings for TOC and add IDs
            soup = BeautifulSoup(chapter_html, 'html.parser')
            headings = []

            for heading in soup.find_all(['h2', 'h3']):
                text = heading.get_text().strip()
                # Create ID if not present
                if not heading.get('id'):
                    heading_id = f"chapter-{i+1}-{text.lower().replace(' ', '-')[:50]}"
                    heading['id'] = heading_id
                else:
                    heading_id = heading['id']

                headings.append({
                    'level': heading.name,
                    'text': text,
                    'id': heading_id
                })

            # Update chapter HTML with IDs
            chapter_html = str(soup)

            title = chapter.title
            if options.number_chapters:
                title = f"{options.chapter_prefix} {i+1}: {title}"

            processed_chapters.append({
                'index': i + 1,
                'title': title,
                'html': chapter_html,
                'headings': headings
            })

        # Generate hierarchical TOC
        if options.include_toc:
            html_parts.append('<div class="toc-page">')
            html_parts.append('<h1>Table of Contents</h1>')
            html_parts.append('<ul class="toc">')

            for chapter_info in processed_chapters:
                # Chapter entry
                html_parts.append(
                    f'<li class="toc-chapter">'
                    f'<a href="#chapter-{chapter_info["index"]}">{chapter_info["title"]}</a>'
                )

                # Subheadings (H2 and H3)
                if chapter_info['headings']:
                    html_parts.append('<ul class="toc-subsections">')
                    for heading in chapter_info['headings']:
                        css_class = 'toc-h2' if heading['level'] == 'h2' else 'toc-h3'
                        html_parts.append(
                            f'<li class="{css_class}">'
                            f'<a href="#{heading["id"]}">{heading["text"]}</a>'
                            f'</li>'
                        )
                    html_parts.append('</ul>')

                html_parts.append('</li>')

            html_parts.append('</ul>')
            html_parts.append('</div>')

        # Output processed chapters
        for chapter_info in processed_chapters:
            html_parts.append(f'''
            <article class="chapter" id="chapter-{chapter_info["index"]}" data-chapter-title="{chapter_info["title"]}">
                <header class="chapter-header">
                    <h1 class="chapter-title">{chapter_info["title"]}</h1>
                </header>
                <section class="chapter-content">
                    {chapter_info["html"]}
                </section>
            </article>
            ''')

        # Close HTML
        html_parts.append("""
        </body>
        </html>
        """)

        return '\n'.join(html_parts)

    def _get_print_css(self) -> str:
        """Professional print CSS with Polish typography"""
        return """
        /* ============================================
           PROFESSIONAL BOOK PRINT CSS
           For high-quality PDF book publishing
           ============================================ */

        /* ====================
           PAGE SETUP - A4 Book Format
           ==================== */
        @page {
            size: A4;
            margin: 2.5cm 2cm 2.5cm 2cm;

            /* Running headers - book title */
            @top-left {
                content: string(book-title);
                font-family: 'Libre Baskerville', 'Georgia', serif;
                font-size: 9pt;
                color: #666;
                font-variant: small-caps;
                letter-spacing: 0.05em;
            }

            /* Page numbers in footer */
            @bottom-center {
                content: counter(page);
                font-family: 'Libre Baskerville', 'Georgia', serif;
                font-size: 9pt;
                color: #333;
            }
        }

        /* Right pages (recto) - chapter title in header */
        @page :right {
            @top-right {
                content: string(chapter-title);
                font-family: 'Libre Baskerville', 'Georgia', serif;
                font-size: 9pt;
                color: #666;
                font-style: italic;
            }
            @top-left { content: none; }
        }

        /* Left pages (verso) - book title in header */
        @page :left {
            @top-left {
                content: string(book-title);
                font-family: 'Libre Baskerville', 'Georgia', serif;
                font-size: 9pt;
                color: #666;
                font-variant: small-caps;
                letter-spacing: 0.05em;
            }
            @top-right { content: none; }
        }

        /* First page - no headers/footers */
        @page :first {
            @top-left { content: none; }
            @top-right { content: none; }
            @bottom-center { content: none; }
        }

        /* Title page - no headers/footers */
        @page title-page {
            @top-left { content: none; }
            @top-right { content: none; }
            @bottom-center { content: none; }
        }

        /* Copyright page - no headers/footers */
        @page copyright-page {
            @top-left { content: none; }
            @top-right { content: none; }
            @bottom-center { content: none; }
        }

        /* TOC page - book title only, no page numbers on first TOC page */
        @page toc-page {
            @top-right { content: none; }
        }

        @page toc-page:first {
            @bottom-center { content: none; }
        }

        /* Chapter start pages - no running header */
        @page chapter-start {
            @top-left { content: none; }
            @top-right { content: none; }
        }

        /* ====================
           BASE TYPOGRAPHY
           ==================== */
        body {
            font-family: 'Libre Baskerville', 'Georgia', 'Palatino', 'Book Antiqua', serif;
            font-size: 11pt;
            line-height: 1.7;
            text-align: justify;
            hyphens: auto;
            -webkit-hyphens: auto;
            -moz-hyphens: auto;
            color: #1a1a1a;
            widows: 2;
            orphans: 2;
        }

        /* Set book title for running headers */
        h1.book-title {
            string-set: book-title content();
        }

        /* Set chapter title for running headers */
        h1.chapter-title {
            string-set: chapter-title content();
        }

        /* ====================
           TITLE PAGE
           ==================== */
        .title-page {
            page: title-page;
            page-break-after: always;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
            margin-top: 35%;
        }

        .book-title {
            font-size: 36pt;
            font-weight: bold;
            letter-spacing: 0.03em;
            margin-bottom: 0.4em;
            line-height: 1.2;
            color: #1a1a1a;
            text-transform: uppercase;
            font-variant: small-caps;
        }

        .subtitle {
            font-size: 20pt;
            color: #555;
            margin-bottom: 3em;
            font-weight: normal;
            font-style: italic;
            letter-spacing: 0.02em;
        }

        .author {
            font-size: 16pt;
            font-style: normal;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #333;
            margin-top: 2em;
        }

        /* ====================
           COPYRIGHT PAGE
           ==================== */
        .copyright-page {
            page: copyright-page;
            page-break-after: always;
            margin-top: 60%;
            font-size: 9pt;
            line-height: 1.5;
            color: #666;
        }

        .copyright-page p {
            margin: 0.5em 0;
            text-indent: 0;
        }

        /* ====================
           TABLE OF CONTENTS - Hierarchical
           ==================== */
        .toc-page {
            page: toc-page;
            page-break-after: always;
        }

        .toc-page h1 {
            font-size: 24pt;
            font-variant: small-caps;
            letter-spacing: 0.08em;
            text-align: center;
            margin-bottom: 2em;
            border-bottom: 2px solid #333;
            padding-bottom: 0.5em;
        }

        .toc {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        /* Chapter entries - bold */
        .toc-chapter {
            margin: 1em 0 0.5em 0;
        }

        .toc-chapter > a {
            font-weight: bold;
            font-size: 11pt;
            color: #1a1a1a;
            text-decoration: none;
        }

        /* Subsections container */
        .toc-subsections {
            list-style: none;
            padding: 0;
            margin: 0.5em 0 0 0;
        }

        /* H2 subsections - indented */
        .toc-h2 {
            margin: 0.4em 0 0.2em 1.5em;
        }

        .toc-h2 a {
            font-size: 10pt;
            color: #2a2a2a;
            text-decoration: none;
            font-weight: normal;
        }

        /* H3 subsections - double indented */
        .toc-h3 {
            margin: 0.3em 0 0.2em 3em;
        }

        .toc-h3 a {
            font-size: 9.5pt;
            color: #444;
            text-decoration: none;
            font-weight: normal;
            font-style: italic;
        }

        /* Leader dots for page numbers */
        .toc a::after {
            content: leader('.') target-counter(attr(href), page);
            color: #888;
            font-size: 9pt;
            margin-left: 0.5em;
        }

        /* Hover effect */
        .toc a:hover {
            color: #0066cc;
        }

        /* ====================
           CHAPTERS
           ==================== */
        .chapter {
            page-break-before: always;
            page: chapter-start;
        }

        .chapter-title {
            font-size: 28pt;
            font-weight: bold;
            letter-spacing: 0.02em;
            margin-bottom: 2em;
            margin-top: 2em;
            text-align: center;
            page-break-after: avoid;
            font-variant: small-caps;
            color: #1a1a1a;
        }

        /* ====================
           SEMANTIC STRUCTURE
           ==================== */
        .chapter {
            /* Article element for semantic HTML5 */
        }

        .chapter-header {
            margin-bottom: 2em;
        }

        .chapter-title {
            /* Styled below in chapter-specific section */
        }

        .chapter-content {
            /* Main chapter content container */
        }

        /* ====================
           DROP CAPS - Beautiful first letter
           ==================== */
        .chapter-content > p:first-of-type::first-letter {
            font-size: 3.8em;
            line-height: 0.85;
            float: left;
            margin: 0.08em 0.12em 0 0;
            font-weight: bold;
            color: #2a2a2a;
        }

        /* ====================
           PARAGRAPHS
           ==================== */
        p {
            margin: 0;
            text-indent: 1.5em;
            line-height: 1.7;
        }

        /* No indent after headings, lists, blockquotes */
        h1 + p, h2 + p, h3 + p, h4 + p,
        ul + p, ol + p, blockquote + p,
        hr + p, figure + p,
        .chapter-content > p:first-of-type {
            text-indent: 0;
        }

        /* ====================
           HEADINGS
           ==================== */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Libre Baskerville', 'Georgia', serif;
            font-weight: bold;
            page-break-after: avoid;
            page-break-inside: avoid;
            color: #1a1a1a;
        }

        h2 {
            font-size: 18pt;
            margin-top: 2em;
            margin-bottom: 0.75em;
            letter-spacing: 0.02em;
            font-variant: small-caps;
        }

        h3 {
            font-size: 14pt;
            margin-top: 1.5em;
            margin-bottom: 0.6em;
            letter-spacing: 0.01em;
        }

        h4 {
            font-size: 12pt;
            margin-top: 1.2em;
            margin-bottom: 0.5em;
            font-weight: 600;
        }

        /* ====================
           SCENE BREAKS
           ==================== */
        hr {
            border: none;
            text-align: center;
            margin: 2em 0;
            height: 1.5em;
            page-break-after: avoid;
        }

        hr::before {
            content: "* * *";
            font-size: 1.2em;
            letter-spacing: 1.5em;
            color: #888;
            font-weight: normal;
        }

        /* ====================
           BLOCKQUOTES
           ==================== */
        blockquote {
            margin: 1.75em 2.5em;
            padding: 1em 1.25em;
            font-style: italic;
            border-left: 3px solid #c0c0c0;
            background: #f8f8f8;
            page-break-inside: avoid;
            color: #2a2a2a;
        }

        blockquote p {
            text-indent: 0;
            margin-bottom: 0.5em;
        }

        blockquote p:last-child {
            margin-bottom: 0;
        }

        blockquote cite {
            display: block;
            text-align: right;
            font-style: normal;
            font-size: 0.9em;
            color: #666;
            margin-top: 0.5em;
        }

        blockquote cite::before {
            content: "— ";
        }

        /* ====================
           LISTS
           ==================== */
        ul, ol {
            margin: 1.2em 0;
            padding-left: 2.5em;
        }

        ul {
            list-style-type: disc;
        }

        ol {
            list-style-type: decimal;
        }

        li {
            margin: 0.6em 0;
            line-height: 1.6;
        }

        li p {
            text-indent: 0;
            margin: 0.3em 0;
        }

        /* Nested lists */
        ul ul, ol ol, ul ol, ol ul {
            margin: 0.5em 0;
        }

        /* ====================
           CODE BLOCKS
           ==================== */
        code {
            font-family: 'Courier New', 'Consolas', monospace;
            background: #f5f5f5;
            padding: 0.15em 0.4em;
            font-size: 9.5pt;
            border-radius: 2px;
            color: #c7254e;
        }

        pre {
            background: #f8f8f8;
            border: 1px solid #e0e0e0;
            border-left: 3px solid #999;
            padding: 1em 1.2em;
            overflow-x: auto;
            page-break-inside: avoid;
            font-size: 9pt;
            line-height: 1.4;
            margin: 1.5em 0;
        }

        pre code {
            background: none;
            padding: 0;
            border-radius: 0;
            color: #333;
        }

        /* ====================
           TABLES
           ==================== */
        table {
            border-collapse: collapse;
            margin: 1.5em auto;
            page-break-inside: avoid;
            width: 100%;
            font-size: 10pt;
        }

        thead {
            page-break-after: avoid;
        }

        th, td {
            border: 1px solid #d0d0d0;
            padding: 0.6em 0.8em;
            text-align: left;
        }

        th {
            background: #f0f0f0;
            font-weight: bold;
            color: #2a2a2a;
            font-variant: small-caps;
            letter-spacing: 0.05em;
        }

        tr:nth-child(even) td {
            background: #fafafa;
        }

        /* ====================
           IMAGES & FIGURES
           ==================== */
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1.5em auto;
            page-break-inside: avoid;
        }

        figure {
            margin: 1.5em 0;
            text-align: center;
            page-break-inside: avoid;
        }

        figcaption {
            font-size: 9pt;
            font-style: italic;
            color: #666;
            margin-top: 0.5em;
            text-align: center;
        }

        /* ====================
           EMPHASIS & STRONG
           ==================== */
        em {
            font-style: italic;
        }

        strong {
            font-weight: bold;
            color: #1a1a1a;
        }

        strong em, em strong {
            font-weight: bold;
            font-style: italic;
        }

        /* ====================
           LINKS (for PDF bookmarks)
           ==================== */
        a {
            color: #1a1a1a;
            text-decoration: none;
        }

        /* ====================
           PRINT-SPECIFIC
           ==================== */
        * {
            box-sizing: border-box;
        }

        /* Prevent awkward breaks */
        h1, h2, h3, h4, h5, h6 {
            page-break-after: avoid;
        }

        p, blockquote, ul, ol, figure {
            page-break-inside: avoid;
        }

        /* Widow and orphan control */
        p {
            widows: 2;
            orphans: 2;
        }
        """

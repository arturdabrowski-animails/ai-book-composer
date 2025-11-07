from ebooklib import epub
import markdown
from typing import Optional
from ..models.book import Book
from ..schemas.book import ExportOptions
from .typographer import apply_polish_typography


class EPUBBuilder:
    """Build EPUB files from Book objects"""

    def build_from_book(
        self,
        book: Book,
        options: Optional[ExportOptions] = None
    ) -> epub.EpubBook:
        """
        Build EPUB from database Book object.

        Args:
            book: Book object from database with chapters
            options: Export options (chapter numbering, etc.)

        Returns:
            EpubBook ready to write
        """
        if options is None:
            options = ExportOptions()

        epub_book = epub.EpubBook()

        # Set metadata from book
        epub_book.set_identifier(str(book.id))
        epub_book.set_title(book.title)
        epub_book.set_language(book.language)
        epub_book.add_author(book.author)

        if book.publisher:
            epub_book.add_metadata('DC', 'publisher', book.publisher)
        if book.isbn:
            epub_book.add_metadata('DC', 'identifier', book.isbn, {'scheme': 'ISBN'})

        # Add default CSS
        css = self._get_default_css()
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=css
        )
        epub_book.add_item(nav_css)

        # Collect items for spine
        spine_items = ['nav']

        # Add title page if requested
        if options.include_title_page:
            title_page = self._create_title_page(book)
            epub_book.add_item(title_page)
            spine_items.append(title_page)

        # Add copyright page if requested
        if options.include_copyright_page:
            copyright_page = self._create_copyright_page(book)
            epub_book.add_item(copyright_page)
            spine_items.append(copyright_page)

        # Add chapters
        chapters_list = []
        sorted_chapters = sorted(book.chapters, key=lambda c: c.position)

        for i, chapter in enumerate(sorted_chapters):
            # Convert Markdown to HTML
            html_content = self._markdown_to_html(chapter.content)

            # Create chapter title
            chapter_title = chapter.title
            if options.number_chapters:
                chapter_title = f"{options.chapter_prefix} {i+1}: {chapter.title}"

            # Create EPUB chapter
            epub_chapter = self._create_chapter(
                title=chapter_title,
                filename=f"chapter_{i+1}.xhtml",
                content=html_content
            )

            epub_book.add_item(epub_chapter)
            chapters_list.append(epub_chapter)
            spine_items.append(epub_chapter)

        # Build TOC
        if options.include_toc:
            epub_book.toc = tuple(chapters_list)
            epub_book.add_item(epub.EpubNcx())
            epub_book.add_item(epub.EpubNav())

        # Set spine
        epub_book.spine = spine_items

        return epub_book

    def _markdown_to_html(self, markdown_text: str) -> str:
        """Convert Markdown to HTML with Polish typography"""
        html = markdown.markdown(
            markdown_text,
            extensions=['extra', 'codehilite', 'tables']
        )
        # Apply professional Polish typography
        return apply_polish_typography(html)

    def _create_title_page(self, book: Book) -> epub.EpubHtml:
        """Create title page"""
        content = f"""
        <?xml version='1.0' encoding='utf-8'?>
        <!DOCTYPE html>
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <title>{book.title}</title>
            <link href="style/nav.css" rel="stylesheet" type="text/css"/>
        </head>
        <body>
            <div class="title-page">
                <h1 class="book-title">{book.title}</h1>
                {f'<h2 class="subtitle">{book.subtitle}</h2>' if book.subtitle else ''}
                <p class="author">by {book.author}</p>
            </div>
        </body>
        </html>
        """

        title_page = epub.EpubHtml(
            title='Title Page',
            file_name='title_page.xhtml',
            lang=book.language
        )
        title_page.content = content

        return title_page

    def _create_copyright_page(self, book: Book) -> epub.EpubHtml:
        """Create copyright page"""
        from datetime import datetime
        year = datetime.now().year

        content = f"""
        <?xml version='1.0' encoding='utf-8'?>
        <!DOCTYPE html>
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <title>Copyright</title>
            <link href="style/nav.css" rel="stylesheet" type="text/css"/>
        </head>
        <body>
            <div class="copyright-page">
                <p>© {year} {book.author}</p>
                <p>All rights reserved.</p>
                {f'<p>Publisher: {book.publisher}</p>' if book.publisher else ''}
                {f'<p>ISBN: {book.isbn}</p>' if book.isbn else ''}
            </div>
        </body>
        </html>
        """

        copyright_page = epub.EpubHtml(
            title='Copyright',
            file_name='copyright.xhtml',
            lang=book.language
        )
        copyright_page.content = content

        return copyright_page

    def _create_chapter(
        self,
        title: str,
        filename: str,
        content: str
    ) -> epub.EpubHtml:
        """Create a chapter"""
        html_content = f"""
        <?xml version='1.0' encoding='utf-8'?>
        <!DOCTYPE html>
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <title>{title}</title>
            <link href="style/nav.css" rel="stylesheet" type="text/css"/>
        </head>
        <body>
            <div class="chapter">
                <h1>{title}</h1>
                {content}
            </div>
        </body>
        </html>
        """

        chapter = epub.EpubHtml(
            title=title,
            file_name=filename,
            lang='en'
        )
        chapter.content = html_content

        return chapter

    def _get_default_css(self) -> str:
        """Professional publishing CSS for EPUB"""
        return """
/* =====================================================
   BOOK COMPOSER - Professional Publishing CSS
   Publication-quality EPUB typography
   ===================================================== */

/* === FONTS === */
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap');

/* === BASE === */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Libre Baskerville', 'Georgia', 'Palatino', serif;
    font-size: 1em;
    line-height: 1.7;
    text-align: justify;
    hyphens: auto;
    -webkit-hyphens: auto;
    -moz-hyphens: auto;
    hyphenate-limit-chars: 6 3 2;
    color: #1a1a1a;
    padding: 1.5em;
    max-width: 40em;
    margin: 0 auto;
}

/* === PARAGRAPHS === */
p {
    text-indent: 1.5em;
    margin: 0;
}

/* No indent after headings, lists, blockquotes */
h1 + p, h2 + p, h3 + p, h4 + p,
ul + p, ol + p, blockquote + p,
hr + p, figure + p {
    text-indent: 0;
}

/* First paragraph of chapter */
.chapter > p:first-of-type {
    text-indent: 0;
}

/* === DROP CAPS === */
.chapter > p:first-of-type::first-letter {
    font-size: 3.5em;
    line-height: 0.9;
    float: left;
    margin: 0.1em 0.1em 0 0;
    font-weight: bold;
}

/* === HEADINGS === */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Libre Baskerville', serif;
    font-weight: 700;
    page-break-after: avoid;
    page-break-inside: avoid;
    color: #1a1a1a;
    text-align: left;
}

h1 {
    font-size: 2.5em;
    margin: 2em 0 1.5em 0;
    page-break-before: always;
    text-align: center;
    font-variant: small-caps;
    letter-spacing: 0.05em;
}

h2 {
    font-size: 1.75em;
    margin: 1.5em 0 1em 0;
}

h3 {
    font-size: 1.35em;
    margin: 1.25em 0 0.75em 0;
}

h4 {
    font-size: 1.15em;
    margin: 1em 0 0.5em 0;
}

/* === CHAPTER NUMBERS === */
.chapter-number {
    display: block;
    font-size: 0.6em;
    font-weight: normal;
    letter-spacing: 0.15em;
    margin-bottom: 0.5em;
    text-transform: uppercase;
    color: #666;
}

/* === LISTS === */
ul, ol {
    margin: 1.25em 0;
    padding-left: 2.5em;
}

li {
    margin: 0.5em 0;
    line-height: 1.6;
}

ul {
    list-style-type: disc;
}

ul ul {
    list-style-type: circle;
    margin: 0.5em 0;
}

ol {
    list-style-type: decimal;
}

ol ol {
    list-style-type: lower-alpha;
}

/* === QUOTES === */
blockquote {
    margin: 1.75em 2.5em;
    padding: 1em 1.25em;
    font-style: italic;
    border-left: 3px solid #c0c0c0;
    background: linear-gradient(to right, #f8f8f8 0%, #ffffff 100%);
    page-break-inside: avoid;
}

blockquote p {
    text-indent: 0 !important;
    margin-bottom: 0.75em;
}

blockquote p:last-child {
    margin-bottom: 0;
}

cite {
    display: block;
    text-align: right;
    font-style: normal;
    font-size: 0.9em;
    margin-top: 0.75em;
    color: #555;
}

cite::before {
    content: "— ";
}

/* === SCENE BREAKS === */
hr {
    border: none;
    text-align: center;
    margin: 2.5em 0;
    height: 1.5em;
    position: relative;
}

hr::before {
    content: "* * *";
    font-size: 1.2em;
    letter-spacing: 1.5em;
    color: #888;
}

/* === EMPHASIS === */
strong {
    font-weight: 700;
}

em {
    font-style: italic;
}

/* === CODE === */
code {
    font-family: 'Courier New', 'Consolas', monospace;
    font-size: 0.9em;
    background: #f5f5f5;
    padding: 0.1em 0.3em;
    border-radius: 2px;
}

pre {
    font-family: 'Courier New', 'Consolas', monospace;
    font-size: 0.85em;
    background: #f5f5f5;
    padding: 1em;
    overflow-x: auto;
    border-left: 3px solid #ccc;
    margin: 1.5em 0;
    page-break-inside: avoid;
}

pre code {
    background: none;
    padding: 0;
}

/* === IMAGES === */
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 2em auto;
}

figure {
    margin: 2em 0;
    text-align: center;
    page-break-inside: avoid;
}

figcaption {
    font-size: 0.9em;
    font-style: italic;
    color: #666;
    margin-top: 0.75em;
    text-align: center;
}

/* === LINKS === */
a {
    color: #1a1a1a;
    text-decoration: underline;
}

a:hover {
    color: #555;
}

/* === TABLES === */
table {
    border-collapse: collapse;
    margin: 1.5em auto;
    width: 100%;
    page-break-inside: avoid;
}

th, td {
    border: 1px solid #ddd;
    padding: 0.75em;
    text-align: left;
}

th {
    background: #f5f5f5;
    font-weight: 700;
}

/* === FRONT MATTER === */
.title-page {
    text-align: center;
    page-break-after: always;
    margin-top: 30vh;
}

.title-page h1 {
    font-size: 3em;
    margin-bottom: 0.5em;
    font-variant: normal;
    letter-spacing: 0.02em;
}

.title-page .subtitle {
    font-size: 1.5em;
    font-weight: normal;
    font-style: italic;
    color: #555;
    margin-bottom: 2em;
}

.title-page .author {
    font-size: 1.25em;
    font-variant: small-caps;
    letter-spacing: 0.1em;
}

.copyright-page {
    page-break-after: always;
    font-size: 0.85em;
    color: #555;
    margin-top: 50vh;
}

.copyright-page p {
    text-indent: 0 !important;
    margin: 0.5em 0;
    text-align: left;
}

.dedication {
    text-align: center;
    font-style: italic;
    page-break-after: always;
    margin-top: 30vh;
}

.dedication p {
    text-indent: 0 !important;
    font-size: 1.1em;
}

/* === SPECIAL BOXES === */
.tip-box, .warning-box, .info-box {
    margin: 1.75em 0;
    padding: 1.25em;
    border-radius: 4px;
    page-break-inside: avoid;
    border-left: 4px solid;
    background: #fafafa;
}

.tip-box {
    border-left-color: #4caf50;
    background: linear-gradient(to right, #e8f5e9 0%, #ffffff 100%);
}

.warning-box {
    border-left-color: #ff9800;
    background: linear-gradient(to right, #fff3e0 0%, #ffffff 100%);
}

.info-box {
    border-left-color: #2196f3;
    background: linear-gradient(to right, #e3f2fd 0%, #ffffff 100%);
}

.tip-box p, .warning-box p, .info-box p {
    text-indent: 0 !important;
}

/* === PAGE BREAKS === */
.page-break {
    page-break-after: always;
}

.avoid-break {
    page-break-inside: avoid;
}
        """

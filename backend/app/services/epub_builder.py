from ebooklib import epub
import markdown
from typing import Optional
from ..models.book import Book
from ..schemas.book import ExportOptions


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
        """Convert Markdown to HTML"""
        return markdown.markdown(
            markdown_text,
            extensions=['extra', 'codehilite', 'tables']
        )

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
        """Get default CSS for EPUB"""
        return """
        body {
            font-family: Georgia, serif;
            font-size: 1.1em;
            line-height: 1.6;
            text-align: justify;
            margin: 1em;
        }

        .title-page {
            text-align: center;
            margin-top: 30%;
        }

        .book-title {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 0.3em;
        }

        .subtitle {
            font-size: 1.5em;
            color: #666;
            margin-bottom: 1.5em;
        }

        .author {
            font-size: 1.2em;
            font-style: italic;
        }

        .copyright-page {
            margin-top: 50%;
            font-size: 0.9em;
            color: #666;
        }

        .chapter {
            margin: 2em 0;
        }

        .chapter h1 {
            font-size: 2em;
            margin-bottom: 1em;
            page-break-after: avoid;
        }

        h2 {
            font-size: 1.5em;
            margin: 1.5em 0 0.8em 0;
            page-break-after: avoid;
        }

        h3 {
            font-size: 1.2em;
            margin: 1.2em 0 0.6em 0;
            page-break-after: avoid;
        }

        p {
            margin: 0 0 0.8em 0;
            text-indent: 1.5em;
        }

        p:first-of-type,
        h1 + p,
        h2 + p,
        h3 + p {
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
        }

        pre {
            background: #f5f5f5;
            padding: 1em;
            overflow-x: auto;
        }
        """

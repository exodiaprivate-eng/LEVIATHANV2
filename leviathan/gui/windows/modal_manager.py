"""Modal/popup window management for PyWebView."""
import logging
import webview
from pathlib import Path

logger = logging.getLogger('leviathan.gui.modals')


class ModalManager:
    """Manage additional windows (settings, training, etc.)."""

    def __init__(self, api):
        self.api = api
        self.windows = {}
        self.frontend_dir = Path(__file__).parent.parent.parent / 'frontend'

    def open_modal(self, html_file: str, title: str, width: int = 800, height: int = 600):
        path = self.frontend_dir / html_file
        if not path.exists():
            logger.error(f"HTML file not found: {path}")
            return
        if html_file in self.windows:
            self.windows[html_file].show()
            return
        window = webview.create_window(
            title=title, url=str(path), js_api=self.api,
            width=width, height=height, background_color='#0a0a0f')
        self.windows[html_file] = window

    def close_modal(self, html_file: str):
        if html_file in self.windows:
            self.windows[html_file].destroy()
            del self.windows[html_file]

"""
Leviathan Trading Platform - PyWebView Application Launcher.

Initializes and launches the desktop GUI using pywebview,
bridging the Python backend to the HTML/JS frontend.
"""
import os
import sys
import webview

from leviathan.gui.api import LeviathanAPI


class LeviathanGUI:
    """Main GUI application using PyWebView."""

    def __init__(self, config, trading_engine=None, learning_db=None, state_db=None):
        self.config = config
        self.trading_engine = trading_engine
        self.learning_db = learning_db
        self.state_db = state_db
        self.window = None

        # Resolve path to frontend directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.frontend_dir = os.path.join(base_dir, 'frontend')
        self.index_path = os.path.join(self.frontend_dir, 'index.html')

        # Create API bridge
        self.api_bridge = LeviathanAPI(
            trading_engine=self.trading_engine,
            learning_db=self.learning_db,
            state_db=self.state_db,
        )

    def create_window(self):
        """Create the main PyWebView window."""
        self.window = webview.create_window(
            'Leviathan V2',
            url=self.index_path,
            width=1400,
            height=900,
            background_color='#0a0a0f',
            js_api=self.api_bridge,
            min_size=(1024, 600),
            frameless=True,
            easy_drag=False,
            resizable=True,
        )
        return self.window

    def start(self):
        """Create the window and start the webview event loop."""
        self.create_window()
        # Give the API bridge a reference to the window for min/max/close
        self.api_bridge._window = self.window
        debug = getattr(self.config, 'debug', False)
        webview.start(debug=debug)


if __name__ == '__main__':
    # Standalone entry point for development
    class _DevConfig:
        debug = True

    gui = LeviathanGUI(config=_DevConfig())
    gui.start()

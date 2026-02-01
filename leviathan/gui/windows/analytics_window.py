"""Analytics window navigation helper."""


class AnalyticsWindow:
    """Manages navigation to the analytics page."""

    def __init__(self, webview_window=None):
        self.window = webview_window

    def show(self):
        if self.window:
            self.window.load_url(self._get_url('analytics.html'))

    def _get_url(self, page):
        import os
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base, 'frontend', page)

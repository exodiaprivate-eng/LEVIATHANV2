"""News text processing for sentiment analysis."""
import re
import logging

logger = logging.getLogger('leviathan.news_processor')


class NewsProcessor:
    """Clean, filter, and prepare news text for FinBERT."""

    def clean_text(self, text: str) -> str:
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:512]

    def extract_relevant_sentences(self, text: str, symbol: str = '') -> str:
        sentences = text.split('.')
        relevant = [s.strip() for s in sentences if symbol.upper() in s.upper() or len(s) > 20]
        return '. '.join(relevant[:3])

    def deduplicate_news(self, news_items: list) -> list:
        seen = set()
        unique = []
        for item in news_items:
            headline = item.get('headline', item.get('title', ''))
            if headline not in seen:
                seen.add(headline)
                unique.append(item)
        return unique

    def process_news_batch(self, news_items: list, symbol: str = '') -> list:
        unique = self.deduplicate_news(news_items)
        processed = []
        for item in unique:
            headline = item.get('headline', item.get('title', ''))
            summary = item.get('summary', '')
            text = self.clean_text(f"{headline}. {summary}")
            if len(text) > 10:
                processed.append({**item, 'clean_text': text})
        return processed

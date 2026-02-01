"""Sentiment feature engineering - merge sentiment scores with price data."""
import logging
import pandas as pd
from datetime import datetime

logger = logging.getLogger('leviathan.features.sentiment')


class SentimentFeatureEngineer:
    """Create sentiment-based features for ML models."""

    def create_sentiment_features(self, sentiment_data: list) -> pd.DataFrame:
        """Convert raw sentiment data to feature DataFrame."""
        if not sentiment_data:
            return pd.DataFrame()
        df = pd.DataFrame(sentiment_data)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
        # Rolling averages
        if 'score' in df.columns:
            df['sentiment_ma_6h'] = df['score'].rolling('6h').mean()
            df['sentiment_ma_24h'] = df['score'].rolling('24h').mean()
            df['sentiment_std_24h'] = df['score'].rolling('24h').std()
            df['sentiment_momentum'] = df['score'] - df['sentiment_ma_24h']
        return df

    def merge_sentiment_with_price(self, price_df: pd.DataFrame,
                                    sentiment_df: pd.DataFrame) -> pd.DataFrame:
        """Merge sentiment features with price data using nearest timestamp."""
        if sentiment_df.empty:
            price_df['sentiment_score'] = 0.0
            return price_df
        merged = pd.merge_asof(
            price_df.sort_index(), sentiment_df.sort_index(),
            left_index=True, right_index=True, direction='backward'
        )
        return merged.fillna(0)

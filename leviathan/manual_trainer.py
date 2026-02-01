"""CLI for manual model retraining."""
import argparse
from data.storage.learning_db import LearningDatabase
from models.training.trainer import ModelTrainer
from models.training.auto_trainer import AutoTrainer


def main():
    parser = argparse.ArgumentParser(description='Leviathan Manual Trainer')
    parser.add_argument('--model', choices=['lstm', 'lgbm', 'nbeats', 'all'], default='all')
    parser.add_argument('--lookback', type=int, default=365, help='Days of data')
    args = parser.parse_args()

    db = LearningDatabase()
    trainer = ModelTrainer()
    auto = AutoTrainer(db, trainer)

    print(f"Starting manual retrain: model={args.model}, lookback={args.lookback} days")
    auto.manual_retrain(lookback_days=args.lookback, specific_model=args.model if args.model != 'all' else None)
    print("Training complete.")


if __name__ == "__main__":
    main()

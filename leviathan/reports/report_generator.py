"""PDF report generation using reportlab."""
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger('leviathan.reports')

REPORTS_DIR = Path(__file__).parent / 'generated'
REPORTS_DIR.mkdir(exist_ok=True)

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
    )
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    logger.warning("reportlab not installed - PDF reports unavailable, falling back to text")


# Theme colors
DARK_BG = colors.HexColor('#1a1a2e')
ACCENT = colors.HexColor('#7c3aed')
GREEN = colors.HexColor('#10b981')
RED = colors.HexColor('#ef4444')
GRAY = colors.HexColor('#6b7280')
WHITE = colors.white


class ReportGenerator:
    """Generate trading performance PDF reports."""

    def generate_daily_report(self, stats: dict, trades: Optional[List[dict]] = None) -> str:
        """Generate daily performance PDF report."""
        date_str = datetime.now().strftime('%Y%m%d')
        filename = f"daily_{date_str}.pdf"
        path = REPORTS_DIR / filename

        if not HAS_REPORTLAB:
            return self._fallback_text_report(path.with_suffix('.txt'), stats, trades)

        doc = SimpleDocTemplate(str(path), pagesize=letter,
                                topMargin=0.5 * inch, bottomMargin=0.5 * inch)
        styles = getSampleStyleSheet()
        elements = []

        # Header
        elements.append(self._make_header(
            f"LEVIATHAN Daily Report",
            datetime.now().strftime('%A, %B %d, %Y')
        ))
        elements.append(Spacer(1, 12))

        # Metrics table
        elements.append(self._make_metrics_table(stats))
        elements.append(Spacer(1, 20))

        # Trades table
        if trades:
            elements.append(Paragraph("Trade Log", styles['Heading2']))
            elements.append(Spacer(1, 8))
            elements.append(self._make_trades_table(trades))

        doc.build(elements)
        logger.info("Daily PDF report saved: %s", path)
        return str(path)

    def generate_weekly_report(self, weekly_data: dict) -> str:
        """Generate weekly summary PDF report."""
        date_str = datetime.now().strftime('%Y%m%d')
        filename = f"weekly_{date_str}.pdf"
        path = REPORTS_DIR / filename

        if not HAS_REPORTLAB:
            return self._fallback_text_report(path.with_suffix('.txt'), weekly_data)

        doc = SimpleDocTemplate(str(path), pagesize=letter,
                                topMargin=0.5 * inch, bottomMargin=0.5 * inch)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(self._make_header(
            "LEVIATHAN Weekly Report",
            f"Week ending {datetime.now().strftime('%B %d, %Y')}"
        ))
        elements.append(Spacer(1, 12))

        # Weekly stats
        stats = {
            'Total P&L': f"${weekly_data.get('total_pnl', 0):.2f}",
            'Total Trades': str(weekly_data.get('total_trades', 0)),
            'Win Rate': f"{weekly_data.get('win_rate', 0):.1%}",
            'Best Day': f"${weekly_data.get('best_day_pnl', 0):.2f}",
            'Worst Day': f"${weekly_data.get('worst_day_pnl', 0):.2f}",
            'Sharpe Ratio': f"{weekly_data.get('sharpe', 0):.2f}",
            'Max Drawdown': f"{weekly_data.get('max_drawdown', 0):.1%}",
            'Opus Accuracy': f"{weekly_data.get('opus_accuracy', 0):.1%}",
        }
        elements.append(self._make_metrics_table(stats))

        doc.build(elements)
        logger.info("Weekly PDF report saved: %s", path)
        return str(path)

    def generate_monthly_report(self, stats: dict) -> str:
        """Generate monthly PDF report."""
        date_str = datetime.now().strftime('%Y%m')
        path = REPORTS_DIR / f"monthly_{date_str}.pdf"

        if not HAS_REPORTLAB:
            return self._fallback_text_report(path.with_suffix('.txt'), stats)

        doc = SimpleDocTemplate(str(path), pagesize=letter)
        elements = []
        elements.append(self._make_header(
            "LEVIATHAN Monthly Report",
            datetime.now().strftime('%B %Y')
        ))
        elements.append(Spacer(1, 12))
        elements.append(self._make_metrics_table(stats))
        doc.build(elements)
        logger.info("Monthly PDF report saved: %s", path)
        return str(path)

    def _make_header(self, title: str, subtitle: str) -> Table:
        """Create report header."""
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ReportTitle', parent=styles['Title'],
            fontSize=22, textColor=ACCENT, spaceAfter=4,
        )
        sub_style = ParagraphStyle(
            'ReportSub', parent=styles['Normal'],
            fontSize=11, textColor=GRAY,
        )
        data = [
            [Paragraph(title, title_style)],
            [Paragraph(subtitle, sub_style)],
        ]
        t = Table(data, colWidths=[6.5 * inch])
        t.setStyle(TableStyle([
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LINEBELOW', (0, -1), (-1, -1), 1, ACCENT),
        ]))
        return t

    def _make_metrics_table(self, stats: dict) -> Table:
        """Create metrics summary table."""
        # Format stats dict for display
        if all(isinstance(v, str) for v in stats.values()):
            display_stats = stats
        else:
            display_stats = {
                'P&L': f"${stats.get('pnl', 0):.2f}" if isinstance(stats.get('pnl'), (int, float)) else str(stats.get('pnl', 'N/A')),
                'Trades': str(stats.get('trades', 0)),
                'Win Rate': f"{stats.get('win_rate', 0):.1%}" if isinstance(stats.get('win_rate'), (int, float)) else str(stats.get('win_rate', 'N/A')),
                'Opus Decisions': str(stats.get('decisions', 0)),
                'API Cost': f"${stats.get('api_cost', 0):.2f}" if isinstance(stats.get('api_cost'), (int, float)) else str(stats.get('api_cost', 'N/A')),
            }

        data = [['Metric', 'Value']]
        for k, v in display_stats.items():
            data.append([str(k), str(v)])

        t = Table(data, colWidths=[3 * inch, 3.5 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), ACCENT),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f3f4f6'), WHITE]),
            ('GRID', (0, 0), (-1, -1), 0.5, GRAY),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        return t

    def _make_trades_table(self, trades: List[dict]) -> Table:
        """Create trades log table."""
        data = [['Time', 'Symbol', 'Side', 'Qty', 'Price', 'P&L']]
        for t in trades[:50]:  # Max 50 trades per report
            pnl = t.get('pnl', 0)
            data.append([
                t.get('time', ''),
                t.get('symbol', ''),
                t.get('side', ''),
                str(t.get('qty', 0)),
                f"${t.get('price', 0):.2f}",
                f"${pnl:.2f}",
            ])

        table = Table(data, colWidths=[1.2 * inch, 0.8 * inch, 0.6 * inch,
                                        0.6 * inch, 1 * inch, 1 * inch])
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), ACCENT),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, GRAY),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f3f4f6'), WHITE]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]
        # Color P&L column
        for i in range(1, len(data)):
            pnl = trades[i - 1].get('pnl', 0)
            if pnl > 0:
                style.append(('TEXTCOLOR', (5, i), (5, i), GREEN))
            elif pnl < 0:
                style.append(('TEXTCOLOR', (5, i), (5, i), RED))

        table.setStyle(TableStyle(style))
        return table

    def _fallback_text_report(self, path, stats, trades=None) -> str:
        """Fallback text report when reportlab is unavailable."""
        path = Path(str(path))
        lines = [
            f"LEVIATHAN Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 50,
        ]
        for k, v in stats.items():
            lines.append(f"  {k}: {v}")
        if trades:
            lines.append("\nTrades:")
            for t in trades[:50]:
                lines.append(f"  {t.get('symbol', '')} {t.get('side', '')} "
                             f"x{t.get('qty', 0)} @ ${t.get('price', 0):.2f} "
                             f"P&L=${t.get('pnl', 0):.2f}")
        path.write_text('\n'.join(lines))
        logger.info("Text report saved (reportlab unavailable): %s", path)
        return str(path)

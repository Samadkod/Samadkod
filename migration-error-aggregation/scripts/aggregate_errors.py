#!/usr/bin/env python3
"""
Migration Error Aggregation Tool
Aggregates and tracks migration validation errors by week
Focus: Blocking errors (Criticite = "Error") only
"""

import os
import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Set

class MigrationErrorAggregator:
    """Aggregates migration validation errors and tracks resolution progress"""

    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.raw_dir = self.base_dir / "data" / "raw"
        self.processed_dir = self.base_dir / "data" / "processed"
        self.history_dir = self.base_dir / "data" / "history"

        # Create directories if they don't exist
        for d in [self.raw_dir, self.processed_dir, self.history_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def parse_tsv_file(self, filepath: str) -> List[Dict]:
        """Parse TSV error file from SSM export"""
        errors = []
        encodings = ['utf-16', 'utf-8-sig', 'utf-8', 'latin-1', 'cp1252']

        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    reader = csv.DictReader(f, delimiter='\t')
                    for row in reader:
                        # Only keep blocking errors (Criticite = "Error")
                        if row.get('Criticite', '').strip() == 'Error':
                            errors.append({
                                'groupe': row.get('Groupe', '').strip(),
                                'code_site': row.get('CodeSite', '').strip(),
                                'scope': row.get('Scope', '').strip(),
                                'error_id': row.get('Id', '').strip(),
                                'message': row.get('Message', '').strip(),
                                'criticite': row.get('Criticite', '').strip(),
                                'nb_occurrence': int(row.get('NbOccurrence', '0').strip() or 0),
                            })
                print(f"✓ Successfully parsed with {encoding} encoding")
                return errors
            except Exception as e:
                continue

        print(f"Error parsing file {filepath}: Could not determine encoding")
        return []

    def aggregate_errors(self, errors: List[Dict]) -> Dict:
        """Aggregate errors by error type (scope + id + message)"""
        aggregated = defaultdict(lambda: {
            'scope': '',
            'error_id': '',
            'message': '',
            'sites_affected': set(),
            'total_occurrences': 0,
            'criticite': 'Error'
        })

        for error in errors:
            error_key = f"{error['error_id']}_{error['message']}"

            agg = aggregated[error_key]
            agg['scope'] = error['scope']
            agg['error_id'] = error['error_id']
            agg['message'] = error['message']
            agg['sites_affected'].add(error['code_site'])
            agg['total_occurrences'] += error['nb_occurrence']

        # Convert sets to lists for JSON serialization
        return {
            k: {
                **v,
                'sites_affected': sorted(list(v['sites_affected'])),
                'num_sites': len(v['sites_affected'])
            }
            for k, v in aggregated.items()
        }

    def load_historical_data(self) -> Dict:
        """Load historical data from previous weeks"""
        history_file = self.history_dir / "error_history.json"
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_historical_data(self, history: Dict):
        """Save historical data"""
        history_file = self.history_dir / "error_history.json"
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def detect_resolved_sites(self, current_sites: Set[str], historical_sites: Set[str]) -> Set[str]:
        """Identify sites that were in error but are no longer present (resolved)"""
        return historical_sites - current_sites

    def process_weekly_export(self, csv_filepath: str, week_identifier: str = None) -> Dict:
        """
        Process a weekly error export

        Args:
            csv_filepath: Path to the SSM export CSV file
            week_identifier: Optional week identifier (e.g., "2024-W33", defaults to current date)

        Returns:
            Dictionary with aggregation results and statistics
        """
        if week_identifier is None:
            week_identifier = datetime.now().strftime("%Y-W%V")

        print(f"\n{'='*60}")
        print(f"Processing weekly export: {week_identifier}")
        print(f"File: {csv_filepath}")
        print(f"{'='*60}\n")

        # Parse CSV
        raw_errors = self.parse_tsv_file(csv_filepath)
        if not raw_errors:
            print("❌ No blocking errors found in file")
            return {}

        print(f"✅ Found {len(raw_errors)} blocking error records")

        # Aggregate errors
        aggregated = self.aggregate_errors(raw_errors)
        print(f"✅ Aggregated into {len(aggregated)} error types")

        # Get all currently affected sites
        current_affected_sites = set()
        for error_data in aggregated.values():
            current_affected_sites.update(error_data['sites_affected'])

        print(f"✅ Sites affected: {len(current_affected_sites)}")

        # Load historical data
        history = self.load_historical_data()

        # Detect resolved sites (only for errors that previously existed)
        resolved_sites = set()
        if week_identifier in history:
            previous_sites = set()
            for error_key, error_data in history[week_identifier].get('aggregated_errors', {}).items():
                previous_sites.update(error_data.get('sites_affected', []))
            resolved_sites = self.detect_resolved_sites(current_affected_sites, previous_sites)

        if resolved_sites:
            print(f"✅ Resolved sites this week: {len(resolved_sites)}")
            print(f"   Sites: {', '.join(sorted(resolved_sites))}")

        # Save current week data
        week_data = {
            'week': week_identifier,
            'processed_date': datetime.now().isoformat(),
            'source_file': Path(csv_filepath).name,
            'total_blocking_errors': len(raw_errors),
            'unique_error_types': len(aggregated),
            'affected_sites': sorted(list(current_affected_sites)),
            'num_affected_sites': len(current_affected_sites),
            'resolved_sites': sorted(list(resolved_sites)),
            'num_resolved': len(resolved_sites),
            'aggregated_errors': aggregated
        }

        # Update history
        history[week_identifier] = week_data
        self.save_historical_data(history)

        # Save this week's processed data as CSV for Power BI
        self.save_weekly_csv(week_data)

        return week_data

    def save_weekly_csv(self, week_data: Dict):
        """Save aggregated data as CSV for Power BI import"""
        week = week_data['week']
        csv_path = self.processed_dir / f"errors_{week}.csv"

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Week', 'ErrorType', 'Scope', 'ErrorID', 'Message',
                'AffectedSites', 'NumSites', 'TotalOccurrences'
            ])

            for error_key, error_data in week_data['aggregated_errors'].items():
                writer.writerow([
                    week,
                    error_key,
                    error_data['scope'],
                    error_data['error_id'],
                    error_data['message'],
                    ';'.join(error_data['sites_affected']),
                    error_data['num_sites'],
                    error_data['total_occurrences']
                ])

        print(f"\n💾 Saved to: {csv_path}")

    def generate_summary_report(self) -> str:
        """Generate a summary report of all weeks"""
        history = self.load_historical_data()

        if not history:
            return "No historical data found"

        report = []
        report.append("\n" + "="*80)
        report.append("MIGRATION ERROR AGGREGATION SUMMARY REPORT")
        report.append("="*80 + "\n")

        total_resolved = 0
        total_sites_affected = 0

        for week in sorted(history.keys()):
            week_data = history[week]
            num_resolved = len(week_data.get('resolved_sites', []))
            num_affected = week_data['num_affected_sites']

            total_resolved += num_resolved
            total_sites_affected = max(total_sites_affected, num_affected)

            report.append(f"Week: {week}")
            report.append(f"  • Error types: {week_data['unique_error_types']}")
            report.append(f"  • Sites affected: {num_affected}")
            report.append(f"  • Resolved this week: {num_resolved}")
            report.append(f"  • Processed: {week_data['processed_date'][:10]}")
            report.append("")

        report.append("-" * 80)
        report.append(f"Total sites resolved (cumulative): {total_resolved}")
        report.append(f"Max sites affected in any week: {total_sites_affected}")
        report.append("="*80 + "\n")

        return "\n".join(report)


def main():
    # Get the script's directory
    script_dir = Path(__file__).parent.parent

    aggregator = MigrationErrorAggregator(script_dir)

    # Example: Process the uploaded file
    raw_file = "/root/.claude/uploads/d2de2eb8-3b74-55d4-b50e-02fb42408d97/4b2c4fdc-erreursvalidationEST_1.txt"

    if os.path.exists(raw_file):
        result = aggregator.process_weekly_export(raw_file, week_identifier="2024-W33")

        # Print summary
        print(aggregator.generate_summary_report())

        # Print top errors
        if result and 'aggregated_errors' in result:
            print("\nTOP 10 BLOCKING ERRORS BY AFFECTED SITES:\n")
            sorted_errors = sorted(
                result['aggregated_errors'].items(),
                key=lambda x: x[1]['num_sites'],
                reverse=True
            )

            for i, (error_key, error_data) in enumerate(sorted_errors[:10], 1):
                print(f"{i}. [{error_data['scope']}] Error {error_data['error_id']}")
                print(f"   Message: {error_data['message']}")
                print(f"   Affected sites: {error_data['num_sites']}")
                print(f"   Total occurrences: {error_data['total_occurrences']}")
                print()
    else:
        print(f"File not found: {raw_file}")


if __name__ == "__main__":
    main()

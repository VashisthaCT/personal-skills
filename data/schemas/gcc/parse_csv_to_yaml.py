#!/usr/bin/env python3
"""
Parse Metabase column-metadata CSV → YAML schema file.

Auto-detects CSV format:
  - Postgres: information_schema.columns export
    (table_schema, table_name, column_name, data_type, ordinal_position, is_nullable, column_default)
  - ClickHouse: system.columns export
    (database, table, column_name, type, comment, position, is_in_primary_key, is_in_partition_key)

Usage:
  parse_csv_to_yaml.py <csv_path> <out_yaml_path> <db_name> <engine>
"""

import csv
import sys
from collections import defaultdict
from datetime import date


def needs_yaml_quote(s: str) -> bool:
    if not s:
        return True
    if s[0] not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_':
        return True
    return any(c in s for c in ' :{}[]()&*?|<>=!%@`#"\'\t\n')


def yaml_key(s: str) -> str:
    return f'"{s}"' if needs_yaml_quote(s) else s


def yaml_value(s: str) -> str:
    """Quote types that contain special chars (e.g. Nullable(UUID), Array(String))."""
    if needs_yaml_quote(s):
        return f'"{s}"'
    return s


def detect_format(header):
    h = set(header)
    if 'table_schema' in h and 'data_type' in h:
        return 'postgres'
    if 'database' in h and 'is_in_primary_key' in h:
        return 'clickhouse'
    raise ValueError(f'Unknown CSV format. Header: {header}')


def normalize_row(row, fmt):
    """Map engine-specific CSV row → normalized dict."""
    if fmt == 'postgres':
        return {
            'table': row['table_name'],
            'column': row['column_name'],
            'type': row['data_type'],
            'position': int(row['ordinal_position']),
            'nullable': row.get('is_nullable', '').strip() != 'NO',
            'default': row.get('column_default', '').strip(),
            'pk': False,
            'partition_key': False,
        }
    elif fmt == 'clickhouse':
        return {
            'table': row['table'],
            'column': row['column_name'],
            'type': row['type'],
            'position': int(row['position']),
            'nullable': row['type'].startswith('Nullable('),
            'default': '',  # ClickHouse defaults aren't in this query; could be added
            'pk': row.get('is_in_primary_key', '0') == '1',
            'partition_key': row.get('is_in_partition_key', '0') == '1',
            'comment': row.get('comment', '').strip(),
        }


def main():
    if len(sys.argv) != 5:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    csv_path, out_path, db_name, engine = sys.argv[1:5]

    with open(csv_path) as f:
        reader = csv.DictReader(f)
        fmt = detect_format(reader.fieldnames)
        tables = defaultdict(list)
        for row in reader:
            n = normalize_row(row, fmt)
            tables[n['table']].append(n)

    sorted_tables = sorted(tables.items())
    total_cols = sum(len(cols) for _, cols in sorted_tables)

    with open(out_path, 'w') as f:
        f.write(f'# {db_name} — schema dump\n')
        f.write(f'# Engine: {engine}\n')
        f.write(f'# Source: OCI Metabase ({fmt} system catalog)\n')
        f.write(f'# Tables: {len(sorted_tables)}\n')
        f.write(f'# Total columns: {total_cols}\n')
        f.write(f'# Last extracted: {date.today().isoformat()}\n')
        f.write(f'#\n')
        f.write(f'# Per-table column maps. Tier classification, JOIN keys,\n')
        f.write(f'# and enum values live in companion files (relationships.md, gotchas.md,\n')
        f.write(f'# query_patterns.yaml).\n\n')
        f.write(f'database: {db_name}\n')
        f.write(f'engine: {engine}\n')
        f.write(f'tables:\n')

        for table_name, cols in sorted_tables:
            cols_sorted = sorted(cols, key=lambda c: c['position'])
            f.write(f'  {yaml_key(table_name)}:\n')
            # Mark partition keys / primary keys at table level (CH only)
            pk_cols = [c['column'] for c in cols_sorted if c.get('pk')]
            part_cols = [c['column'] for c in cols_sorted if c.get('partition_key')]
            if pk_cols:
                f.write(f'    primary_key: [{", ".join(yaml_key(c) for c in pk_cols)}]\n')
            if part_cols:
                f.write(f'    partition_key: [{", ".join(yaml_key(c) for c in part_cols)}]\n')
            f.write(f'    columns:\n')
            for col in cols_sorted:
                col_name = yaml_key(col['column'])
                col_type = yaml_value(col['type'])
                # Compact form for vanilla columns
                has_extra = bool(col['default']) or col.get('comment')
                if has_extra:
                    f.write(f'      {col_name}:\n')
                    f.write(f'        type: {col_type}\n')
                    if col['default']:
                        default_esc = col['default'].replace("'", "''")
                        f.write(f"        default: '{default_esc}'\n")
                    if col.get('comment'):
                        comment_esc = col['comment'].replace('"', '\\"')
                        f.write(f'        comment: "{comment_esc}"\n')
                else:
                    f.write(f'      {col_name}: {col_type}\n')

    print(f'Wrote {out_path}: {len(sorted_tables)} tables, {total_cols} columns ({fmt} format)')


if __name__ == '__main__':
    main()

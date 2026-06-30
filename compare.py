import duckdb
import re
from database import get_table_name

def clean_column_name(name):
    """Normalizes column names to Title Case (e.g., 'firstName' -> 'First Name')."""
    name = str(name)
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name) 
    words = re.split(r'[\s_\-]+', name)              
    return ' '.join(w.capitalize() for w in words if w)

def get_common_columns(dsn1, dsn2):
    """Helper to fetch common columns for the setup UI."""
    tb1, _ = get_table_name(dsn1)
    tb2, _ = get_table_name(dsn2)
    
    con = duckdb.connect()
    con.execute("INSTALL odbc; LOAD odbc;")
    
    con.execute(f"CREATE VIEW t1_raw AS SELECT * FROM odbc_query('DSN={dsn1};', 'SELECT * FROM [{tb1}]')")
    con.execute(f"CREATE VIEW t2_raw AS SELECT * FROM odbc_query('DSN={dsn2};', 'SELECT * FROM [{tb2}]')")
    
    cols1 = [c[0] for c in con.execute("DESCRIBE t1_raw").fetchall()]
    cols2 = [c[0] for c in con.execute("DESCRIBE t2_raw").fetchall()]
    
    cols1_clean = [clean_column_name(c) for c in cols1]
    cols2_clean = [clean_column_name(c) for c in cols2]
    
    return [c for c in cols1_clean if c in cols2_clean]

def run_duckdb_comparison(dsn1, dsn2, id_cols: list):
    print(f"Discovering tables for '{dsn1}' and '{dsn2}'...")
    tb1, file1 = get_table_name(dsn1)
    tb2, file2 = get_table_name(dsn2)

    print('Initializing DuckDB and ODBC extension...')
    con = duckdb.connect()
    con.execute("INSTALL odbc; LOAD odbc;")

    print('Registering views...')
    con.execute(f"CREATE VIEW t1_raw AS SELECT * FROM odbc_query('DSN={dsn1};', 'SELECT * FROM [{tb1}]')")
    con.execute(f"CREATE VIEW t2_raw AS SELECT * FROM odbc_query('DSN={dsn2};', 'SELECT * FROM [{tb2}]')")

    cols1_raw = con.execute("DESCRIBE t1_raw").fetchall()
    cols2_raw = con.execute("DESCRIBE t2_raw").fetchall()
    cols1 = [c[0] for c in cols1_raw]
    cols2 = [c[0] for c in cols2_raw]
    
    count1 = con.execute("SELECT COUNT(*) FROM t1_raw").fetchone()[0]
    count2 = con.execute("SELECT COUNT(*) FROM t2_raw").fetchone()[0]

    sel1 = ", ".join([f'"{c}" AS "{clean_column_name(c)}"' for c in cols1])
    sel2 = ", ".join([f'"{c}" AS "{clean_column_name(c)}"' for c in cols2])

    con.execute(f"CREATE VIEW t1 AS SELECT {sel1} FROM t1_raw")
    con.execute(f"CREATE VIEW t2 AS SELECT {sel2} FROM t2_raw")

    cols1_clean = [clean_column_name(c) for c in cols1]
    cols2_clean = [clean_column_name(c) for c in cols2]

    # Validate id_cols
    for id_col in id_cols:
        if id_col not in cols1_clean or id_col not in cols2_clean:
            raise ValueError(f"Column '{id_col}' is not present in both files.")

    data_columns = [c for c in cols1_clean if c in cols2_clean and c not in id_cols]
    src_only_columns = [c for c in cols1_clean if c not in cols2_clean and c not in id_cols] 
    dstn_only_columns = [c for c in cols2_clean if c not in cols1_clean and c not in id_cols]

    # Fetch types to handle numeric vs string comparisons correctly
    types1 = {r[0]: r[1] for r in con.execute("DESCRIBE t1").fetchall()}
    types2 = {r[0]: r[1] for r in con.execute("DESCRIBE t2").fetchall()}

    print('Building dynamic comparison query...')
    
    # Composite key helpers
    id_display_parts = [f"REGEXP_REPLACE(COALESCE(CAST(t1.\"{col}\" AS VARCHAR), CAST(t2.\"{col}\" AS VARCHAR), ''), '[.]0$', '')" for col in id_cols]
    id_display_expr = f"CONCAT_WS(' - ', {', '.join(id_display_parts)})"
    
    is_comparable_expr = " AND ".join([f'(t1."{col}" IS NOT NULL AND t2."{col}" IS NOT NULL)' for col in id_cols])
    
    src_only_expr_part1 = " AND ".join([f't1."{col}" IS NOT NULL' for col in id_cols])
    src_only_expr_part2 = " OR ".join([f't2."{col}" IS NULL' for col in id_cols])
    is_src_only_expr = f"({src_only_expr_part1}) AND ({src_only_expr_part2})"
    
    dstn_only_expr_part1 = " AND ".join([f't2."{col}" IS NOT NULL' for col in id_cols])
    dstn_only_expr_part2 = " OR ".join([f't1."{col}" IS NULL' for col in id_cols])
    is_dstn_only_expr = f"({dstn_only_expr_part1}) AND ({dstn_only_expr_part2})"
    
    join_cond_expr = " AND ".join([f't1."{col}" = t2."{col}"' for col in id_cols])
    any_id_null_expr = " OR ".join([f'(t1."{col}" IS NULL OR t2."{col}" IS NULL)' for col in id_cols])
    all_id_not_null_expr = " AND ".join([f'(t1."{col}" IS NOT NULL AND t2."{col}" IS NOT NULL)' for col in id_cols])
    
    select_parts = [
        f"{id_display_expr} AS id_display",
        f"({is_comparable_expr}) AS is_comparable",
        f"({is_src_only_expr}) AS is_src_only",
        f"({is_dstn_only_expr}) AS is_dstn_only"
    ]

    has_nan_parts = []
    has_mismatch_parts = []

    for col in data_columns:
        # Mismatch checking types
        type1, type2 = types1.get(col, 'VARCHAR'), types2.get(col, 'VARCHAR')
        num_types = ['TINYINT', 'SMALLINT', 'INTEGER', 'BIGINT', 'HUGEINT', 'FLOAT', 'DOUBLE', 'DECIMAL']
        is_num = any(t in type1 for t in num_types) and any(t in type2 for t in num_types)

        # Fetch formatted values
        if is_num:
            select_parts.append(f'''
                CASE 
                    WHEN t1."{col}" IS NULL THEN ''
                    WHEN ROUND(CAST(t1."{col}" AS DOUBLE), 0) = CAST(t1."{col}" AS DOUBLE) 
                         THEN CAST(CAST(t1."{col}" AS BIGINT) AS VARCHAR)
                    ELSE printf('%.2f', CAST(t1."{col}" AS DOUBLE))
                END AS "{col}_1"
            ''')
            select_parts.append(f'''
                CASE 
                    WHEN t2."{col}" IS NULL THEN ''
                    WHEN ROUND(CAST(t2."{col}" AS DOUBLE), 0) = CAST(t2."{col}" AS DOUBLE) 
                         THEN CAST(CAST(t2."{col}" AS BIGINT) AS VARCHAR)
                    ELSE printf('%.2f', CAST(t2."{col}" AS DOUBLE))
                END AS "{col}_2"
            ''')
        else:
            select_parts.append(f'COALESCE(CAST(t1."{col}" AS VARCHAR), \'\') AS "{col}_1"')
            select_parts.append(f'COALESCE(CAST(t2."{col}" AS VARCHAR), \'\') AS "{col}_2"')

        # NaN checking
        nan_check = f'((t1."{col}" IS NULL) != (t2."{col}" IS NULL)) AND ({all_id_not_null_expr})'
        select_parts.append(f'{nan_check} AS "{col}_nan"')
        has_nan_parts.append(nan_check)


        if is_num:
            # Numeric comparison with tolerance
            diff_check = f'ABS(t1."{col}" - t2."{col}") > 1e-08 + 1e-05 * ABS(t2."{col}")'
        else:
            # String comparison
            diff_check = f'LOWER(TRIM(CAST(t1."{col}" AS VARCHAR))) != LOWER(TRIM(CAST(t2."{col}" AS VARCHAR)))'

        mismatch_expr = f'''
            ({any_id_null_expr}) OR
            ({nan_check}) OR 
            (t1."{col}" IS NOT NULL AND t2."{col}" IS NOT NULL AND {diff_check})
        '''
        select_parts.append(f'({mismatch_expr}) AS "{col}_mismatch"')
        has_mismatch_parts.append(f'({mismatch_expr})')

    for col in src_only_columns:
        select_parts.append(f'COALESCE(CAST(t1."{col}" AS VARCHAR), \'\') AS "{col}_src_only"')

    for col in dstn_only_columns:
        select_parts.append(f'COALESCE(CAST(t2."{col}" AS VARCHAR), \'\') AS "{col}_dstn_only"')

    select_parts.append(f"({' OR '.join(has_nan_parts) if has_nan_parts else 'FALSE'}) AS has_nan")
    select_parts.append(f"({' OR '.join(has_mismatch_parts) if has_mismatch_parts else 'FALSE'}) AS has_mismatch")

    query = f"""
        SELECT {', '.join(select_parts)}
        FROM t1
        FULL OUTER JOIN t2 ON {join_cond_expr}
        ORDER BY is_comparable DESC, id_display
    """

    print('Executing query...')
    result_rel = con.execute(query)
    columns = [desc[0] for desc in result_rel.description]
    rows = result_rel.fetchall()

    # Convert fetched rows into a list of dictionaries
    records = []
    for row in rows:
        records.append(dict(zip(columns, row)))

    # Process lists
    missing_rows = [r for r in records if r['has_nan'] and r['is_comparable']]
    mismatched_rows = [r for r in records if r['has_mismatch'] and not r['has_nan'] and r['is_comparable']]
    matched_rows = [r for r in records if not r['has_nan'] and not r['has_mismatch'] and r['is_comparable']]

    # Aggregations for report
    mismatches_by_column = {}
    completeness_combined = []
    column_stats = {}

    for col in data_columns:
        matched = 0
        mismatched = 0
        missing = 0

        for r in records:
            if not r['is_comparable']: continue

            if r[f"{col}_1"] == '' or r[f"{col}_2"] == '':
                missing += 1
            elif r.get(f"{col}_mismatch"):
                mismatched += 1
            else:
                matched += 1

        column_stats[col] = {
            'matched': matched,
            'mismatched': mismatched,
            'missing': missing
        }


        mismatches_by_column[col] = sum(1 for r in records if r.get(f"{col}_mismatch") and r['is_comparable'])
        missing_count = sum(1 for r in records if (r[f"{col}_1"] == '' or r[f"{col}_2"] == '') and r['is_comparable'])
        completeness_combined.append(missing_count)

    return {
        'id_col_name': " - ".join(id_cols),
        'total_intersection': sum(1 for r in records if r['is_comparable']),
        'src_only_count': sum(1 for r in records if r.get('is_src_only')),
        'dstn_only_count': sum(1 for r in records if r.get('is_dstn_only')),
        'total_mismatches': len(mismatched_rows),
        'total_rows_with_nan': len(missing_rows),
        'total_rows_matched': len(matched_rows),
        'total_rows_mismatched': len(mismatched_rows),
        'data_columns': data_columns,
        'src_only_columns': src_only_columns,
        'dstn_only_columns': dstn_only_columns,
        'comparison_data': records,
        'mismatched_data': mismatched_rows,
        'missing_value_rows': missing_rows,
        'matched_data': matched_rows,
        'mismatches_by_column': mismatches_by_column,
        'completeness_combined': completeness_combined,
        'column_stats': column_stats,
        'tb1': tb1,
        'tb2': tb2,
        'file1': file1,
        'file2': file2,
        'cols1_len': len(cols1),
        'cols2_len': len(cols2),
        'count1': count1,
        'count2': count2
    }

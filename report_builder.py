import json
from datetime import datetime
from fastapi import Request

def build_template_context(request: Request, results: dict, src_dsn: str, dstn_dsn: str, execution_time: float) -> dict:
    report_data_dict = {
        'totalIntersection': results['total_intersection'],
        'srcOnlyCount': results['src_only_count'],
        'dstnOnlyCount': results['dstn_only_count'],
        'totalMatched': results['total_intersection'] - results['total_mismatches'],
        'totalMismatched': results['total_mismatches'],
        'totalCleanRows': results['total_intersection'] - results['total_rows_with_nan'],
        'totalMissingRows': results['total_rows_with_nan'],
        'columnMismatchLabels': list(results['mismatches_by_column'].keys()),
        'columnMismatchValues': list(results['mismatches_by_column'].values()),
        'completenessLabels': results['data_columns'],
        'completenessCombined': results['completeness_combined'],
        'dataColumns': results['data_columns'],
        'srcOnlyColumns': results['src_only_columns'],
        'dstnOnlyColumns': results['dstn_only_columns'],
        'id_col_name': results['id_col_name'],
        'tableData': {
            'sub-all': results['comparison_data'],
            'sub-comparable': [r for r in results['comparison_data'] if r.get('is_comparable')],
            'sub-non-comparable-records': [r for r in results['comparison_data'] if r.get('is_src_only') or r.get('is_dstn_only')],
            'sub-non-comparable-columns': results['comparison_data'],
            'sub-matched': results['matched_data'],
            'sub-mismatched': results['mismatched_data'],
            'sub-missing': results['missing_value_rows']
        }
    }
    
    report_json_str = json.dumps(report_data_dict).replace("\\", "\\\\").replace("'", "\\'")

    context = {
        "request": request,
        "id_col_name": results['id_col_name'],
        "total_intersection": results['total_intersection'],
        "total_mismatches": results['total_mismatches'],
        "total_rows_with_nan": results['total_rows_with_nan'],
        "total_columns": len(results['data_columns']),
        "data_columns": results['data_columns'],
        "comparison_data": results['comparison_data'],
        "mismatched_data": results['mismatched_data'],
        "missing_value_rows": results['missing_value_rows'],
        "matched_data": results['matched_data'],
        "column_mismatch_labels": list(results['mismatches_by_column'].keys()),
        "column_mismatch_values": list(results['mismatches_by_column'].values()),
        "completeness_labels": results['data_columns'],
        "completeness_combined": results['completeness_combined'],
        "report_json": report_json_str,
        "column_stats": results['column_stats'],
        "dsn1": src_dsn,
        "dsn2": dstn_dsn,
        "tb1": results.get('tb1'),
        "tb2": results.get('tb2'),
        "file1": results.get('file1'),
        "file2": results.get('file2'),
        "cols1_len": results.get('cols1_len'),
        "cols2_len": results.get('cols2_len'),
        "count1": results.get('count1'),
        "count2": results.get('count2'),
        "src_only_columns": results.get('src_only_columns', []),
        "dstn_only_columns": results.get('dstn_only_columns', []),
        "src_only_count": results.get('src_only_count', 0),
        "dstn_only_count": results.get('dstn_only_count', 0),
        "generation_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        "execution_time": execution_time
    }
    return context

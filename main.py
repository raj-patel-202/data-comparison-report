import os
import json
import webbrowser
import time
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from compare import run_duckdb_comparison, get_common_columns
import uvicorn

load_dotenv()

app = FastAPI(title="Data Comparison Report")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_dsns():
    src_dsn = os.environ.get('SOURCE_DSN')
    dstn_dsn = os.environ.get('DESTINATION_DSN')
    if not src_dsn or not dstn_dsn:
        raise ValueError("SOURCE_DSN and DESTINATION_DSN must be set in the environment variables")
    return src_dsn, dstn_dsn

@app.get("/", response_class=HTMLResponse)
async def setup_page(request: Request):
    try:
        src_dsn, dstn_dsn = get_dsns()
        common_cols = get_common_columns(src_dsn, dstn_dsn)
        return templates.TemplateResponse(
            request=request,
            name="setup_template.html", 
            context={"request": request, "dsn1": src_dsn, "dsn2": dstn_dsn, "common_cols": common_cols}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_report", response_class=HTMLResponse)
async def generate_report_route(request: Request, id_cols: list[str] = Form(...)):
    try:
        start_time = time.perf_counter()
        
        src_dsn, dstn_dsn = get_dsns()
        
        # Make sure user picked at least one column
        if not id_cols:
            raise HTTPException(status_code=400, detail="You must select at least one comparison key.")
            
        results = run_duckdb_comparison(src_dsn, dstn_dsn, id_cols)
        
        end_time = time.perf_counter()
        execution_time = round(end_time - start_time, 2)
        
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

        # Render template context
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
        
        # Render HTML string
        template = templates.get_template('report_template.html')
        html_out = template.render(context)
        
        # Save to static directory
        output_path = os.path.join('static', 'report.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_out)
        
        # Open in browser automatically
        abs_path = os.path.abspath(output_path)
        webbrowser.open(f'file:///{abs_path}')
        

        success_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Report Generated</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <div class="mesh-bg">
                <div class="mesh-blob blob-1"></div>
                <div class="mesh-blob blob-2"></div>
                <div class="mesh-blob blob-3"></div>
            </div>
            <div class="app-wrapper" style="align-items: center; justify-content: center; min-height: 80vh;">
                <div class="glass-panel" style="padding: 3rem; text-align: center; max-width: 600px;">
                    <h2 style="color: var(--color-success); margin-bottom: 1rem;">Report Generated Successfully!</h2>
                    <p style="color: var(--color-text-secondary); margin-bottom: 2rem;">
                        You can close this window safely.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=success_html)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    # Open setup page automatically on startup
    webbrowser.open('http://127.0.0.1:8000')
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
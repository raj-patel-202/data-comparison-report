import os
import json
import webbrowser
import time
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from compare import run_duckdb_comparison, get_common_columns
import uvicorn
from excel_export import ExportRequest, generate_excel_workbook
from report_builder import build_template_context

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
        
        # Render template context
        context = build_template_context(request, results, src_dsn, dstn_dsn, execution_time)
        
        # Render HTML string
        template = templates.get_template('report_template.html')
        html_out = template.render(context)
        
        # Save to static directory
        output_path = os.path.join('static', 'report.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_out)
        
        # Open in browser automatically
        webbrowser.open('http://127.0.0.1:8000/static/report.html')
        

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
                        You can close this window safely, or generate another report.
                    </p>
                    <button class="glass-btn" onclick="window.location.href='/'" style="padding: 10px 24px; font-size: 1rem; font-weight: 600; cursor: pointer; border-radius: 8px; background: rgba(0, 122, 255, 0.1); color: var(--color-accent); border: 1px solid rgba(0, 122, 255, 0.2); transition: all 0.2s;">
                        Generate New Report
                    </button>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=success_html)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export_excel")
async def export_excel(req: ExportRequest):
    out = generate_excel_workbook(req)
    
    filename = "Comparison_Report.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    return StreamingResponse(out, headers=headers, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == '__main__':
    # Open setup page automatically on startup
    webbrowser.open('http://127.0.0.1:8000')
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
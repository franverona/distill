import csv
import io
import json

from fastapi.responses import StreamingResponse


def export_csv(records) -> StreamingResponse:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "url", "summary", "model", "created_at"])
    for r in records:
        writer.writerow([r.id, r.url, r.summary, r.model, r.created_at])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=summaries.csv"},
    )


def export_jsonl(records) -> StreamingResponse:
    def generate():
        for r in records:
            yield json.dumps({"id": r.id, "url": r.url, "summary": r.summary}) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")

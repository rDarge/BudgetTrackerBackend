from io import TextIOWrapper
from fastapi import FastAPI, UploadFile
import uvicorn

from backend.csv import parse_csv

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post("/import")
async def import_csv(uploadFile: UploadFile):
    async with uploadFile.file as binaryFile:
        csv_file = TextIOWrapper(binaryFile, encoding="utf-8")
        transactions = parse_csv(csv_file)
        return {"description": transactions[0].description, "total": len(transactions)}


# curl --header "Content-Type:application/octet-stream" --trace-ascii debugdump.txt --data-binary test_data/sensitive/sample_transactions_checking.CSV http://localhost:8000/import
# curl -L -F "file=@test_data/sensitive/sample_transactions_checking.CSV" http://localhost:8000/import


def start():
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)

call env\Scripts\activate.bat
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
@REM python -m app.main
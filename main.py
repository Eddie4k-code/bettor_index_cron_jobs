from db.db import get_db

def main():
    with get_db() as db:
        # Example: pass db to your pipeline functions
        # from pipelines.some_pipeline import run_pipeline
        # run_pipeline(db)
        pass

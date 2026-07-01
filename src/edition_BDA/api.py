from fastapi import FastAPI, Query
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

DB_URL = "mysql+mysqldb://root:@127.0.0.1:3306/data-viz_db?charset=utf8mb4"
engine = create_engine(DB_URL, pool_pre_ping=True)

app = FastAPI(title="BDA API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/editions-par-annee")
def editions_par_annee():

    sql = """
    SELECT 
    e.lieu AS ville,
    v.latitude,
    v.longitude,
    GROUP_CONCAT(e.annee ORDER BY e.annee ASC SEPARATOR '\n') AS annees_edition 
FROM edition e
JOIN ville v ON v.nom = e.lieu
GROUP BY e.lieu, v.latitude, v.longitude
ORDER BY e.lieu ASC;
    """

    try:
        with engine.connect() as conn:
            rows = conn.execute(text(sql)).mappings().all()

        return {
            "count": len(rows),
            "data": [dict(r) for r in rows]
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
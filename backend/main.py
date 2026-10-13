import json
from contextlib import asynccontextmanager
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agents.example_questions import build_example_groups, current_year, flat_examples
from agents.help_agent import HELP_ANSWER, match_help_question, unsupported_hint
from agents.schema_agent import SchemaAgent
from agents.retriever_agent import RetrieverAgent
from agents.sql_agent import SQLGeneratorAgent
from agents.synth_agent import SynthesizerAgent
from db.database import sql_dialect
from db.init_db import ensure_database

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

load_dotenv(PROJECT_ROOT / ".env")

APP_VERSION = (PROJECT_ROOT / "VERSION").read_text(encoding="utf-8").strip()

schema = {
    "customers": ["id", "name", "city", "age"],
    "employees": ["id", "name", "department", "joining_date"],
    "products": ["id", "name", "category", "price"],
    "sales": ["id", "customer_id", "employee_id", "product_id", "quantity", "sale_amount", "sale_date"],
}

schema_agent = SchemaAgent()
sql_agent = SQLGeneratorAgent(schema, dialect=sql_dialect())
retriever_agent = RetrieverAgent()
synth_agent = SynthesizerAgent()


def sync_examples_json() -> None:
    payload = {
        "current_year": current_year(),
        "groups": build_example_groups(),
        "examples": flat_examples(),
    }
    (FRONTEND_DIR / "demo" / "examples.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_database(force_seed=False)
    sync_examples_json()
    yield


app = FastAPI(
    title="Multi-Agent RAG NL-to-SQL System",
    version=APP_VERSION,
    description="Natural-language questions → schema routing → SQL → database → synthesized answers.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


class AskSteps(BaseModel):
    schema_used: Optional[Dict[str, List[str]]] = None
    generated_sql: Optional[str] = None
    result_rows: Optional[List[Dict[str, Any]]] = None


class AskResponse(BaseModel):
    answer: str
    error: Optional[str] = None
    steps: AskSteps


def serialize_value(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def serialize_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [{k: serialize_value(v) for k, v in row.items()} for row in rows]


@app.get("/health")
def health():
    return {"status": "ok", "version": APP_VERSION, "database": sql_dialect()}


@app.get("/examples")
def examples():
    return {
        "current_year": current_year(),
        "groups": build_example_groups(),
        "examples": flat_examples(),
    }


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    question = req.question.strip()

    if not question:
        return {
            "answer": "Please provide a valid question.",
            "error": "Empty question.",
            "steps": {
                "schema_used": None,
                "generated_sql": None,
                "result_rows": None,
            },
        }

    if match_help_question(question):
        return {
            "answer": HELP_ANSWER,
            "error": None,
            "steps": {
                "schema_used": schema,
                "generated_sql": None,
                "result_rows": None,
            },
        }

    relevant = schema_agent.identify_relevant_tables(question)

    if not relevant:
        return {
            "answer": "I couldn't find any relevant tables for your question.",
            "error": "Schema or table not found.",
            "steps": {
                "schema_used": None,
                "generated_sql": None,
                "result_rows": None,
            },
        }

    sql_data = sql_agent.generate_sql(question)

    if sql_data.get("error"):
        return {
            "answer": unsupported_hint(),
            "error": None,
            "steps": {
                "schema_used": relevant,
                "generated_sql": None,
                "result_rows": None,
            },
        }

    sql = sql_data.get("sql")
    params = sql_data.get("params", [])

    db_output = retriever_agent.execute_query(sql, params)

    if db_output.get("error"):
        return {
            "answer": "There was an error while running your SQL query.",
            "error": db_output["error"],
            "steps": {
                "schema_used": relevant,
                "generated_sql": sql,
                "result_rows": None,
            },
        }

    rows = db_output.get("rows", [])

    if len(rows) == 0:
        return {
            "answer": "No matching records found for your question.",
            "error": None,
            "steps": {
                "schema_used": relevant,
                "generated_sql": sql,
                "result_rows": [],
            },
        }

    answer = synth_agent.synthesize(question, sql, rows)
    serialized_rows = serialize_rows(rows)

    return {
        "answer": answer,
        "error": None,
        "steps": {
            "schema_used": relevant,
            "generated_sql": sql,
            "result_rows": serialized_rows,
        },
    }


@app.get("/api")
def api_root():
    return {
        "message": "Multi-Agent RAG NL-to-SQL API. Use POST /ask with a question.",
        "version": APP_VERSION,
        "docs": "/docs",
    }


if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

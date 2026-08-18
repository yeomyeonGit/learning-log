# L — SQLite에 스트리밍 적재.
# 04_practice.py에서 확인한 함정: sqlite3.Connection을 `with conn`으로 감싸도
# commit/rollback만 될 뿐 close()는 호출되지 않는다.
# 여기서는 그 문제를 @contextlib.contextmanager 기반(제너레이터 기반) 컨텍스트 매니저로 직접 해결한다.

import contextlib
import sqlite3

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS cards (
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    hint TEXT,
    published_at TEXT
)
"""


@contextlib.contextmanager
def db_connection(db_path):
    """성공 시 commit, 예외 시 rollback 후 그대로 전파, 어느 경우든 finally에서 반드시 close().
    yield 이전이 __enter__, try/except/else/finally가 __exit__ 역할을 하는 제너레이터 기반 컨텍스트 매니저."""
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.close()


def load_cards(conn, cleaned_cards):
    """정제된 tuple 스트림을 받아 INSERT한다. executemany에 제너레이터를 그대로 넘기므로
    전체를 리스트로 모으지 않고 한 줄씩 스트리밍 적재된다."""
    conn.execute(_CREATE_TABLE)
    conn.execute("DELETE FROM cards")  # 반복 실행 시 중복 적재 방지 (멱등성)
    conn.executemany(
        "INSERT INTO cards (front, back, hint, published_at) VALUES (?, ?, ?, ?)",
        cleaned_cards,
    )

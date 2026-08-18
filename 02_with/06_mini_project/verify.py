# db_connection(제너레이터 기반 컨텍스트 매니저)이 실제로 커넥션을 닫는지,
# 그리고 예외 발생 시 rollback되는지를 assert로 검증한다.
# (04_practice.py에서 확인한 "with conn은 commit일 뿐 close가 아니다" 문제의 해결 확인)

import os
import sqlite3

from load import db_connection
from pipeline import CSV_PATH, DB_PATH, run


def check(label, condition):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")


def verify_success_path():
    row_count = run(CSV_PATH, DB_PATH)
    check("CSV의 유효한 카드가 1건 이상 적재된다", row_count > 0)

    conn = sqlite3.connect(DB_PATH)
    try:
        stored = conn.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
        check("commit되어 DB에서 다시 읽어도 같은 건수가 보인다", stored == row_count)
    finally:
        conn.close()


def verify_connection_closes_on_success():
    with db_connection(DB_PATH) as conn:
        pass
    try:
        conn.execute("SELECT 1")
        closed = False
    except sqlite3.ProgrammingError:
        closed = True
    check("with 블록을 나오면 (04_practice.py와 달리) 커넥션이 실제로 close된다", closed)


def verify_rollback_and_close_on_exception():
    with db_connection(DB_PATH) as conn:
        before = conn.execute("SELECT COUNT(*) FROM cards").fetchone()[0]

    caught = False
    try:
        with db_connection(DB_PATH) as conn:
            conn.execute("DELETE FROM cards")
            raise RuntimeError("적재 중 실패 상황을 흉내")
    except RuntimeError:
        caught = True
    check("예외는 삼켜지지 않고 그대로 전파된다", caught)

    verify_conn = sqlite3.connect(DB_PATH)
    try:
        after = verify_conn.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
        check("예외가 나면 rollback되어 DELETE가 반영되지 않는다", after == before)
    finally:
        verify_conn.close()

    try:
        conn.execute("SELECT 1")
        closed = False
    except sqlite3.ProgrammingError:
        closed = True
    check("예외가 나도 커넥션은 finally에서 close된다", closed)


if __name__ == "__main__":
    print("=== 1) 성공 경로: 스트리밍 적재 + commit 확인 ===")
    verify_success_path()

    print()
    print("=== 2) with 블록을 나오면 실제로 close되는지 확인 ===")
    verify_connection_closes_on_success()

    print()
    print("=== 3) 예외 발생 시 rollback + close 확인 ===")
    verify_rollback_and_close_on_exception()

    os.remove(DB_PATH)

# db_connection(제너레이터 기반 컨텍스트 매니저)이 실제로 커넥션을 닫는지,
# 그리고 예외 발생 시 rollback되는지를 assert로 검증한다.
# (04_practice.py에서 확인한 "with conn은 commit일 뿐 close가 아니다" 문제의 해결 확인)

import os
import sqlite3

from extract import iter_cards
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


def verify_generator_closes_file_on_early_exit():
    """iter_cards는 제너레이터라 `with open(...)`이 즉시 실행되지 않고, 처음 소비되는
    순간(next())에야 열린다. 이 테스트는 그 파일을 끝까지 순회하지 않고 도중에
    gen.close()로 강제 종료했을 때도 with 블록의 __exit__이 실행되어 파일이 닫히는지
    확인한다: gen.close()는 일시정지된 제너레이터 프레임에 GeneratorExit을 던지고,
    이 예외가 with 블록을 빠져나가면서 파일을 닫는다."""
    gen = iter_cards(CSV_PATH)
    check("제너레이터를 만든 시점엔 아직 with 블록이 실행되지 않아 f가 없다", "f" not in gen.gi_frame.f_locals)

    first_row = next(gen)  # with open(...) 실행 -> 첫 행까지 진행 -> yield에서 일시정지
    f = gen.gi_frame.f_locals["f"]  # 일시정지된 제너레이터 프레임에서 지역변수 f(파일 객체)를 직접 참조
    check("첫 행을 소비했다", first_row["front"] != "")
    check("for 루프를 끝까지 돌지 않았는데도 파일은 아직 열려 있다", not f.closed)

    gen.close()
    check("gen.close() -> GeneratorExit -> with __exit__ 실행으로 파일이 닫힌다", f.closed)


if __name__ == "__main__":
    print("=== 1) 성공 경로: 스트리밍 적재 + commit 확인 ===")
    verify_success_path()

    print()
    print("=== 2) with 블록을 나오면 실제로 close되는지 확인 ===")
    verify_connection_closes_on_success()

    print()
    print("=== 3) 예외 발생 시 rollback + close 확인 ===")
    verify_rollback_and_close_on_exception()

    print()
    print("=== 4) yield + with: 제너레이터를 도중에 close()해도 파일이 닫히는지 확인 ===")
    verify_generator_closes_file_on_early_exit()

    os.remove(DB_PATH)

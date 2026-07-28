# with를 실제로 사용하는 경우: 데이터엔지니어링 사례 연습.
# - 파일 읽기: duo_cards_it_export.csv (Duolingo 이탈리아어 카드 export)
# - DB 커넥션 열고 닫기: SQLite (표준 라이브러리 sqlite3, 서버 설치 없이 바로 연결 가능)
# - 여러 리소스 동시 관리: csv 파일 + DB 커넥션을 함께 열어서 스트리밍으로 적재

import contextlib
import csv
import os
import sqlite3
import tempfile

CSV_PATH = os.path.join(os.path.dirname(__file__), "duo_cards_it_export.csv")
DB_PATH = os.path.join(tempfile.gettempdir(), "duo_cards_practice.db")


def read_cards(csv_path):
    """with로 csv 파일을 열고 닫는다.
    newline="" + csv.DictReader 조합이라 따옴표로 감싼 멀티라인 hint 필드도 알아서 처리된다."""
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_cards_into_sqlite(csv_path, conn):
    """csv 파일 자원 + 이미 열려 있는 DB 커넥션, 두 자원을 한 with 블록에서 함께 사용해
    파일 전체를 메모리에 올리지 않고 한 줄씩 스트리밍으로 적재한다."""
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        with conn:  # 주의: with conn은 "닫기"가 아니라 트랜잭션 commit/rollback이다
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cards (
                    front TEXT,
                    back TEXT,
                    hint TEXT,
                    published_at TEXT
                )
                """
            )
            conn.execute("DELETE FROM cards")  # 반복 실행 시 중복 적재 방지
            conn.executemany(
                "INSERT INTO cards VALUES (:front, :back, :hint, :publishedAt)",
                reader,
            )


if __name__ == "__main__":
    print("=== 1) with로 csv 파일 읽기 (자원 1개: 파일) ===")
    cards = read_cards(CSV_PATH)
    print(f"읽은 카드 수: {len(cards)}")
    print("첫 번째 카드:", {k: v[:30] for k, v in cards[0].items()})

    print()
    print("=== 2) csv 파일 + SQLite 커넥션, 두 자원을 동시에 관리 ===")
    # sqlite3.Connection에는 close()를 대신 호출해주는 __exit__이 없다.
    # contextlib.closing으로 감싸야 with 블록을 벗어날 때 진짜로 close()가 불린다.
    with contextlib.closing(sqlite3.connect(DB_PATH)) as conn:
        load_cards_into_sqlite(CSV_PATH, conn)

        row_count = conn.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
        print(f"[적재 완료] {row_count}개의 카드를 SQLite에 저장")

        print()
        print("=== 3) with conn은 '커밋'이지 '닫기'가 아니다 (흔한 착각) ===")
        sample = conn.execute("SELECT front, back FROM cards LIMIT 3").fetchall()
        print("load_cards_into_sqlite의 with conn 블록을 나왔지만 커넥션은 여전히 열려 쿼리가 된다:")
        for front, back in sample:
            print(f"  - {front} -> {back}")

    print()
    print("=== 4) contextlib.closing의 with 블록을 나오면 그제서야 진짜로 닫힌다 ===")
    try:
        conn.execute("SELECT 1")
    except sqlite3.ProgrammingError as exc:
        print("닫힌 커넥션에 쿼리 시도 -> 예외:", exc)

    os.remove(DB_PATH)

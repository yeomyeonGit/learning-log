# 오케스트레이터 — E(extract) -> T(transform) -> L(load)을 조립한다.
# load의 executemany가 당기면 transform -> extract 순으로 한 줄씩 생산-소비되는 제너레이터 체인이라,
# CSV 전체나 정제된 카드 전체를 메모리에 모으지 않는다.

import os

from extract import iter_cards
from load import db_connection, load_cards
from transform import iter_clean_cards

_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV_PATH = os.path.join(os.path.dirname(_DIR), "duo_cards_it_export.csv")
DEFAULT_DB_PATH = os.path.join(_DIR, "duo_cards.db")

CSV_PATH = os.environ.get("CSV_PATH", DEFAULT_CSV_PATH)
DB_PATH = os.environ.get("DB_PATH", DEFAULT_DB_PATH)


def run(csv_path=CSV_PATH, db_path=DB_PATH):
    raw_cards = iter_cards(csv_path)
    cleaned_cards = iter_clean_cards(raw_cards)
    with db_connection(db_path) as conn:
        load_cards(conn, cleaned_cards)
        row_count = conn.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
    return row_count


if __name__ == "__main__":
    count = run()
    print(f"[적재 완료] {count}개의 카드를 {DB_PATH}에 저장")

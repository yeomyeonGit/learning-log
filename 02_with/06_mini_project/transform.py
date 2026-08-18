# T — raw dict를 DB 적재용 tuple로 정제한다.


def clean_card(row):
    """CSV 컬럼(front, back, hint, publishedAt)을 정제해 DB 컬럼 순서
    (front, back, hint, published_at)에 맞는 tuple로 변환한다.
    front/back이 비어있는 행은 카드로서 의미가 없으므로 None을 반환해 스킵 신호로 쓴다."""
    front = row["front"].strip()
    back = row["back"].strip()
    if not front or not back:
        return None
    hint = row["hint"].strip()
    published_at = row["publishedAt"].strip()
    return (front, back, hint, published_at)


def iter_clean_cards(rows):
    """extract가 만든 raw dict 스트림을 받아 정제된 tuple만 걸러서 yield한다."""
    for row in rows:
        cleaned = clean_card(row)
        if cleaned is not None:
            yield cleaned

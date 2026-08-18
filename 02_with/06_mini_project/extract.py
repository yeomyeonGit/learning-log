# E — CSV 파일을 한 줄씩 스트리밍하는 제너레이터.

import csv


def iter_cards(csv_path):
    """duo_cards_it_export.csv를 열어 한 줄씩 dict로 yield한다.
    list로 모으지 않고 제너레이터로 흘려보내므로 대용량 파일에서도 메모리 사용량이 O(1)이다."""
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

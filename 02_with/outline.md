# with로 구현하는 자원 관리 안전성 — 목차

챕터 순서를 `02_with/` 폴더의 실제 파일 번호(01→05)와 1:1로 맞춘 블로그 포스팅 목차.

---

1. 들어가며
    - 학습 계기
    - 학습 목표
    - 레포지토리 구조 소개 (`02_with/01~05` 파일 로드맵, `duo_cards_it_export.csv` 샘플 데이터)

2. 컨텍스트 매니저란 무엇인가 — [`01_context_manager.py`](01_context_manager.py)
    - 컨텍스트, 컨텍스트 매니저 정의
    - `__enter__` / `__exit__` 프로토콜
    - 동작 흐름: 진입 - 처리 - 종료
    - `with` 없이 프로토콜을 손으로 직접 호출해보기
    - `__exit__`의 반환값과 예외 처리
        - 예외를 그대로 전파시키는 경우 (`return False`)
        - 예외를 삼키는 경우 (`return True`)와 그 위험성

3. try/finally의 한계와 with의 등장 — [`02_finally.py`](02_finally.py)
    - try/finally로 자원을 관리하는 기본 패턴
    - 한계 1: `close()` 호출을 깜빡하면 생기는 자원 누수
    - 한계 2: 자원이 여러 개일 때 급격히 깊어지는 중첩 try/finally
    - 이 한계가 `with` 문법 등장의 배경이 된다

4. with의 특징
    - 이점 (자동 정리 보장, 가독성, 예외 안전성)
    - 한계 (모든 자원이 컨텍스트 매니저를 지원하지는 않음, 잘못 쓰면 오히려 착각을 유발 — 6장의 `sqlite3` 사례 예고)

5. with를 사용한 자원 관리 문법 — [`03_with.py`](03_with.py)
    - block statement + context manager 조합
    - 기본 with 문
    - 콤마(`,`)로 여러 컨텍스트 매니저 묶기
    - 중첩 with
    - 표준 라이브러리 실사례: `open()`
    - 클래스 기반(`__enter__`/`__exit__`) vs `@contextlib.contextmanager`(제너레이터 기반)
    - `contextlib.ExitStack` — 개수가 가변적인 자원 묶음 관리 (7장에서 실습으로 이어짐)

6. with를 사용하는 경우: 실전 사례 — [`04_practice.py`](04_practice.py)
    - 데이터엔지니어링의 사례
        - 파일 읽기/쓰기: `duo_cards_it_export.csv`를 `csv.DictReader`로 안전하게 읽기 (멀티라인 필드 처리 포함)
        - DB 커넥션 열고 닫기: SQLite(`sqlite3`)로 연결 — 서버 설치 없이 가장 간단히 붙는 오픈소스 DB
        - 여러 리소스 동시 관리: csv 파일 + DB 커넥션을 하나의 with 흐름에서 함께 다루며 스트리밍 적재
    - 백엔드 개발의 사례
        - 락(lock) 획득/해제 (`threading.Lock`, `asyncio.Lock`)
        - 트랜잭션 범위 관리 (commit/rollback)
        - 테스트에서의 활용 (`unittest.mock.patch`, `pytest.raises`)

7. 자원 안전성 검증 — [`05_test.py`](05_test.py)
    - naive(자원 누수) vs try/finally vs with, 세 방식을 assert로 직접 비교
    - `contextlib.ExitStack`으로 여러 리소스를 한 번에 열고, 중간에 예외가 나도 전부 안전하게 닫히는지 검증
    - 이 챕터가 곧 "with가 안전하다"는 주장에 대한 코드 근거

8. 주의할 지점
    - 안티패턴
        - 예외를 의도치 않게 삼키는 `__exit__` (`return True`의 함정)
        - `sqlite3.Connection`을 `with`로 감싸면 닫힌다고 착각하는 경우 — `with conn`은 커밋/롤백일 뿐 close가 아니다 (`04_practice.py`에서 실행 결과로 확인한 내용)
    - 실전 체크리스트
        - 자원 누수 여부를 어떻게 점검할 것인가
        - `__exit__`에서 예외를 삼켜야 하는 경우 vs 삼키면 안 되는 경우 구분
        - 컨텍스트 매니저가 실제로 `close()`까지 호출하는지 문서로 확인하는 습관

9. 추가 학습할 내용
    - 나만의 컨텍스트 매니저 직접 구현하기 (`__enter__`/`__exit__`, `contextlib`)
    - 트랜잭션과 with의 관계
    - 멀티스레딩/멀티프로세싱에서의 with
    - `async with` (`__aenter__`/`__aexit__`) — asyncio 기반 비동기 컨텍스트 매니저

- 레포지토리 공유

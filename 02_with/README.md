# 02. with로 구현하는 자원 관리 안전성

## 태그
`자원 관리` `컨텍스트 매니저` `예외 처리`

## 요약

파일, DB 커넥션처럼 "다 쓰면 반드시 반납해야 하는" 자원을 예외 상황에서도 안전하게 닫아주는 `with` 문을 4단계로 뜯어봤다.

- **프로토콜 관점**: `with`는 마법이 아니라 `__enter__`/`__exit__`이라는 두 메서드 호출을 자동화해주는 문법 설탕이다. `__exit__`은 예외가 나도 반드시 호출되고, `True`를 반환하면 예외를 삼킬 수도 있다.
- **try/finally와의 비교**: try/finally로도 안전하게 닫을 수 있지만, 자원이 여러 개가 되는 순간 중첩이 급격히 깊어지고 `close()` 호출을 깜빡하기 쉽다. `with`는 이 반복을 문법 레벨에서 강제한다.
- **문법 변주**: 클래스 기반(`__enter__`/`__exit__`) 뿐 아니라 `@contextlib.contextmanager`로 제너레이터 함수를 컨텍스트 매니저로 만들 수 있고, 콤마로 여러 개를 한 줄에 묶거나 `contextlib.ExitStack`으로 개수가 가변적인 자원들을 한 번에 관리할 수 있다.
- **검증**: naive(자원 누수) / try-finally(정상) / with(정상) 세 버전을 실제로 실행해 열린 자원 개수를 비교하면, `with`가 예외 상황에서도 자원을 안전하게 반납한다는 것을 코드로 확인할 수 있다.

## 목차

블로그 포스팅용 전체 목차와 파일-챕터 매핑은 [`outline.md`](outline.md) 참고.

## 파일

| 챕터 | 파일 | 내용 |
|---|---|---|
| 2. 컨텍스트 매니저란 무엇인가 | [`01_context_manager.py`](01_context_manager.py) | `with` 없이 `__enter__`/`__exit__`을 직접 호출해 진입-처리-종료 흐름과 예외 전달/억제(`return True`) 방식을 확인 |
| 3. try/finally의 한계와 with의 등장 | [`02_finally.py`](02_finally.py) | try/finally로 자원을 닫을 때의 한계(누수 가능성, 중첩 심화)를 재현 |
| 5. with를 사용한 자원 관리 문법 | [`03_with.py`](03_with.py) | `with`의 기본 문법, 다중/중첩 `with`, 표준 라이브러리 실사례(`open`), `@contextlib.contextmanager` |
| 6. with를 사용하는 경우: 실전 사례 | [`04_practice.py`](04_practice.py) | `duo_cards_it_export.csv` 파일 읽기 + SQLite(`sqlite3`) 커넥션을 동시에 관리하며 데이터 적재. `sqlite3.Connection`은 `with`로 감싸도 **커밋만 될 뿐 close되지 않는다**는 함정과 `contextlib.closing`으로 이를 보완하는 법을 확인 |
| 7. 자원 안전성 검증 | [`05_test.py`](05_test.py) | naive vs try/finally vs with 방식의 자원 안전성을 assert로 검증, `contextlib.ExitStack`으로 여러 리소스 동시 관리 |

## 데이터

- `duo_cards_it_export.csv` — Duolingo 이탈리아어 학습 카드 export (front/back/hint/publishedAt). `04_practice.py`의 파일 읽기/DB 적재 연습용 샘플 데이터.

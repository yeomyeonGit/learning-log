# naive / try-finally / with 세 가지 방식의 자원 안전성을 실제로 검증(assert)한다.
# 데이터엔지니어링에서 흔한 "여러 DB 커넥션을 동시에 열고, 중간에 하나가
# 실패해도 전부 안전하게 닫혀야 하는" 시나리오를 contextlib.ExitStack으로 재현한다.

import contextlib


class FakeConnection:
    open_count = 0  # 현재 열려 있는 커넥션 수 (자원 누수 확인용)

    def __init__(self, name):
        self.name = name
        self.closed = True

    def __enter__(self):
        self.closed = False
        FakeConnection.open_count += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.closed:
            self.closed = True
            FakeConnection.open_count -= 1
        return False

    def query(self, sql):
        if self.closed:
            raise ValueError("closed connection에 query 시도")
        if sql == "BAD":
            raise RuntimeError("쿼리 실행 중 에러!")


def check(label, condition):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")


def naive_leak_demo():
    conn = FakeConnection("naive")
    conn.__enter__()
    try:
        conn.query("BAD")
    except RuntimeError:
        pass
    return conn


def with_safety_demo():
    result = {}
    try:
        with FakeConnection("safe") as conn:
            result["conn"] = conn
            conn.query("BAD")
    except RuntimeError:
        pass
    return result["conn"]


def multi_resource_demo():
    """여러 리소스를 동시에 열고, 중간에 예외가 나도 전부 닫히는지 검증한다.
    (데이터엔지니어링: 여러 DB 커넥션/파일 핸들을 동시에 관리하는 상황을 흉내)"""
    names = ["db-1", "db-2", "db-3"]
    opened = []

    try:
        with contextlib.ExitStack() as stack:
            for name in names:
                conn = stack.enter_context(FakeConnection(name))
                opened.append(conn)
            opened[1].query("BAD")  # 두 번째 리소스 처리 중 예외 발생
    except RuntimeError:
        pass  # ExitStack은 자원을 안전하게 닫아줄 뿐, 예외 자체를 삼키지는 않는다

    return opened


if __name__ == "__main__":
    print("=== 1) close()를 깜빡한 naive 버전: 자원이 샌다 ===")
    before = FakeConnection.open_count
    leaked_conn = naive_leak_demo()
    check("naive 버전은 예외 발생 시 커넥션이 닫히지 않는다", leaked_conn.closed is False)
    check("open_count가 그대로 남아있다 (누수)", FakeConnection.open_count == before + 1)

    print()
    print("=== 2) with로 감싼 버전: 예외가 나도 반드시 닫힌다 ===")
    safe_conn = with_safety_demo()
    check("with 버전은 예외가 나도 커넥션이 닫힌다", safe_conn.closed is True)

    print()
    print("=== 3) ExitStack으로 여러 리소스를 한 번에 관리 ===")
    before = FakeConnection.open_count
    conns = multi_resource_demo()
    check("예외가 나도 열었던 리소스가 전부 닫힌다", all(c.closed for c in conns))
    check("open_count가 예외 이전 수준으로 돌아온다", FakeConnection.open_count == before)

    print()
    print(f"최종 open_count: {FakeConnection.open_count} (1번의 naive 누수는 여전히 남아있는 게 정상)")

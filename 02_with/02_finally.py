# try/finally로 자원을 직접 관리할 때의 한계를 보여준다.
# (1) close()를 깜빡하면 자원이 샌다
# (2) 자원이 여러 개면 중첩된 try/finally로 코드가 급격히 지저분해진다


class FakeConnection:
    open_count = 0  # 현재 열려 있는 커넥션 수 (자원 누수 확인용)

    def __init__(self, name):
        self.name = name
        self.closed = True

    def open(self):
        self.closed = False
        FakeConnection.open_count += 1
        print(f"[열림] {self.name}")

    def close(self):
        if not self.closed:
            self.closed = True
            FakeConnection.open_count -= 1
            print(f"[닫힘] {self.name}")

    def query(self, sql):
        if self.closed:
            raise ValueError("closed connection에 query 시도")
        if sql == "BAD":
            raise RuntimeError("쿼리 실행 중 에러!")
        print(f"[쿼리] {self.name} <- {sql}")


def naive_close_missing():
    """close()를 깜빡한 경우: 예외가 나면 자원이 영영 안 닫힌다."""
    conn = FakeConnection("conn-naive")
    conn.open()
    conn.query("BAD")  # 여기서 예외 발생 -> 아래 close()는 실행되지 않는다
    conn.close()


def with_try_finally():
    """try/finally로 제대로 닫는 경우: 예외가 나도 finally는 항상 실행된다."""
    conn = FakeConnection("conn-finally")
    conn.open()
    try:
        conn.query("BAD")
    finally:
        conn.close()


def nested_resources_try_finally():
    """자원이 여러 개면 try/finally가 중첩되어 급격히 읽기 어려워진다."""
    conn_a = FakeConnection("conn-A")
    conn_a.open()
    try:
        conn_b = FakeConnection("conn-B")
        conn_b.open()
        try:
            conn_c = FakeConnection("conn-C")
            conn_c.open()
            try:
                conn_a.query("SELECT 1")
                conn_b.query("SELECT 2")
                conn_c.query("SELECT 3")
            finally:
                conn_c.close()
        finally:
            conn_b.close()
    finally:
        conn_a.close()


if __name__ == "__main__":
    print("=== 1) close()를 깜빡한 경우 (자원 누수) ===")
    try:
        naive_close_missing()
    except RuntimeError as exc:
        print(f"예외 발생: {exc}")
    print("열려 있는 커넥션 수:", FakeConnection.open_count, "-> 누수 발생! (이 커넥션은 이후에도 계속 열려 있다)")

    print()
    print("=== 2) try/finally로 제대로 닫은 경우 ===")
    try:
        with_try_finally()
    except RuntimeError as exc:
        print(f"예외 발생: {exc}")
    print("열려 있는 커넥션 수:", FakeConnection.open_count, "(1번의 누수분만 남아있으면 정상)")

    print()
    print("=== 3) 자원이 여러 개일 때: 중첩 try/finally (가독성 한계) ===")
    nested_resources_try_finally()
    print("열려 있는 커넥션 수:", FakeConnection.open_count, "(여전히 1번의 누수분만 남아있으면 정상)")

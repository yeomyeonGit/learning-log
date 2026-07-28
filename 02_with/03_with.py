# with 문법 자체를 다루는 예제.
# block statement + context manager 조합, 여러 개를 한 줄에 묶는 법,
# 중첩, 표준 라이브러리 실사례(open), 그리고 @contextlib.contextmanager로
# 클래스 없이 컨텍스트 매니저를 만드는 법까지 한 파일에 모았다.

import contextlib
import os
import tempfile


class FakeConnection:
    def __init__(self, name):
        self.name = name
        self.closed = True

    def __enter__(self):
        self.closed = False
        print(f"[열림] {self.name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.closed = True
        print(f"[닫힘] {self.name} (exc_type={exc_type})")
        return False

    def query(self, sql):
        if self.closed:
            raise ValueError("closed connection에 query 시도")
        print(f"[쿼리] {self.name} <- {sql}")


@contextlib.contextmanager
def managed_connection(name):
    """클래스 대신 제너레이터 함수 + @contextmanager로 컨텍스트 매니저를 만드는 방법."""
    conn = FakeConnection(name)
    conn.__enter__()  # yield 이전 = __enter__
    try:
        yield conn  # 여기서 as 대상으로 값을 넘긴다
    finally:
        conn.__exit__(None, None, None)  # yield 이후(finally 블록) = __exit__


if __name__ == "__main__":
    print("=== 1) 기본 with: block statement + context manager ===")
    with FakeConnection("conn-1") as conn:
        conn.query("SELECT 1")
    print("closed:", conn.closed)

    print()
    print("=== 2) 예외가 나도 __exit__은 항상 호출된다 ===")
    try:
        with FakeConnection("conn-2") as conn:
            conn.query("SELECT 1")
            raise RuntimeError("처리 중 에러!")
    except RuntimeError as exc:
        print(f"바깥으로 전파된 예외: {exc}")
    print("closed:", conn.closed)

    print()
    print("=== 3) 콤마로 여러 컨텍스트 매니저를 한 with에 묶기 ===")
    with FakeConnection("conn-A") as a, FakeConnection("conn-B") as b:
        a.query("SELECT A")
        b.query("SELECT B")
    print("closed:", a.closed, b.closed)

    print()
    print("=== 4) 중첩 with (콤마 버전과 사실상 동일한 효과) ===")
    with FakeConnection("conn-X") as x:
        with FakeConnection("conn-Y") as y:
            x.query("SELECT X")
            y.query("SELECT Y")
    print("closed:", x.closed, y.closed)

    print()
    print("=== 5) 파일 입출력: 표준 라이브러리의 실제 with 사례 ===")
    tmp_path = os.path.join(tempfile.gettempdir(), "with_demo.txt")
    with open(tmp_path, "w") as file_out:
        file_out.write("hello with\n")
    with open(tmp_path) as file_in:
        print("파일 내용:", file_in.read().strip())
    print("파일 closed:", file_in.closed)
    os.remove(tmp_path)

    print()
    print("=== 6) 클래스가 아니라 @contextlib.contextmanager로도 만들 수 있다 ===")
    with managed_connection("conn-gen") as conn:
        conn.query("SELECT 1 (generator 기반)")
    print("closed:", conn.closed)

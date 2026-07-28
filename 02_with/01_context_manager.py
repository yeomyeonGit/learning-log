# 컨텍스트 매니저 프로토콜(__enter__/__exit__) 자체를 이해하기 위한 예제.
# 아직 with 키워드는 쓰지 않고, 프로토콜을 손으로 직접 호출해서
# "진입 - 처리 - 종료" 흐름과 예외 전달 방식을 눈으로 확인한다.


class ManagedFile:
    def __init__(self, name):
        self.name = name
        self.closed = True

    def __enter__(self):
        print(f"[진입] {self.name} 오픈")
        self.closed = False
        return self  # as 뒤에 바인딩되는 값

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"[종료] {self.name} 클로즈 (exc_type={exc_type})")
        self.closed = True
        return False  # 예외를 삼키지 않고 그대로 전파시킨다

    def write(self, data):
        if self.closed:
            raise ValueError("closed file에 write 시도")
        print(f"[처리] {self.name} <- {data!r}")


class SuppressingResource:
    def __enter__(self):
        print("[진입] SuppressingResource")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"[종료] 예외 {exc_type.__name__}를 여기서 삼킴")
        return True  # 예외를 삼킴 -> 바깥으로 전파되지 않는다


if __name__ == "__main__":
    print("=== 1) with 없이, 프로토콜을 손으로 호출 ===")
    f = ManagedFile("data.txt")
    f.__enter__()
    f.write("hello")
    f.__exit__(None, None, None)
    print("closed:", f.closed)

    print()
    print("=== 2) 처리 중 예외가 나도 __exit__은 반드시 호출된다 (수동 흉내) ===")
    f2 = ManagedFile("data2.txt")
    f2.__enter__()
    try:
        f2.write("hello")
        raise RuntimeError("처리 중 에러 발생!")
    except Exception as exc:
        f2.__exit__(type(exc), exc, exc.__traceback__)
        print("closed:", f2.closed)
        print(f"__exit__이 False를 반환했으므로 예외는 그대로 다시 던져진다: {exc}")

    print()
    print("=== 3) __exit__이 True를 반환하면 예외가 삼켜진다 ===")
    r = SuppressingResource()
    r.__enter__()
    try:
        raise ValueError("삼켜질 예외")
    except Exception as exc:
        swallowed = r.__exit__(type(exc), exc, exc.__traceback__)
        print("swallowed:", swallowed)

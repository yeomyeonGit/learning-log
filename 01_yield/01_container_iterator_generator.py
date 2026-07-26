import time
import tracemalloc

# 이터레이터 클래스, 제너레이터, list 버전의 정확성 + 성능(시간/메모리) 비교


class ReverseIterator:
    def __init__(self, data):
        self.data = data
        self.position = len(self.data) - 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.position < 0:
            raise StopIteration
        result = self.data[self.position]
        self.position -= 1
        return result


def reverse_generator(data):
    for i in range(len(data) - 1, -1, -1):
        yield data[i]

def plain_generator():
    yield 3
    yield 2
    yield 1
    

def reverse_list(data):
    result = []
    for i in range(len(data) - 1, -1, -1):
        result.append(data[i])
    return result


def measure(label, run):
    tracemalloc.start()
    start_time = time.perf_counter()

    total = 0
    for value in run():
        total += value

    elapsed = time.perf_counter() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(
        f"[{label}] 처리 시간: {elapsed:.4f}초, "
        f"피크 메모리: {peak / 1024:.2f} KB, "
        f"총합(검증용): {total}"
    )


if __name__ == "__main__":
    raw_data = [1, 2, 3]

    print("=== 원본 데이터 ===")
    print(raw_data)

    print("=== 이터레이터 클래스 버전 ===")
    it_ob = ReverseIterator(raw_data)
    print(type(it_ob))
    for item in it_ob:
        print(item, type(item))
        
    try:
        next(it_ob)
    except StopIteration:
        print("StopIteration 발생 확인")
    
    print("=== 이터레이터 iter() 함수 버전 ===")

    it_func = iter(raw_data)

    print("--- 1) for 문으로 next 자동 함수 호출 ---" )
    
    for item in it_func:
        print(item, type(item))
    
    print("--- 2) next() 함수로 명시적 함수 호출 ---" )

    try: 
        print(next(it_func), type(it_func))
    except StopIteration:
        print("StopIteration 발생 확인")

    print("=== 제너레이터 버전 ===")
    print("--- 1) input data: 이터러블 객체 ---" )

    g = reverse_generator(raw_data)
    print(type(g))
    print(next(g), type(g))
    print(next(g), type(g))
    print(next(g), type(g))
    try:
        next(g)
    except StopIteration:
        print("StopIteration 발생 확인")

    print("--- 2) input data: 없음 ---" )
    pl_g = plain_generator()
    
    print(type(pl_g))
    print(next(pl_g), type(pl_g))
    print(next(pl_g), type(pl_g))
    print(next(pl_g), type(pl_g))
    try:
        next(g)
    except StopIteration:
        print("StopIteration 발생 확인")

    print("=== list 버전 ===")
    lst = reverse_list(raw_data)
    print(lst, type(lst))

    print()
    print("=== 성능 비교 (N=1,000,000) ===")
    N = 1_000_000
    big_data = list(range(N))

    measure("class", lambda: ReverseIterator(big_data))
    measure("generator", lambda: reverse_generator(big_data))
    measure("list", lambda: reverse_list(big_data))

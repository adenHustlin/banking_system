import functools
import time


def retry(exceptions, tries=3, delay=1, backoff=2):
    """
    SQLite는 데이터베이스 테이블이 잠겼을 때 바로 에러를 던지므로,
    이 문제를 해결하기 위해 retry 데코레이터를 사용하여 잠금이 해제될 때까지
    트랜잭션을 재시도합니다.
    """

    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper_retry(*args, **kwargs):
            _tries, _delay = tries, delay
            while _tries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(f"{e}, Retrying in {_delay} seconds...")
                    time.sleep(_delay)
                    _tries -= 1
                    _delay *= backoff
            return func(*args, **kwargs)

        return wrapper_retry

    return decorator_retry

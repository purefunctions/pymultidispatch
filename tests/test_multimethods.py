from pymultidispatch.multimethods import multimethod
import pytest


def test_non_callable_key_fn_raises_error():
    with pytest.raises(TypeError) as e:

        @multimethod(key_fn=None)
        def multi():
            pass


def test_define_multimethod_creation():
    @multimethod(key_fn=lambda x: x)
    def multi(x):
        return x

    @multimethod(lambda x: x)
    def multi_1(x):
        return x

    def key_gen(x):
        return x

    @multimethod(key_gen)
    def multi_2(x):
        return x


def test_multimethod_registration():
    @multimethod(key_fn=lambda x: x)
    def multi(x):
        return "default handler was called"

    @multi.register(1)
    def _(x):
        return str(x + 1)

    multi.register(3)(lambda x: str(x + 3))

    @multi.register(2)
    def _(x):
        return str(x + 2)

    assert multi(1) == "2"
    assert multi(2) == "4"
    assert multi(3) == "6"
    assert multi(-1) == "default handler was called"

    assert set(multi.registered_keys()) == {1, 2, 3}


def test_multimethod_duplicate_registration():
    @multimethod(key_fn=lambda x: x)
    def multi(x):
        return "default"

    @multi.register(1)
    def _(x):
        return str(x + 1)

    with pytest.raises(KeyError) as excinfo:

        @multi.register(1)
        def _(x):
            return str(x + 2)

    assert "key 1" in str(excinfo.value)
    assert "multi" in str(excinfo.value)


def test_multimethod_duplicate_registration_with_overwrite():
    @multimethod(key_fn=lambda x: x)
    def multi(x):
        return "default"

    @multi.register(1)
    def _(x):
        return str(x)

    assert multi(1) == "1"

    @multi.register(1, overwrite=True)
    def _(x):
        return str(x + 1)

    assert multi(1) == "2"


def test_multimethod_registration_hashable_check():
    @multimethod(key_fn=lambda x: x)
    def multi(x):
        pass

    with pytest.raises(TypeError) as excinfo:

        @multi.register([])
        def _(x):
            return x

    assert "[]" in str(excinfo.value)
    assert "multi" in str(excinfo.value)


def test_multimethod_key_gen_hashable_check():
    @multimethod(key_fn=lambda x: [x])
    def multi(x):
        pass

    @multi.register(1)
    def _(x):
        return str(x)

    with pytest.raises(TypeError) as excinfo:
        multi(1)

    assert "lambda" in str(excinfo.value)


def test_decorated_functions_retain_names():
    @multimethod(key_fn=lambda x: x)
    def multi(x):
        return "default"

    @multi.register(1)
    def multi_1(x):
        return str(x + 1)

    @multi.register(2)
    def multi_2(x):
        return str(x + 2)

    assert multi.__name__ == "multi"
    assert multi_1.__name__ == "multi_1"
    assert multi_2.__name__ == "multi_2"

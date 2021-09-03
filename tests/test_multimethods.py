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


def test_default_handler_with_default_params():
    @multimethod(key_fn=lambda x, y, z: type(x))
    def type_info(x, y=1, z=2):
        return NotImplementedError

    @type_info.register(int)
    def _(x, y, z):
        return x, int, y, z

    @type_info.register(float)
    def _(x, y, z):
        return x, float, y, z

    assert type_info(1) == (1, int, 1, 2)
    assert type_info(1.1) == (1.1, float, 1, 2)


def test_with_call_site_defaults_only():
    @multimethod(key_fn=lambda x, y, z: type(x))
    def type_info(x, y, z):
        return NotImplementedError

    @type_info.register(int)
    def _(x, y, z):
        return x, int, y, z

    @type_info.register(float)
    def _(x, y, z):
        return x, float, y, z

    assert type_info(1, z=2, y=1) == (1, int, 1, 2)
    assert type_info(1.1, y=1, z=2) == (1.1, float, 1, 2)


def test_that_call_site_defaults_override_default_params_of_default_handler():
    @multimethod(key_fn=lambda x, y, z, zz: type(x))
    def type_info(x, y="a", z="b", zz="c"):
        return NotImplementedError

    @type_info.register(int)
    def _(x, y, z, zz):
        return x, int, y, z, zz

    @type_info.register(float)
    def _(x, y, z, zz):
        return x, float, y, z, zz

    assert type_info(1, z="2", y="1") == (1, int, "1", "2", "c")
    assert type_info(1.1, zz="2") == (1.1, float, "a", "b", "2")


def test_that_multimethod_registration_with_default_params_fails():
    @multimethod(key_fn=lambda x, y, z, zz: type(x))
    def type_info(x, y="a", z="b", zz="c"):
        return NotImplementedError

    with pytest.raises(ValueError):
        @type_info.register(int)
        def _(x, y, z, zz=1):
            return x, int, y, z, zz


def test_multimethod_registration_with_more_keys_passes():
    @multimethod(key_fn=lambda x, y, z, zz: type(x))
    def type_info(x, y="a", z="b", zz="c"):
        return NotImplementedError

    @type_info.register(int, float, str)
    def _(x, y, z, zz):
        return (int, float, str)

    @type_info.register(bool)
    def _(x, y, z, zz):
        return x, bool, y, z, zz

    assert type_info(1, z="2", y="3") == (int, float, str)
    assert type_info(1.1, z="2", y="3") == (int, float, str)
    assert type_info("1", z="2", y="3") == (int, float, str)
    assert type_info(True, z="2", y="3") == (True, bool, "3", "2", "c")


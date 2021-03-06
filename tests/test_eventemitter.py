import unittest
import gevent
import gevent.event

from eventemitter import EventEmitter

class EETestCase(unittest.TestCase):
    def setUp(self):
        class Dummy(EventEmitter):
            pass

        self.dummy = Dummy()
        self.calls = 0

    def idle(self):
        for _ in range(100):
            gevent.idle()

    def test_emit_with_args(self):
        @self.dummy.on('one')
        def func_one(a):
            self.calls += a

        @self.dummy.on('two')
        def func_two(a, b):
            self.calls += a + b

        self.dummy.emit('one', 1)
        self.dummy.emit('two', 10, 100)

        self.idle()
        self.assertEqual(self.calls, 111)

        self.dummy.emit('one', 1)
        self.dummy.emit('two', 10, 100)

        self.idle()
        self.assertEqual(self.calls, 222)

    def test_emit_async(self):
        result = gevent.event.AsyncResult()
        self.dummy.on('event', result)
        self.dummy.emit('event', 1)

        self.assertEqual(result.get(block=True, timeout=1), (1,))

        result2 = gevent.event.AsyncResult()
        self.dummy.on('event', result2)
        self.dummy.emit('event', 1, 2, 3)

        self.idle()
        self.assertEqual(result2.get(block=True, timeout=1), (1, 2, 3))

    def test_on(self):
        def func_one():
            self.calls += 1

        def func_two():
            self.calls += 10

        self.dummy.on('event', func_one)
        self.dummy.on('event', func_two)
        self.dummy.emit('event')

        self.idle()
        self.assertEqual(self.calls, 11)

    def test_on_decorator(self):
        @self.dummy.on('event')
        def func_one():
            self.calls += 1

        @self.dummy.on('event')
        def func_two():
            self.calls += 10

        self.dummy.emit('event')

        self.idle()
        self.assertEqual(self.calls, 11)

    def test_once(self):
        def func_one():
            self.calls += 1

        self.dummy.once('event', func_one)
        self.dummy.emit('event')
        self.dummy.emit('event')

        self.idle()
        self.assertEqual(self.calls, 1)

    def test_once_decorator(self):
        @self.dummy.once('event')
        def func_one():
            self.calls += 1

        self.dummy.emit('event')
        self.dummy.emit('event')

        self.idle()
        self.assertEqual(self.calls, 1)

    def test_wait_event(self):
        def tiny_worker():
            self.dummy.wait_event('event')

        g = gevent.spawn(tiny_worker)
        self.idle()

        self.dummy.emit('event')

        self.idle()
        g.get(block=False)

    def test_wait_event_with_timeout(self):
        def tiny_worker():
            resp = self.dummy.wait_event('event', timeout=0)
            self.assertIsNone(resp)

            resp = self.dummy.wait_event('event', timeout=0, raises=False)
            self.assertIsNone(resp)

            with self.assertRaises(gevent.Timeout):
                self.dummy.wait_event('event', timeout=0, raises=True)

        g = gevent.spawn(tiny_worker)
        g.join(2)

        self.assertTrue(g.ready())

    def test_remove_listener(self):
        self.dummy.remove_listener('event', None)

        @self.dummy.once('event')
        def func_one():
            self.calls += 1

        self.dummy.remove_listener('event', func_one)
        self.dummy.emit('event')
        self.dummy.emit('event')
        self.dummy.emit('event')

        self.idle()
        self.assertEqual(self.calls, 0)

    def test_remove_all_listeners(self):
        @self.dummy.once('event')
        def func_one():
            self.calls += 1

        @self.dummy.once('event')
        def func_two():
            self.calls += 10

        @self.dummy.once('other')
        def func_three():
            self.calls += 100

        self.dummy.remove_all_listeners()
        self.dummy.emit('event')
        self.dummy.emit('other')

        self.idle()
        self.assertEqual(self.calls, 0)

    def test_remove_all_listeners_for_event(self):
        @self.dummy.once('event')
        def func_one():
            self.calls += 1

        @self.dummy.once('event')
        def func_two():
            self.calls += 10

        @self.dummy.once('other')
        def func_three():
            self.calls += 100

        self.dummy.remove_all_listeners('event')
        self.dummy.emit('event')
        self.dummy.emit('other')

        self.idle()
        self.assertEqual(self.calls, 100)

    def test_callback_call_order(self):
        result = []

        def c():
            result.append(1)
        def bbb_bbb_bbb():
            result.append(2)
        def aaa():
            result.append(3)

        self.dummy.on('event', aaa)
        self.dummy.on('event', bbb_bbb_bbb)
        self.dummy.on('event', c)

        self.dummy.emit('event')

        self.idle()
        self.assertEqual(result, [3, 2, 1])

    def test_count_listeners(self):
        @self.dummy.on('event')
        def func_one():
            self.calls += 1

        self.assertEqual(self.dummy.count_listeners('event'), 1)

        self.dummy.once('event', func_one)

        self.assertEqual(self.dummy.count_listeners('event'), 1)

        self.dummy.remove_all_listeners('event')

        self.assertEqual(self.dummy.count_listeners('event'), 0)

    def test_count_listeners_with_no_listeners(self):
        self.assertEqual(self.dummy.count_listeners(None), 0)
        self.assertEqual(self.dummy.count_listeners('event'), 0)
        self.assertEqual(self.dummy.count_listeners(''), 0)
        self.assertEqual(self.dummy.count_listeners(1), 0)
        self.assertEqual(self.dummy.count_listeners(0), 0)

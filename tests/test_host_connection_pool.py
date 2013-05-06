from mock import Mock, NonCallableMagicMock
from threading import Thread, Event
import unittest

from cassandra.cluster import Session
from cassandra.connection import Connection
from cassandra.pool import Host, HostConnectionPool, NoConnectionsAvailable
from cassandra.policies import HostDistance

class HostConnectionPoolTests(unittest.TestCase):

    def make_session(self):
        session = NonCallableMagicMock(spec=Session, keyspace='foobarkeyspace')
        session.cluster.get_core_connections_per_host.return_value = 1
        session.cluster.get_max_requests_per_connection.return_value = 1
        session.cluster.get_max_connections_per_host.return_value = 1
        return session

    def test_borrow_and_return(self):
        host = Mock(spec=Host, address='ip1')
        session = self.make_session()
        conn = NonCallableMagicMock(spec=Connection, in_flight=0, is_defunct=False, is_closed=False)
        session.cluster.connection_factory.return_value = conn

        pool = HostConnectionPool(host, HostDistance.LOCAL, session)
        session.cluster.connection_factory.assert_called_once_with(host.address)

        c = pool.borrow_connection(timeout=0.01)
        self.assertIs(c, conn)
        self.assertEqual(1, conn.in_flight)
        conn.set_keyspace.assert_called_once_with('foobarkeyspace')

        pool.return_connection(conn)
        self.assertEqual(0, conn.in_flight)
        self.assertNotIn(conn, pool._trash)

    def test_failed_wait_for_connection(self):
        host = Mock(spec=Host, address='ip1')
        session = self.make_session()
        conn = NonCallableMagicMock(spec=Connection, in_flight=0, is_defunct=False, is_closed=False)
        session.cluster.connection_factory.return_value = conn

        pool = HostConnectionPool(host, HostDistance.LOCAL, session)
        session.cluster.connection_factory.assert_called_once_with(host.address)

        pool.borrow_connection(timeout=0.01)
        self.assertEqual(1, conn.in_flight)

        # we're already at the max number of requests for this connection,
        # so we this should fail
        self.assertRaises(NoConnectionsAvailable, pool.borrow_connection, 0)

        pool.return_connection(conn)
        self.assertEqual(0, conn.in_flight)

    def test_successful_wait_for_connection(self):
        host = Mock(spec=Host, address='ip1')
        session = self.make_session()
        conn = NonCallableMagicMock(spec=Connection, in_flight=0, is_defunct=False, is_closed=False)
        session.cluster.connection_factory.return_value = conn

        pool = HostConnectionPool(host, HostDistance.LOCAL, session)
        session.cluster.connection_factory.assert_called_once_with(host.address)

        pool.borrow_connection(timeout=0.01)
        self.assertEqual(1, conn.in_flight)

        def get_second_conn():
            c = pool.borrow_connection(1.0)
            self.assertIs(conn, c)
            pool.return_connection(c)

        t = Thread(target=get_second_conn)
        t.start()

        pool.return_connection(conn)
        t.join()
        self.assertEqual(0, conn.in_flight)

    def test_all_connections_trashed(self):
        host = Mock(spec=Host, address='ip1')
        session = self.make_session()
        conn = NonCallableMagicMock(spec=Connection, in_flight=0, is_defunct=False, is_closed=False)
        session.cluster.connection_factory.return_value = conn
        session.cluster.get_core_connections_per_host.return_value = 1

        # manipulate the core connection setting so that we can
        # trash the only connection
        pool = HostConnectionPool(host, HostDistance.LOCAL, session)
        session.cluster.get_core_connections_per_host.return_value = 0
        pool._trash_connection(conn)
        session.cluster.get_core_connections_per_host.return_value = 1

        submit_called = Event()

        def fire_event(*args, **kwargs):
            submit_called.set()

        session.submit.side_effect = fire_event

        def get_conn():
            c = pool.borrow_connection(1.0)
            self.assertIs(conn, c)
            self.assertEqual(1, conn.in_flight)
            conn.set_keyspace.assert_called_once_with('foobarkeyspace')
            pool.return_connection(c)

        t = Thread(target=get_conn)
        t.start()

        submit_called.wait()
        self.assertEqual(1, pool._scheduled_for_creation)
        session.submit.assert_called_once_with(pool._create_new_connection)

        # now run the create_new_connection call
        pool._create_new_connection()

        t.join()
        self.assertEqual(0, conn.in_flight)

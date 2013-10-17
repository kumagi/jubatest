# -*- coding: utf-8 -*-

from jubatest import *
from jubatest.unit import JubaSkipTest
from jubatest.remote import SyncRemoteProcess

import json

class OperationTest(JubaTestCase):

    @classmethod
    def init_benchmark_tool(cls):
        cls.bench = cls.env.get_param('JUBATUS_BENCH_CLASSIFIER')
        if not cls.bench:
            raise JubaSkipTest('JUBATUS_BENCH_CLASSIFIER parameter is not set.')
        cls.dataset = cls.env.get_param('JUBATUS_BENCH_CLASSIFIER_DATASET')
        if not cls.dataset:
            raise JubaSkipTest('JUBATUS_BENCH_CLASSIFIER_DATASET parameter is not set.')

    def run_benchmark_tool(self, query_mode, time, unit):
        args = [
            self.bench,
            '--host', self.target.node.get_host() + ':' + str(self.target.port),
            '--dataset', self.dataset,
            '--query-mode', query_mode,
            '--thread-num', '1', # fixed value
            '--dump-path', '/dev/stdout',
            '--run-time', str(time),
            '--time-unit', str(unit),
            '--silent',
        ]
        if self.name:
            args += ['--name', self.name]
        stdout = self.client_node.run_process(args)
        return json.loads(stdout)

    def test(self):
        self.run_benchmark_tool('update', 1, 0)
        sleep(20)
        result = self.run_benchmark_tool('analyze', 20, 5)
        print result

    @classmethod
    def setUpCluster(cls, env):
        cls.env = env
        cls.node0 = env.get_node(0)
        cls.cluster = env.cluster(CLASSIFIER, default_config(CLASSIFIER))
        cls.server1 = env.server(cls.node0, cls.cluster)
        cls.server2 = env.server(cls.node0, cls.cluster)
        cls.server3 = env.server(cls.node0, cls.cluster)
        cls.server4 = env.server(cls.node0, cls.cluster)
        cls.keeper1 = env.keeper(cls.node0, CLASSIFIER)
        cls.target = cls.keeper1
        cls.name = cls.cluster.name
        cls.client_node = env.get_node(0)
        cls.init_benchmark_tool()

    def setUp(self):
        for server in [self.server1, self.server2, self.server3, self.server4, self.keeper1]:
            server.start()

    def tearDown(self):
        for server in [self.server1, self.server2, self.server3, self.server4, self.keeper1]:
            server.stop()

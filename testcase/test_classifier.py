# -*- coding: utf-8 -*-

from jubatest import *
from jubatest.unit import JubaSkipTest
from jubatest.remote import SyncRemoteProcess

import json

class ClassifierAPIPerformanceTestBase():
    @classmethod
    def init_benchmark_tool(cls):
        cls.bench = cls.env.get_param('JUBATUS_BENCH_CLASSIFIER')
        if not cls.bench:
            raise JubaSkipTest('JUBATUS_BENCH_CLASSIFIER parameter is not set.')
        cls.dataset = cls.env.get_param('JUBATUS_BENCH_CLASSIFIER_DATASET')
        if not cls.dataset:
            raise JubaSkipTest('JUBATUS_BENCH_CLASSIFIER_DATASET parameter is not set.')

    def run_benchmark_tool(self, query_mode, threads):
        args = [
            self.bench,
            '--host', self.target.node.get_host() + ':' + str(self.target.port),
            '--dataset', self.dataset,
            '--query-mode', query_mode,
            '--thread-num', str(threads),
            '--dump-path', '/dev/stdout',
            '--silent',
        ]
        if self.name:
            args += ['--name', self.name]
        stdout = self.client_node.run_process(args)
        return json.loads(stdout)

    def test_update_performance(self):
        result = self.run_benchmark_tool('update', 1)
        self.attach_record({
            'Throughput (QPS)': result['summary']['throughput_QPS'],
            'Latency Mean (trimmed by 5%) (msec)': result['summary']['trimmed_latency_mean_msec'],
            'Latency Variance (trimmed by 5%)': result['summary']['trimmed_latency_variance'],
        })

    def test_analyze_performance(self):
        self.run_benchmark_tool('update', 1)
        result = self.run_benchmark_tool('analyze', 1)
        self.attach_record({
            'Throughput (QPS)': result['summary']['throughput_QPS'],
            'Latency Mean (trimmed by 5%) (msec)': result['summary']['trimmed_latency_mean_msec'],
            'Latency Variance (trimmed by 5%)': result['summary']['trimmed_latency_variance'],
        })

class ClassifierAPIPerformanceStandaloneTest(JubaTestCase, ClassifierAPIPerformanceTestBase):
    @classmethod
    def setUpCluster(cls, env):
        cls.env = env
        cls.server1 = env.server_standalone(env.get_node(0), CLASSIFIER, default_config(CLASSIFIER))
        cls.target = cls.server1
        cls.name = ''
        cls.client_node = env.get_node(0)
        cls.init_benchmark_tool()

    def setUp(self):
        self.server1.start()

    def tearDown(self):
        self.server1.stop()

class ClassifierAPIPerformanceDistributedTest(JubaTestCase, ClassifierAPIPerformanceTestBase):
    @classmethod
    def setUpCluster(cls, env):
        cls.env = env
        cls.node0 = env.get_node(0)
        cls.cluster = env.cluster(CLASSIFIER, default_config(CLASSIFIER))
        cls.server1 = env.server(cls.node0, cls.cluster)
        cls.server2 = env.server(cls.node0, cls.cluster)
        cls.server3 = env.server(cls.node0, cls.cluster)

class ClassifierAPIPerformanceStandaloneTest(JubaTestCase, ClassifierAPIPerformanceTestBase):
    @classmethod
    def setUpCluster(cls, env):
        cls.env = env
        cls.server1 = env.server_standalone(env.get_node(0), CLASSIFIER, default_config(CLASSIFIER))
        cls.target = cls.server1
        cls.name = ''
        cls.client_node = env.get_node(0)
        cls.init_benchmark_tool()

    def setUp(self):
        self.server1.start()

    def tearDown(self):
        self.server1.stop()

class ClassifierAPIPerformanceDistributedTest(JubaTestCase, ClassifierAPIPerformanceTestBase):
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

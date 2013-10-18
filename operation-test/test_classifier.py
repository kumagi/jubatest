# -*- coding: utf-8 -*-

from jubatest import *
from jubatest.unit import JubaSkipTest
from jubatest.remote import SyncRemoteProcess

import json
from multiprocessing.pool import ThreadPool
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.cm as cm
import matplotlib.dates as dts

class OperationTest(JubaTestCase):

    @classmethod
    def init_benchmark_tool(cls):
        cls.bench = cls.env.get_param('JUBATUS_BENCH_CLASSIFIER')
        if not cls.bench:
            raise JubaSkipTest('JUBATUS_BENCH_CLASSIFIER parameter is not set.')
        cls.dataset = cls.env.get_param('JUBATUS_BENCH_CLASSIFIER_DATASET')
        if not cls.dataset:
            raise JubaSkipTest('JUBATUS_BENCH_CLASSIFIER_DATASET parameter is not set.')

    @classmethod
    def get_jubatus_config(cls):
        cls.config_path = cls.env.get_param('JUBATUS_CONFIG_PATH')
        if not cls.config_path:
            return default_config(CLASSIFIER)
        return json.loads(open(cls.config_path).read())

    @classmethod
    def get_cluster_name(cls):
        if not cls.env.get_param('CLUSTER_NAME'):
            return None
        return cls.env.get_param('CLUSTER_NAME')

    def run_benchmark_tool(self, target):
        args =[
            self.bench,
            '--host', target[1].node.get_host() + ':' + str(target[1].port),
            '--name', self.name,
            '--dataset', self.dataset,
            '--tag', target[1].node.get_host() + ':' + str(target[1].port),
            '--query-mode', target[2],
            '--run-time', str(target[3]),
            '--time-unit', str(target[4]),
            '--dump-path', '/dev/stdout',
            '--thread-num', str(1), # fixed value
            '--silent'
            ]
        stdout = target[0].run_process(args)
        return json.loads(stdout)

    @classmethod
    def setUpCluster(cls, env):
        cls.env = env

        # Create Node Instance
        cls.server_node1 = env.get_node(0)
        cls.server_node2 = env.get_node(1)
        cls.server_node3 = env.get_node(2)
        cls.keeper_node1 = env.get_node(3)
        cls.keeper_node2 = env.get_node(4)
        cls.client_node1 = cls.keeper_node1
        cls.client_node2 = cls.keeper_node2

        # Create Cluster
        cls.name = cls.get_cluster_name()
        cls.cluster = env.cluster(CLASSIFIER, cls.get_jubatus_config(), cls.name)
        cls.server1 = env.server(cls.server_node1, cls.cluster)
        cls.server2 = env.server(cls.server_node2, cls.cluster)
        cls.server3 = env.server(cls.server_node3, cls.cluster)
        cls.keeper1 = env.keeper(cls.keeper_node1, CLASSIFIER)
        cls.keeper2 = env.keeper(cls.keeper_node2, CLASSIFIER)

        # Initialize benchmark tool
        cls.init_benchmark_tool()

    def setUp(self):
        for server in [self.server1, self.server2, self.server3, self.keeper1, self.keeper2]:
            server.start()

    def tearDown(self):
        for server in [self.server1, self.server2, self.server3, self.keeper1, self.keeper2]:
            server.stop()

    def drow_graphs(self, results):
        timelines = {}
        means = {}
        variances = {}
        nums = {}
        success_nums = {}
        wrong_nums = {}
        error_nums = {}
        exception_nums = {}
        for result in results:
            host = result['summary']['tag']
            timeline = []
            mean = []
            variance = []
            num = []
            success_num = []
            wrong_num = []
            error_num = []
            exception_num = []
            timespan_result = result['timespan_results']['0']
            times = timespan_result.keys()
            for time in sorted(times):
                timeline.append(datetime.fromtimestamp(float(time)))
                mean.append(timespan_result[time]['mean'])
                variance.append(timespan_result[time]['variance'])
                num.append(timespan_result[time]['num'])
                success_num.append(timespan_result[time]['success_num'])
                wrong_num.append(timespan_result[time]['wrong_num'])
                error_num.append(timespan_result[time]['error_num'])
                exception_num.append(timespan_result[time]['exception_num'])
            timelines[host] = timeline
            means[host] = mean
            variances[host] = variance
            nums[host] = num
            success_nums[host] = success_num
            wrong_nums[host] = wrong_num
            error_nums[host] = error_num
            exception_nums[host] = exception_num
        self.drow_graph(timelines, 'latency-mean (sec)', means)
        self.drow_graph(timelines, 'latency-variances', variances)
        self.drow_graph(timelines, 'queries', nums)
        self.drow_graph(timelines, 'success queries', success_nums)
        self.drow_graph(timelines, 'wrong queries', wrong_nums)
        self.drow_graph(timelines, 'error queries', error_nums)
        self.drow_graph(timelines, 'exception queries', exception_nums)

    def drow_graph(self, timelines, title, values):
        d_min = datetime.max
        d_max = datetime.min
        v_min = 0
        v_max = 0
        for host in timelines.keys():
            if min(timelines[host]) < d_min: d_min = min(timelines[host])
            if max(timelines[host]) > d_max: d_max = max(timelines[host])
            if min(values[host]) < v_min: v_min = min(values[host])
            if max(values[host]) > v_max: v_max = max(values[host])

        idx = 0
        for host in timelines.keys():
            plt.plot_date(
                timelines[host],
                values[host],
                label = host,
                color = cm.hsv(float(idx)/len(timelines.keys())),
                linestyle = '-',
                marker = '.',
                markersize = 5
            )
            idx += 1
        plt.title(title)
        plt.xticks(fontsize = 10)
        plt.yticks(fontsize = 10)
        if (v_min == v_max): v_max = v_min + 1
        plt.axis([d_min, d_max, v_min, v_max * 1.1])
        plt.subplot(111).xaxis.set_major_formatter(dts.DateFormatter('%H:%M:%S'))
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(title + '.png')
        plt.clf()

    """
    Main processing
    (Method Name is `test` Because using jubatest-framework)
    """
    def test(self):
        targets = []
        # tupple
        #  (client_node, keeper, query_type, run_time, time_unit)
        targets.append((self.client_node1, self.keeper1, 'update', 60, 1))
        targets.append((self.client_node2, self.keeper2, 'update', 60, 1))

        pool = ThreadPool(processes=len(targets))
        self.drow_graphs(pool.map(self.run_benchmark_tool, targets))

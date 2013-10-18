# ----------------------------- #
#  Test Environment Definition  #
# ----------------------------- #

homedir = '/home/imama-r'

# PREFIX of Jubatus
env.prefix(homedir + '/local')

# Work Directory (default: '/tmp')
#  * Used to `--datadir` option
env.workdir(homedir + '/tmp')

# Environment values
#  * Used to start Jubatus
env.variable('LD_LIBRARY_PATH', homedir + '/local/lib')

# Prefix of Jubatus Cluster Name (default: '')
# env.cluster_prefix('prefix')

# Node
#  * Define host and pool of port
#  * Able to define pool of port by list
#  * Added to list if you define
#  * Used to run Jubatus Server and Keeper
env.node('127.0.0.1', range(19001, 19100))
env.node('127.0.0.1', [19101, 19102, 19103])
env.node('127.0.0.1', 19201)
env.node('127.0.0.1', 19301)
env.node('127.0.0.1', 19401)

# ZooKeeper
#  * Define host and port
#  * Added to list if you define
#  * Used to start Jubatus and `jubaconfig`
env.zookeeper('127.0.0.1', 2181)
# env.zookeeper('127.0.0.1', 2182)
# env.zookeeper('127.0.0.1', 2183)


# User defined parameter
#  * Define key and value
bench_home = homedir + '/work/github/rimms/jubatus-benchmark'
env.param('CLUSTER_NAME', 'mytest')
env.param('JUBATUS_BENCH_CLASSIFIER', bench_home + '/build/classifier/jubatus-bench-classifier')
env.param('JUBATUS_BENCH_CLASSIFIER_DATASET', bench_home + '/url_svmlight/Day0.svm')
env.param('JUBATUS_CONFIG_PATH', homedir + '/local/share/jubatus/example/config/classifier/arow.json')


See Also https://github.com/rimms/jubatest/blob/master/README.rst

## How to Use

To run the operation tests :

```
$ cd ../
$ PYTHONPATH=lib bin/jubatest --config operation-test/myenv.py --testcase operation-test/ --pattern "test*"
```

## Edit myenv.py

See Also https://github.com/rimms/jubatest/tree/for_operation_test/operation-test/myenv.py

## Scenario

1. Startup Keepers from entries of myenv.py
2. Run benchmark-tool
3. Drow graph
4. Shutdown Keepers 

## How to change Scenario

### Running time of Benchmark Tool

update `60` as following:

```python
def test(self):
    targets.append((self.client_node1, self.keeper1, 'update', 60, 1, timeout))
```
### Time span of Stats

update `1` as following:

```python
def test(self):
    targets.append((self.client_node1, self.keeper1, 'update', 60, 1, timeout))
```

### Graph

update following method:

```python
def drow_graph(self, timelines, title, values):
```
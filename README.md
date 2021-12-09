# wickerGen
this tool can be used to generate 3d wicker patterns for building components. At our University, the Karlsruhe Institute of Technology in Germany, we will use this to weave willow branches with a fleet of robots driving on the floor, each holding a branch.

The tool computes the pattern based on knot positions and knot connections which are given as input.

## usage
```python3 main.py --show3d --showcombined --showgraph --animate```

add ```--smallmodel``` to only show a single knot (is 20x faster)

## single knot
the 2D animation shows how three bundles, consisting of 4, 8, and 4 strands of willow move around each other to form a knot.

<img src="https://github.com/ottozastrow/wickerGen/blob/3ea97578f3346ccb5ad527fe53d3a53e3e7b73f5/images/3d%20knot%20with%203%20inputs.png" width="30%"/>

![2d video animation](https://youtu.be/vFCoQ6GhMaU)


## several knots combined to module
This graph is the input to the wickerGen tool.

![3d video animation](https://youtu.be/ixJlgMRt51A)


<img style="float: left;" src="https://github.com/ottozastrow/wickerGen/blob/a4458d3a5dc8888d48d74b991b4385bf3921aa22/images/module%20graph.png" width="35%"/>


From this graph the braiding movement of strands in 3d across time is generated.

<img style="float: left;" src="https://github.com/ottozastrow/wickerGen/blob/a4458d3a5dc8888d48d74b991b4385bf3921aa22/images/snip%20from%203d%20braid%20video.png" width="60%"/>



The 3d lines output can be saved as obj (by setting an obj path with ```--obj_path```. This format can be opened with rhino. In Rhino these lines can be made to pipes with the rebuild(200) and Pipe(0.004) commands. The result looks like this:

<img src="https://github.com/ottozastrow/wickerGen/blob/aa4d645499e42305e3c282427227b58d925d0c1f/images/3d%20braided%20visualization.jpeg"/>


feel free to reach out via GitHub or LinkedIn if you have any questions


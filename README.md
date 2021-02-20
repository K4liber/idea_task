# idea_task
To run the interactive visualization type the command:  
`./build_and_run.sh`  
or if you want to build the docker image based on alpine:  
`./build_and_run.sh DockerfileAlpine`  
It takes a lot more time to build from the alpine image.  
Type the address below into your browser and have fun:
`http://127.0.0.1:8050/`  
## Instructions for use 
There are two use cases: 
1. Show the network state in the specific hour.
To do this just select the same hour on input fields at bottom corners.*
2. Show the difference between network states for selected hours.
The differences are shown as simple nodes colors (demand difference) and arrow sizes (flow difference).

*You can use the bottom slider to change the hours.
## Elements of the visualization
1. Simple nodes - nodes that are not generators. Marked as circles.
2. Generators - nodes that are generators. Marked as circles with symbol "X" or "+" inside them, where:  
"+" - node type 2  
"X" - node type 3
3. Branches - branch between two nodes. Marked as grey lines.
4. Arrows - show the difference between branches flows for selected hours.
5. The scale on the left - shows the balance of the cost for generators, where:  
balance = generation - demand
6. The scale on the right - shows the difference between simple node demands for selected hours.

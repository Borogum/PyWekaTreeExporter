# PyWekaTreeExporter

A little python script to transform Weka tree classifier text output into a graphviz file.

## Usage example

You can create a simple weka's workflow to automate things. We need two files, a text representation of tree ( tree.txt ) and the tree train data ( train.csv ).

![Weka workflow](https://raw.githubusercontent.com/Borogum/PyWekaTreeExporter/master/images/workflow.png)


Execute the python script

```bash
python tree2graph.py tree.txt train.csv tree.gv
```

Finally you can use dot util to transform graphviz file to a image file.

```bash
  dot -q -Tpng tree.gv -o tree.png
```
for png file  or

```bash
  dot -q -Tsvg tree.svg -o tree.svg
```

for svg file

### Results

Ugly weka tree:

![Ugly tree](https://raw.githubusercontent.com/Borogum/PyWekaTreeExporter/master/images/ugly_tree.png)

Beautiful version:

![Beautiful tree](https://raw.githubusercontent.com/Borogum/PyWekaTreeExporter/master/images//beautiful_tree.png)

**Note 1:** *dot* util can be found at  https://www.graphviz.org/

**Note 2:** Any comment is welcomed

**Note 3:** Use it at your own risk ;P

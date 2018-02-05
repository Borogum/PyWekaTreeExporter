import argparse


class Rule(object):

    ''' '''

    def __init__(self,field,operator,value):

        self.field=field
        self.operator=self.get_operator(operator)
        self.value=value


    def get_operator(self,operator):

        if operator=='<':
            return (lambda x,y : x<y)
        elif operator=='>':
            return (lambda x,y : x>y)
        elif operator=='<=':
            return (lambda x,y : x<=y)
        elif operator=='>=':
            return (lambda x,y : x>=y)
        elif operator=='=':
            return (lambda x,y : x==y)
        else:
            return lambda x,y: True



    def check(self,data):

        return self.operator(data[self.field],self.value)

class AllRule (object):

    ''' '''

    def check(self,data):

        return True



class Node(object):

    ''' '''

    def __init__(self,n):

        self.n=n
        self.depth=0 #or -1
        self.level=None
        self.parent=None
        self.childs=[]
        self.split_feature=None # Para abajo
        self.split_operator=None
        self.split_value=None
        self.samples=0
        self.value=None # sorted by calesses
        self.value_label=None
        self.rule=AllRule()


    def __repr__(self):

        return 'node'+str(self.n)


    def append(self,node):

        node.parent=self
        self.childs.append(node)


    def check_rules(self,data):

        ''' '''
        current=self
        ck=current.rule.check(data)
        if ck:
            while current.parent is not None:
                if not current.parent.rule.check(data):
                    return False
                current=current.parent
        return ck



class TreeParser(object):

    ''' '''

    def __init__(self,tree_file,data_file):

        self.__tree_file=tree_file
        self.__data_file=data_file


    def __get_level(self,l):

        ''' '''

        return sum(x=='|' for x in l)


    def __math_index(self,l):

        ''' '''

        for s in ['<=','>=','<','>','=']:
            i=l.find(s)
            if  i!=-1:
                return (s,i)
        return (None,-1)


    def __process(self,l):

        ''' Extract info from file line by line '''

        feature=None
        value=None
        level=None
        s,i=self.__math_index(l)
        if s is not None:
            level=self.__get_level(l)
            c=l.split(s)
            feature=c[0].strip().replace('|   ','')
            if c[1].find(':') != -1:
                c=c[1].split(':')
                value=c[0].strip()
            else:
                value=c[1].strip()
        return (level,feature,s,value)


    def __get_file_info(self):

        ''' '''
        classes=set() # .add()
        with open(self.__data_file,'r') as r:
            headers=r.__next__().split(';')
            for l in r:
                classes.add(l.strip().split(';')[-1]) #last column for class
        return list(classes)


    def __assign_to_node(self,node,data,classes,instance_class):

        ''' '''
        if node.check_rules(data):
            node.samples+=1
            if node.value_label is None:
                node.value_label=classes
                node.value=[0]*len(node.value_label)
            node.value[node.value_label.index(instance_class)]+=1

        for child in node.childs:
            self.__assign_to_node(child,data,classes,instance_class)


    def __fill(self,node):

        ''' '''
        classes=self.__get_file_info()
        with open(self.__data_file,'r') as r:
            headers=r.__next__().split(';')
            for l in r:
                d=l.strip().split(';')
                self.__assign_to_node(node,{ x[0]:x[1] for x in zip(headers,d)},classes,d[-1])


    def parse(self):

        ''' '''

        with open(self.__tree_file,'r') as f:

            scheme=None
            cont=True
            while cont:
                l=f.__next__()
                if l.startswith('Scheme'):
                    scheme=l.split(':')[1].strip()
                    continue
                if scheme is not None and l.startswith(scheme):
                    cont=False
            l=f.__next__() #Skip one line
            l=f.__next__() #Skip tow lines

            last_level=-1
            n=0
            root=Node(n)
            path=[root]

            for l in f:
                level,feature,operator,value=self.__process(l)
                if level is not None:
                    n+=1
                    #Configure node
                    node=Node(n)
                    node.depth=level+1
                    node.split_feature=feature
                    node.split_operator=operator
                    node.split_value=value
                    node.rule=Rule(feature,operator,value)
                    if level <= last_level:
                        for _ in range(last_level-level+1):
                            tmp=path.pop()
                            path[-1].append(tmp)

                    path.append(node)
                    last_level=level
            for _ in range(len(path)-1):
                tmp=path.pop()
                path[-1].append(tmp)

        self.__fill(root)

        return root



class TreeExporter(object):

    ''' '''
    GRAPHVIZ_FEATURE_FONT_SIZE=10
    GRAPHVIZ_MAX=25.
    GRAPHVIZ_BAR_WIDTH=30
    GRAPHVIZ_COLOR='#777777FF#'
    GRAPHVIZ_BACKGROUND_COLOR='#FFFFFFFF#'
    GRAPHVIZ_FONT_COLOR='#222222FF#'
    GRAPHVIZ_SELECTED_FONT_COLOR='#FFFFFFFF#'
    GRAPHVIZ_SELECTED_BACKGROUND='#AAAAAAFF#'
    GRAPHVIZ_CLASS_COLORS=['#7293CBFF#','#E1974CFF#','#84BA5BFF#','#D35E60FF#',
    '#808585FF#','#9067A7FF#','#AB6857FF#','#CCC210FF#'] #TODO make more flexible

    def __init__(self,tree,out_file):

        self.__tree=tree
        self.__out_file=out_file


    def __node2str(self,node):

        ''' '''

        value = node.value
        samples=node.samples
        sorted_value=[self.GRAPHVIZ_MAX] + \
        [int(self.GRAPHVIZ_MAX * x / float(samples)) for x in sorted(value,reverse=True)] + [0]
        max_value=max(value)
        n_class=len(value)

        node_string='%s [label=<<FONT COLOR="%s" ><TABLE BORDER="1" COLOR="%s" CELLSPACING="1" VALIGN="MIDDLE" >' \
        % (node.n,self.GRAPHVIZ_FONT_COLOR,self.GRAPHVIZ_COLOR)
        node_string+='<TR><TD BORDER="0" COLSPAN="4" ALIGN="CENTER">Node %s</TD></TR>' \
        % node.n
        node_string+='<TR><TD SIDES="B" BORDER="1" ALIGN="CENTER" ></TD>'
        node_string+='<TD SIDES="B" BORDER="1" ALIGN="CENTER" >Category</TD>'
        node_string+='<TD SIDES="B" BORDER="1" ALIGN="CENTER">%</TD>'
        node_string+='<TD SIDES="B" BORDER="1" ALIGN="CENTER">n</TD></TR>'

        class_found=False
        for i in range(n_class):
            bgcolor=self.GRAPHVIZ_BACKGROUND_COLOR
            color=self.GRAPHVIZ_FONT_COLOR
            if value[i]==max_value and not class_found:
                bgcolor=self.GRAPHVIZ_SELECTED_BACKGROUND
                color=self.GRAPHVIZ_SELECTED_FONT_COLOR
                class_found=True
            node_string+='<TR><TD BGCOLOR="%s" BORDER="0" ALIGN="CENTER" >' % bgcolor
            node_string+='<FONT COLOR="%s">&#9632;</FONT></TD>' % self.GRAPHVIZ_CLASS_COLORS[i]
            node_string+='<TD BGCOLOR="%s" BORDER="0" ALIGN="CENTER" ><FONT COLOR="%s">%s</FONT></TD>' % \
            (bgcolor,color,node.value_label[i])
            node_string+='<TD BGCOLOR="%s" BORDER="0" ALIGN="CENTER" ><FONT COLOR="%s">%s</FONT></TD>' % \
            (bgcolor,color,round(100. * value[i] / float(node.samples),1))
            node_string+='<TD BGCOLOR="%s" BORDER="0" ALIGN="CENTER" ><FONT COLOR="%s">%d</FONT></TD></TR>' % \
            (bgcolor,color,value[i])


        node_string+='<TR><TD SIDES="T" BORDER="1" ALIGN="CENTER" ></TD>'
        node_string+='<TD SIDES="T" BORDER="1" ALIGN="CENTER" >Total</TD>'
        node_string+='<TD SIDES="T" BORDER="1" ALIGN="CENTER" >%s</TD>' % \
        round(100. * node.samples /float(self.__tree.samples),1)
        node_string+='<TD SIDES="T" BORDER="1" ALIGN="CENTER" >%d</TD></TR>' % \
        node.samples

        node_string+='<TR><TD COLSPAN="4" BORDER="0">'
        node_string+='<TABLE  CELLPADDING="0" CELLSPACING="0" SIDES="LB" BORDER="1" FIXEDSIZE="TRUE" HEIGHT="%s" WIDTH="%s">' % \
        (self.GRAPHVIZ_MAX,self.GRAPHVIZ_BAR_WIDTH*n_class)

        position=self.GRAPHVIZ_MAX
        for i in range(n_class+1):
            height=sorted_value[i]-sorted_value[i+1]
            if height>0:
                node_string+='<TR>'
                for j in range(n_class):
                    node_string+='<TD FIXEDSIZE="TRUE" BORDER="0" HEIGHT="%s" WIDTH="%s" BGCOLOR="%s" ></TD>' \
                    % (height,self.GRAPHVIZ_BAR_WIDTH, self.GRAPHVIZ_CLASS_COLORS[j] \
                    if self.GRAPHVIZ_MAX * value[j] / float(node.samples)>=position else self.GRAPHVIZ_BACKGROUND_COLOR)
                node_string+='</TR>'
            position-=height

        node_string+='</TABLE></TD></TR>'
        node_string+= '</TABLE></FONT>>, ];\n'

        return node_string


    def __recurse(self,node,writer,position,max_depth=None):

        if max_depth is None or node.depth <= max_depth:
            writer.write(self.__node2str(node))
            if node.parent is not None:
                if position==0:
                    #only once
                    writer.write('V%d [ label="%s" fontsize="%s" ];\n' \
                    % (node.parent.n, node.split_feature,self.GRAPHVIZ_FEATURE_FONT_SIZE))
                    writer.write('%d -> V%d [dir=none];\n' % (node.parent.n, node.parent.n))
                    #only once
                    #writer.write('V%d -> %d [label="%s%s" fontsize="%s"];\n' % \
                        #(node.parent.n, node.n,node.split_operator,node.split_value,self.GRAPHVIZ_FEATURE_FONT_SIZE)) # Posible redundant code
                #else:
                #    writer.write('V%d -> %d [label="%s%s" fontsize="%s"];\n' % \
                #        (node.parent.n, node.n,node.split_operator,node.split_value,self.GRAPHVIZ_FEATURE_FONT_SIZE)) # Posible redundant code
                writer.write('V%d -> %d [label="%s%s" fontsize="%s"];\n' % \
                      (node.parent.n, node.n,node.split_operator,node.split_value,self.GRAPHVIZ_FEATURE_FONT_SIZE))
            for i,child in enumerate(node.childs):
                self.__recurse(child,writer,i,max_depth=max_depth)


    def export(self,rotate=False,max_depth=None):

        ''' '''

        with open(self.__out_file, "w", encoding="utf-8") as out_file:
            out_file.write('digraph Tree {\n')
            out_file.write('graph [fontname = "helvetica", fontsize=15, splines=polyline, color="%s", %s];\n' \
            % (self.GRAPHVIZ_COLOR,'rankdir=LR' if rotate else '' ))
            out_file.write('node [fontname = "helvetica", shape=plaintext, color="%s"];\n' \
             % self.GRAPHVIZ_COLOR)
            out_file.write('edge [fontname = "helvetica", fontcolor="%s", color="%s"];\n' \
            % (self.GRAPHVIZ_FONT_COLOR,self.GRAPHVIZ_COLOR))
            self.__recurse(self.__tree,out_file,0,max_depth=max_depth)
            out_file.write('}\n')



if __name__ == '__main__':

    parser=argparse.ArgumentParser()
    parser.add_argument('treefile',help='Tree file')
    parser.add_argument('datafile',help='Data file')
    parser.add_argument('outfile',help='Output file')

    args = parser.parse_args()

    tp=TreeParser(args.treefile,args.datafile)
    tree=tp.parse()
    te=TreeExporter(tree,args.outfile)
    te.export(rotate=False,max_depth=None)

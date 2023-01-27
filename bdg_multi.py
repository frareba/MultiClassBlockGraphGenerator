import networkx as nx
import random as rd
import argparse
import os


'''
Returns numc non-isorphic graphs of size n which are each generated from a tree 
by appending a single edge, such that their sets of vertex degrees are equivalent.
'''
def blockgraph_layouts(n,Nc):

    while True:
        # generate random tree g of size n
        g = nx.random_tree(n=n)

        # group vertices by their degrees
        deg_grouped = {}
        for i,d in g.degree():
            if d in deg_grouped: deg_grouped[d].append(i)
            else: deg_grouped[d] = [i]

        # find vertex nC pairs (v1,v2) and (u1,u2) with d(v1)==d(u1) and d(v2)==d(u2)
        delete = [key for key in deg_grouped if len(deg_grouped[key])<Nc]
        for key in delete: del deg_grouped[key]
        if not deg_grouped: continue
        deg1 = rd.choice(list(deg_grouped.values()))
        v1 = rd.sample(deg1, Nc)
        res = [i for i in deg1 if i not in v1]
        deg1 = res
        
        delete = [key for key in deg_grouped if len(deg_grouped[key])<Nc]
        for key in delete: del deg_grouped[key]
        if not deg_grouped: continue
        deg2 = rd.choice(list(deg_grouped.values()))
        v2 = rd.sample(deg2, Nc)

        # check whether extra edges are already contained in g
        contained = False
        for i in range(Nc):
        	if v1[i]==v2[i] or (v1[i],v2[i]) in g.edges: contained = True
        if contained: continue

        # generate networkx graphs
        bgraphs = []
        for i in range(Nc):
        	h = g.copy()
        	h.add_edge(v1[i],v2[i])
        	bgraphs.append(h)
        
        # return graphs only if they are non-isomorphic
        iso = False
        for i in range(Nc):
        	for j in range(i+1, Nc):
        		if nx.is_isomorphic(bgraphs[i],bgraphs[j]): iso = True
        if iso: continue
        
        return bgraphs


'''
Returns block graph that has the underlying structure of graph g. Each node in g is replaced
by a block of c vertices. vertices within each block and of neighboring blocks are connected
with probability p. Additionally a number of m noise edges are added. 
'''
def blockgraph(g, c, p, m):

    edges = []

    # intra cluster nodes
    for v in g.nodes:
        for i in range(c):
            for j in range(i):
                if rd.random() < p:
                    edges.append((v*c+j,v*c+i))

    # inter cluster nodes
    for v in g.nodes:
        for u in g.neighbors(v):
            if v<u:
                for i in range(c):
                    for j in range(c):
                        if rd.random() < p:
                            edges.append((v*c+j,u*c+i))

    # random edges
    nmb_edges = len(edges)
    while len(edges) < nmb_edges+m:
        v = rd.randint(0, len(g.nodes)*c-1)
        u = rd.randint(0, len(g.nodes)*c-1)
        u,v = min(u,v), max(u,v)
        if v!=u and (u,v) not in edges: edges.append((v,u))

    # return networkx graph
    h = nx.Graph()
    h.add_nodes_from(range(len(g.nodes)*c))
    h.add_edges_from(edges)
    return h
    

'''
Writes graphs to file following TU Dortmund format.
'''
def write_graphs(graphs, Nc, file_name):

    if not os.path.exists(file_name):
        os.mkdir(file_name)

    f_A = open(file_name+'/'+file_name+'_A.txt', 'w')
    f_gi = open(file_name+'/'+file_name+'_graph_indicator.txt', 'w')
    f_gl = open(file_name+'/'+file_name+'_graph_labels.txt', 'w')
    f_nl = open(file_name+'/'+file_name+'_node_labels.txt', 'w')
    f_A.close()
    f_gi.close()
    f_gl.close()
    f_nl.close()

    f_A = open(file_name+'/'+file_name+'_A.txt', 'a')
    f_gi = open(file_name+'/'+file_name+'_graph_indicator.txt', 'a')
    f_gl = open(file_name+'/'+file_name+'_graph_labels.txt', 'a')
    f_nl = open(file_name+'/'+file_name+'_node_labels.txt', 'a')

    offset = 1
    for i,g in enumerate(graphs):
        for (u,v) in g.edges:
            f_A.write(str(offset+v)+', '+str(offset+u)+'\n')
            f_A.write(str(offset+u)+', '+str(offset+v)+'\n')
        for v in g.nodes:   
            f_gi.write(str(i+1)+'\n')
            f_nl.write('0\n')
        f_gl.write(str(i%Nc)+'\n')
        offset += len(g.nodes)

    f_A.close()
    f_gi.close()
    f_gl.close()
    f_nl.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Blockgraph Dataset Generator')
    parser.add_argument('--name', 
                        type=str, 
                        required=True, 
                        help='Name of output file(s)')
    parser.add_argument('--Nc', 
                        type=int, 
                        required=True, 
                        help='Number of classes')
    parser.add_argument('--N', 
                        type=int, 
                        required=True, 
                        help='Number of graphs per class')
    parser.add_argument('--n', 
                        type=int, 
                        required=True, 
                        help='Number of blocks')
    parser.add_argument('--c', 
                        type=int, 
                        required=True, 
                        help='Size of blocks')
    parser.add_argument('--p', 
                        type=float, 
                        required=True, 
                        help='Edge probability')
    parser.add_argument('--m', 
                        type=int, 
                        required=True, 
                        help='Number of noise edges')
    parser.add_argument('--seed', 
                        type=int, 
                        required=False, 
                        default=None, 
                        help='Random seed')
    args = parser.parse_args()
    
    file = args.name
    Nc = args.Nc
    N = args.N
    n = args.n
    c = args.c
    p = args.p
    m = args.m
    if args.seed: rd.seed(args.seed)

    # generate underlying block graph structures
    bgraphs = blockgraph_layouts(n,Nc)

    print("underlying block graphs generated")
    # generate N blockgraphs for each structure
    graphs = []
    for _ in range(N):
    	for g in bgraphs:
    		graphs.append(blockgraph(g, c, p, m))
    print("graphs generated")
    # write graphs to file
    write_graphs(graphs, Nc, file)
    # write parameters
    f_p = open(file+'/'+file+'_para.txt', 'w')
    f_p.write("Name 				"+ file)
    f_p.write("\nNumber of classes 		"+ str(Nc))
    f_p.write("\nNumber of graphs per class 	"+ str(N))
    f_p.write("\nNumber of blocks 		"+ str(n))
    f_p.write("\nSize of blocks 		"+ str(c))
    f_p.write("\nEdge probability 		"+ str(p))
    f_p.write("\nNumber of noise edges 	"+ str(m))
    f_p.close()

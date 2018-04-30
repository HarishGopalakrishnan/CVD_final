import networkx as nx

#get graph from file
def edge_list():
	"""
	Read graph form file
	Input: File name where 
	File format: The graph is represented by edge(vertex separated by single space) in each line
	Output: Graph G	
	"""
	G=nx.Graph()
	print("Enter File:",end='')#reads file name
	file_name=input().strip("\n")
	fp=open(file_name,"r")
	for lines in fp:
		edge=lines.strip("\n").split(" ")
		G.add_edge(edge[0],edge[1])# adds edges in to graph
	fp.close()
	return G
	
#get graph from file
def get_graph_file():
	"""
	Read graph form file
	Input: 	File name where the graph
	File format: 	First line contains the number of vertices |V|. Next |V| lines contains the vertices names. Next |V| contains the 				adjacency matrix with similarity scores (in triangular format). There is an edge between two vertices iff the 				similarity score is greater than 10.
	
	Output: Graph G	
	"""
	G=nx.Graph()
	print("Enter File:",end='')# reads the file name
	file_name=input().strip("\n")
	fp=open(file_name,"r")
	no_node=int(fp.readline().strip("\n"))# number of vertices |V|
	for i in range(no_node):
		fp.readline() # reads the name of the vertices
		G.add_node(i)
	for i in range(no_node-1):
		line=fp.readline().strip("\n").split("\t")
		k=0
		for j in range(i+1,no_node):# adjacency matrix 
			if not line[k]=='' and float(line[k])>10: # adds edge iff similarity score >= 10
				G.add_edge(i,j)
			k+=1 
	fp.close()
	return G



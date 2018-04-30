import networkx as nx
import matplotlib.pyplot as plt
import copy
import math
#get graph from file
def get_graph_file():
	G=nx.Graph()
	print("Enter File Name:",end='')
	file_name=input().strip("\n")
	fp=open(file_name,"r")
	for lines in fp:
		edge=lines.strip("\n").split(" ")
		G.add_edge(edge[0],edge[1])
	fp.close()
	return G

def get_p3(G):
	p3s=[]
	for n1 in G:
		for n2 in G:
			for n3 in G:
				if not ((n1 == n2) or (n2 == n3) or (n1 == n3)):
					if ((G.has_edge(n1, n2) and G.has_edge(n2, n3) and not G.has_edge(n3, n1)) or (G.has_edge(n1, n2) and not G.has_edge(n2, n3) and  G.has_edge(n3, n1)) or (not G.has_edge(n1, n2) and G.has_edge(n2, n3) and G.has_edge(n3, n1))):
						p3=[n1,n2,n3]
						if sorted(p3) not in p3s:
							p3s.append(sorted(p3))	
	return p3s		

def get_universe(p3s):
	universe=set()
	for collection in p3s:
		for element in collection:
			universe.add(element)
	return universe		

def p3s_highest_element(S,p3_s):
	dict_element_count={}
	for vertex in S:
		dict_element_count[vertex]=0	
	for p3 in p3_s:
		for element in p3:
			dict_element_count[element]+=1
	max_element = max(dict_element_count, key=dict_element_count.get)
	return dict_element_count[max_element],max_element
	
def kernelization_hdv(universe,p3s,k,solution):
	if k>0 and len(p3s)>0 :
		#p3ss=copy.deepcopy(p3s)
		count,element=p3s_highest_element(universe,p3s)
		if (count>=(((k+1)*(k+2))/2)):
			k-=1
			solution.append(element)
			universe.remove(element)
			'''for p3 in p3ss:
				if element in p3:
					p3s.remove(p3)'''
			p3s=delete_vertex(p3s,element)
			return kernelization_hdv(universe,p3s,k,solution)
	return universe,p3s,k,solution


def kernelization_wre(p3s,k):
	WRE=[p3s[0]]
	
	for p3_1 in p3s:
		count = 0
		for p3_2 in WRE:
			if len(set(p3_1).intersection(p3_2))<2:
				count+=1/2
		if count==len(WRE):
			WRE.append(p3_1) 
	return WRE

def print_input_graph(G):
	plt.figure(1)
	number_of_connect_components=nx.number_connected_components(G)
	if number_of_connect_components==1:
		pos = nx.random_layout(G)
		nx.draw(G,pos,with_labels=True)
	else:
		i=1
		for a in nx.connected_component_subgraphs(G):	
			pos = nx.random_layout(a)
			plt.subplot(math.ceil(number_of_connect_components/2),2,i)
			i+=1
			nx.draw(a,pos,with_labels=True)		
	

def print_output_graph(G):
	plt.figure(2)
	number_of_connect_components=nx.number_connected_components(G)
	if number_of_connect_components==1:
		pos = nx.circular_layout(G)
		nx.draw(G,pos,with_labels=True)
	else:
		i=1
		for a in nx.connected_component_subgraphs(G):	
			pos = nx.circular_layout(a)
			plt.subplot(math.ceil(number_of_connect_components/2),2,i)
			i+=1
			nx.draw(a,pos,with_labels=True)	
	plt.show()

def kernelization(G,k):
	solutionI=[]
	p3s=get_p3(G)
	S=get_universe(p3s)
	#print (len(S))
	S,p3s,k,solution=kernelization_hdv(S,p3s,k,[])
	#print(len(S),k,solution)
	G.remove_nodes_from(solution)
	if k>0 and len(p3s)>0:
		#S=get_universe(p3s)
		W=kernelization_wre(p3s,k)
		if len(W)>k*k:
			print ("No Solution")
			k=-1
		else:
			V_W=get_universe(W)
			I=[item for item in S if item not in V_W]
			G_I=nx.subgraph(G,I)
			#print (G_I.number_of_edges(),I)
			if len(I)>=len(W)*3 and G_I.number_of_edges()==0:
				H=[]
				for element in W:
					H.append([element[0],element[1]])
					H.append([element[0],element[2]])
					H.append([element[1],element[2]])
				#print (I,H)
				G_HI=nx.Graph()
				for i in I:
					for h in H:
						a=copy.deepcopy(h)
						a.append(i)
						if a in p3s:
							str1 = ''.join(h)
							G_HI.add_edge(i,str1) 
				for key in nx.bipartite.maximum_matching(G_HI):
					if key in I:
						solutionI.append(element)
	
				G.remove_nodes_from(solutionI)
	return G,k,solution


def delete_vertex(p_3s,v):
	p3ss=copy.deepcopy(p_3s)
	for p_3 in p3ss:
		if v in p_3:
			p_3s.remove(p_3)
	return p_3s


def d_cvd(G,d,k,solution):
	number_cliques=nx.number_connected_components(G)
	if number_cliques<d:
		return False
	if number_cliques==d:
		return True
	else:
		cliques={}
		for connected_component in nx.connected_component_subgraphs(G):
			cc_nodes=connected_component.nodes()
			if len(cc_nodes) not in cliques:
				cliques[len(cc_nodes)]=[cc_nodes]
			else:
				cliques[len(cc_nodes)].append(cc_nodes)
		print(cliques)
		while (not number_cliques==d) and k>0:
			key=sorted(cliques)[0]
			print(key)
			del_clique=cliques[key].pop(0)
			solution+=del_clique
			k-=key
			if cliques[key]==[]:
				del cliques[key]
			number_cliques-=1
		if k>=0 and number_cliques==d:
			return True
		return False
def three_way_branching(p3s0,k,d,solution):
	p3s1=copy.deepcopy(p3s0)
	p3s2=copy.deepcopy(p3s0)
	p3s3=copy.deepcopy(p3s0)

	if len(p3s0)==0:
		#print (solution)
		G1=copy.deepcopy(G)
		G1.remove_nodes_from(solution)		
		if d_cvd(G1,d,k,solution):
			print ("Solution:",solution)
			G1.remove_nodes_from(solution)
			print_output_graph(G1)
			return True
		return False
		
	if k<=0:
		return False
	p3=p3s0[0]
	p3s1 = delete_vertex(p3s1,p3[0])
	p3s2 = delete_vertex(p3s2,p3[1])
	p3s3 = delete_vertex(p3s3,p3[2])
	return three_way_branching(p3s1,k-1,d,solution+[p3[0]]) or three_way_branching(p3s2,k-1,d,solution+[p3[1]]) or three_way_branching(p3s3,k-1,d,solution+[p3[2]])



G=get_graph_file()
print_input_graph(G)
k=int(input("Enter k:"))
d=int(input("Enter d:"))
G,k,solution=kernelization(G,k)
print(k,solution)

p3s=get_p3(G)
if not three_way_branching(p3s,k,d,solution):
	print ("No Solution")


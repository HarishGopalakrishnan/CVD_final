import networkx as nx
import copy
import math

#find all p3s of G
def get_p3(G):
	"""
	Find all the p3s in the given graph G
	"""
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

#find the universe of the p3s
def get_universe(p3s):
	"""
	Find the unoverse of the given p3s
	"""
	universe=set()
	for collection in p3s:
		for element in collection:
			universe.add(element)
	return universe		

#find the element that is present most of the p3s
def p3s_highest_element(S,p3_s):
	"""
	Find the element that is present in most of the p3s
	Input: Universe S and the collection of p3 as p3s
	Output: The element which is present in most of the p3s
	
	"""
	dict_element_count={}
	for vertex in S:
		dict_element_count[vertex]=0	
	for p3 in p3_s:
		for element in p3:
			dict_element_count[element]+=1
	max_element = max(dict_element_count, key=dict_element_count.get)
	return dict_element_count[max_element],max_element

#kernelization rule for high degree vertex rule
def kernelization_hdv(universe,p3s,k,solution):
	"""
	Kernelization rule for high degree vertex rule
	"""
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

	"""
	Kernelization rule2
	"""
	WRE=[p3s[0]]
	
	for p3_1 in p3s:
		count = 0
		for p3_2 in WRE:
			if len(set(p3_1).intersection(p3_2))<2:
				count+=1/2
		if count==len(WRE):
			WRE.append(p3_1) 
	return WRE


#kernelization of 3-hitting set
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

#delete all p3s that contain the element v
def delete_vertex(p_3s,v):
	"""
	Delete all p3s that contain the element v
	Input: p3s and v
	Output: Updated collection of p3s after deleting p3s that contains v
	"""
	p3ss=copy.deepcopy(p_3s)
	for p_3 in p3ss:
		if v in p_3:
			p_3s.remove(p_3)
	return p_3s



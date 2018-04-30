#system packages
import networkx as nx
import copy

#user defined functions
import kernelization as kernel
import print_graph
import get_graph


#3-way branching algorithm for CVD
def three_way_branching(p3s0,k,solution):
	"""
	Three way branching algorithm for CVD
	Input: Graph G represented by p3s,the parameter k
	Output: True if the G has a k-sized solution or False
	Select a p3 and do a three way branching 
	"""
	p3s1=copy.deepcopy(p3s0)
	p3s2=copy.deepcopy(p3s0)
	p3s3=copy.deepcopy(p3s0)

	if len(p3s0)==0:# if on p3 then graph is a cluster graph
		print ("Solution",solution)
		global sol
		sol=solution
		return True
	if k<=0:# the branch has no solution
		return False
	p3=p3s0[0]
	p3s1 = kernel.delete_vertex(p3s1,p3[0])
	p3s2 = kernel.delete_vertex(p3s2,p3[1])
	p3s3 = kernel.delete_vertex(p3s3,p3[2])
	return three_way_branching(p3s1,k-1,solution+[p3[0]]) or three_way_branching(p3s2,k-1,solution+[p3[1]]) or three_way_branching(p3s3,k-1,solution+[p3[2]])


def main():
	G=get_graph.edge_list()	# read the input instance
	print_graph.input(G)
	k=int(input("Enter k:"))
	G,k,solution=kernel.kernelization(G,k) # do kernelization
	print("Kernelization",k,solution)
	p3s=kernel.get_p3(G)
	if not three_way_branching(p3s,k,solution):	
		print ("No Solution")
	else:
		G.remove_nodes_from(sol)
		print_graph.output(G)
		print_graph.show()

if __name__== "__main__":
	main()

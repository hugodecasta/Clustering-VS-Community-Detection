import math
from igraph import Graph as ig
from graph_tool.all import minimize_nested_blockmodel_dl, Graph as gt
import os
import pickle


# ------------------------ distance
def euclidianDistance(coordinate1, coordinate2):
	# each coordinate should be of the same dimension
	size = len(coordinate1)
	if(size != len(coordinate2)):
		raise ValueError('error : the coordinate of the two points should be of the same dimension')

	sumOfSquare = 0
	for i in range(size):
		sumOfSquare += ((abs(coordinate1[i]) - abs(coordinate2[i])) ** 2)

	distance = math.sqrt(sumOfSquare)
	return distance


#transform the partition to correspond to the format of the librairy
def transformPartition(clusters) :
	nbrElement = 0
	for i in range(0,len(clusters)) :
		nbrElement = nbrElement + len(clusters[i])

	partition = [-1]*nbrElement
	for i in range(0,len(clusters)) :			#gave for each vertex the number of the community which it belong to.
		for j in range(0,len(clusters[i])) :
			partition[clusters[i][j]] = i

	return partition



class netMethods:
	# ------------------------ loading
	# -- Type de données:
	# --
	# -- sommets demarre a 0
	# --
	# -- [
	# -- ...
	# -- (sommet1, sommet2[, poid])
	# -- (sommet2, sommet7[, poid])
	# -- ...
	# -- ]
	# --
	# --------------------------------
	def loadData(filename):
		graph = ig.Read_GML(filename)
		return graph.get_edgelist()


	# ------------------------ transfrom
	class transform:

		#k nearest neightboors
		def naiveTransform(netData,**kwargs):
			k = kwargs.get('k', None)	# valeur par défault à definir, None ne peut pas permettre de construire un graphe
			nbrCore = kwargs.get('Core', 6)
			nbrPoint = len(netData)
			nbrPointCore = nbrPoint//nbrCore
			distance = dict()
			graph = []

			def partialTransform(debut, fin) :
				for i in range(debut, fin) :
					j = 0
					#calcul of all the distances :
					while j < nbrPoint :
						distance[j] = euclidianDistance(netData[i], netData[j])
						j += 1

					#construction of the graph :
					j = 0
					del distance[i]
					while j < k :
						nearest = min(distance, key=distance.get)
						del distance[nearest]	#if k > 1 we don't want to get always the same point.
						graph.append([i, nearest])
						j += 1

				return graph

			#pipes
			r = [-1,-1]*nbrCore
			w = [-1,-1]*nbrCore
			pid = [-1]*nbrCore

			for i in range(nbrCore):
				r[i], w[i] = os.pipe()

				try:
				    pid[i] = os.fork()
				except OSError:
				    exit("Could not create a child process\n")


				if pid[i] == 0:
					if i < nbrCore-1 :
						g = partialTransform(i*nbrPointCore, (i+1)*nbrPointCore)
					else :
						g = partialTransform(i*nbrPointCore, nbrPoint)	#to be sure that there is not a forgoten point.
					os.write(w[i], pickle.dumps(g))
					exit()


			for i in range(nbrCore):
				finished = os.waitpid(pid[i], 0)
				graph += pickle.loads(os.read(r[i], 250000000))

			return graph	#the final graph can contain some edge in both direction.



	# ------------------------ clustering
	class clustering:
		def infomap(netObject, clusterCount=None,**kwargs):
			graph = ig(0, netObject)
			partition = graph.community_infomap()
			return transformPartition(partition)


		def louvain(netObject, clusterCount=None,**kwargs):
			graph = ig(0, netObject)
			partition = graph.community_multilevel()
			return transformPartition(partition)


		def labelPropagation(netObject, clusterCount=None,**kwargs):
			graph = ig(0, netObject)
			partition = graph.community_label_propagation()
			return transformPartition(partition)


		def nestedBlockmodel(netObject, clusterCount=None,**kwargs):
			g = gt()
			g.set_directed(False)
			#get the number of node in netObject (note : the nuber of node is consider to be equal to the id of the biggest node with a vertex). add 1 because netObject count the node from 0.
			nbrNode = max([item for sublist in netObject for item in sublist])+1
			for i in range(nbrNode) :
				g.add_vertex()
			g.add_edge_list(netObject)		#create the edges.

			block = minimize_nested_blockmodel_dl(g)
			nbrBlocks = block.levels[0].get_B()
			block = block.levels[0].get_blocks()

			partition = [[] for x in range(nbrBlocks)]	#one list for each community.

			for i in range (0, nbrNode) :
				partition[block[i]].append(i)

			return transformPartition(partition)

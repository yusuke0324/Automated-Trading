#!/usr/bin/env python
# -*- coding:utf-8 -*-

from random import random,randint,choice
from copy import deepcopy
from math import log

class fwrapper:
	def __init__(self,function,childcount,name):
		self.function=function
		self.childcount=childcount
		self.name=name

class node:
	def __init__(self,fw,children):
		self.function=fw.function
		self.name=fw.name
		self.children=children
	def evaluate(self,inp):
		results=[n.evaluate(inp) for n in self.children]
		return self.function(results)
	def display(self,indent=0):
		print (' '*indent)+self.name
		for c in self.children:
			c.display(indent+1)

class paramnode:
	def __init__(self,idx):
		self.idx=idx
	def evaluate(self,inp):
		return inp[self.idx]
	def display(self,indent=0):
		print '%sp%d' % (' '*indent,self.idx)

class constnode:
	def __init__(self,v):
		self.v=v
	def evaluate(self,inp):
		return self.v
	def display(self,indent=0):
		print '%s%d' % (' '*indent,self.v)

addw=fwrapper(lambda l:l[0]+l[1],2,'add')
subw=fwrapper(lambda l:l[0]-l[1],2,'subtract')
mulw=fwrapper(lambda l:l[0]*l[1],2,'multiply')

def iffunc(l):
	if l[0]>0: return l[1]
	else: return l[2]
ifw=fwrapper(iffunc,3,'if')

def isgreater(l):
	if l[0]>l[1]: return 1
	else: return 0
gtw=fwrapper(isgreater,2,'isgreater')
flist=[addw,mulw,ifw,gtw,subw]

def exampletree():
	return node(ifw,[
		node(gtw,[paramnode(0),constnode(3)]),
		node(addw,[paramnode(1),constnode(5)]),
		node(subw,[paramnode(1),constnode(2)]),
		]
	)

def makerandomtree(pc,maxdepth=4,fpr=0.5,ppr=0.6):
	if random()<fpr and maxdepth>0:
		f=choice(flist)
		children=[makerandomtree(pc,maxdepth-1,fpr,ppr) for i in range(f.childcount)]
		return node(f,children)
	elif random() < ppr:
		return paramnode(randint(0,pc-1))
	else:
		return constnode(randint(0,10))

def hiddenfunction(x,y):
	return x**2+2*y+3*x+5

def buildhiddenset():
	rows=[]
	for i in range(200):
		x=randint(0,40)
		y=randint(0,40)
		rows.append([x,y,hiddenfunction(x,y)])
	return rows

def scorefunction(tree,s):
	dif=0
	for data in s:
		v=tree.evaluate([data[0],data[1]])
		dif+=abs(v-data[2])
	return dif

def mutate(t,pc,probchange=0.1):
	if random()<probchange:
		return makerandomtree(pc)
	else:
		result=deepcopy(t)
		if hasattr(t,"children"):
			result.children=[mutate(c,pc,probchange) for c in t.children]
		return result

def crossover(t1,t2,probswap=0.7,top=1):
	if random() < probswap and not top:
		return deepcopy(t2)
	else:
		result=deepcopy(t1)
		if hasattr(t1,"children") and hasattr(t2,"children"):
			result.children=[crossover(c,choice(t2.children),probswap,0) for c in t1.children]
		return result

def evolve(pc,popsize,rankfunction,maxgen=500,mutationrate=0.1,breedingrate=0.4,pexp=0.7,pnew=0.05):
	# ランダムな低い数値を返す。pexpが低ければ低いほど得られる数値は小さくなる
	def selectindex():
		return int(log(random())/log(pexp))
	# 初期集団をランダムに作り上げる
	population=[makerandomtree(pc) for i in range(popsize)]
	for i in range(maxgen):
		scores=rankfunction(population)
		print scores[0][0]
		if scores[0][0]==0: break

		# 上位二つは無条件に採用
		newpop=[scores[0][1],scores[1][1]]

		# 次世代を作る
		while len(newpop)<popsize:
			if random()>pnew:
				newpop.append(mutate(crossover(scores[selectindex()][1],scores[selectindex()][1],probswap=breedingrate),pc,probchange=mutationrate))
			else:
				newpop.append(makerandomtree(pc))
		population=newpop
	scores[0][1].display()
	return scores[0][1]

def getrankfunction(dataset):
	def rankfunction(population):
		scores=[(scorefunction(t,dataset),t) for t in population]
		scores.sort()
		return scores
	return rankfunction

from __future__ import annotations
import json
import math
from typing import List

# Datum class.
# DO NOT MODIFY.
class Datum():
    def __init__(self,
                 coords : tuple[int],
                 code   : str):
        self.coords = coords
        self.code   = code
    def to_json(self) -> str:
        dict_repr = {'code':self.code,'coords':self.coords}
        return(dict_repr)

# Internal node class.
# DO NOT MODIFY.
class NodeInternal():
    def  __init__(self,
                  splitindex : int,
                  splitvalue : float,
                  leftchild,
                  rightchild):
        self.splitindex = splitindex
        self.splitvalue = splitvalue
        self.leftchild  = leftchild
        self.rightchild = rightchild

# Leaf node class.
# DO NOT MODIFY.
class NodeLeaf():
    def  __init__(self,
                  data : List[Datum]):
        self.data = data

# KD tree class.
class KDtree():
    def  __init__(self,
                  k    : int,
                  m    : int,
                  root = None):
        self.k    = k
        self.m    = m
        self.root = root

    # For the tree rooted at root, dump the tree to stringified JSON object and return.
    # DO NOT MODIFY.
    def dump(self) -> str:
        def _to_dict(node) -> dict:
            if isinstance(node,NodeLeaf):
                return {
                    "p": str([{'coords': datum.coords,'code': datum.code} for datum in node.data])
                }
            else:
                return {
                    "splitindex": node.splitindex,
                    "splitvalue": node.splitvalue,
                    "l": (_to_dict(node.leftchild)  if node.leftchild  is not None else None),
                    "r": (_to_dict(node.rightchild) if node.rightchild is not None else None)
                }
        if self.root is None:
            dict_repr = {}
        else:
            dict_repr = _to_dict(self.root)
        return json.dumps(dict_repr,indent=2)

    # Insert the Datum with the given code and coords into the tree.
    # The Datum with the given coords is guaranteed to not be in the tree.
    def insert(self,point:tuple[int],code:str):
        datum : Datum = Datum(coords=point,code=code)
        if self.root == None:
            node_leaf = NodeLeaf(data=[datum])
            self.root = node_leaf
        else:
            parent = None
            cur_is_left_child = False
            cur = self.root
            while isinstance(cur, NodeInternal):
                parent = cur
                if datum.coords[cur.splitindex] < cur.splitvalue:
                    cur = cur.leftchild
                    cur_is_left_child = True
                else:
                    cur = cur.rightchild # goes right if it is equal
                    cur_is_left_child = False

            # cur is now a NodeLeaf
            cur.data.append(datum)

            if len(cur.data) > self.m:
                # Split node
                split_index = get_max_spread_index(cur.data)
                split_value = get_median(cur.data, split_index)
                sorted_datum_lst = sorted(cur.data, key=lambda x: x.coords[split_index])
                left_child = NodeLeaf(data=sorted_datum_lst[:(self.m+1)//2])  # NodeLeaf containing floor((m+1)/2) lesser data
                right_child = NodeLeaf(data=sorted_datum_lst[(self.m+1)//2:]) # NodeLeaf containing remaining data
                internal_Node = NodeInternal(splitindex=split_index, splitvalue=split_value, leftchild=left_child, rightchild=right_child)
                if parent == None:
                    self.root = internal_Node
                elif cur_is_left_child:
                    parent.leftchild = internal_Node
                else:
                    parent.rightchild = internal_Node

    # Delete the Datum with the given point from the tree.
    # The Datum with the given point is guaranteed to be in the tree.
    def delete(self,point:tuple[int]):
        grandparent = None
        parent_is_left_child = False
        parent = None
        cur_is_left_child = False
        cur = self.root
        while isinstance(cur, NodeInternal):
            grandparent = parent
            parent = cur
            parent_is_left_child = cur_is_left_child
            if point[cur.splitindex] < cur.splitvalue:
                cur = cur.leftchild
                cur_is_left_child = True
            else:
                cur = cur.rightchild # goes right if it is equal
                cur_is_left_child = False
        
        # cur is now a NodeLeaf
        for datum in cur.data:
            if datum.coords == point:
                cur.data.remove(datum)
                break
        
        # Check if leaf is empty
        if len(cur.data) == 0:
            if parent == None:
                # cur is the root
                self.root = None
            elif grandparent == None:
                # parent is the root
                self.root = parent.rightchild if cur_is_left_child else parent.leftchild
            else:
                if parent_is_left_child:
                    grandparent.leftchild = parent.rightchild if cur_is_left_child else parent.leftchild
                else:
                    grandparent.rightchild = parent.rightchild if cur_is_left_child else parent.leftchild

    # Find the k nearest neighbors to the point.
    def knn(self,k:int,point:tuple[int]) -> str:
        # Use the strategy discussed in class and in the notes.
        # The list should be a list of elements of type Datum.
        # While recursing, count the number of leaf nodes visited while you construct the list.
        # The following lines should be replaced by code that does the job.

        (leaveschecked,knnlist,ignore) = knn_helper(k=k, point=point, leaveschecked=0, knnlist=[], datum_to_distance_map=dict(), cur=self.root)

        # The following return line can probably be left alone unless you make changes in variable names.
        return(json.dumps({"leaveschecked":leaveschecked,"points":[datum.to_json() for datum in knnlist]},indent=2))

    
def get_max_spread_index(lst:List[Datum]) -> int:
    index = -1
    max_spread = 0
    for i in range(len(lst[0].coords)):
        min = None
        max = None
        for j in range(len(lst)):
            if min == None or lst[j].coords[i] < min:
                min = lst[j].coords[i]
            if max == None or lst[j].coords[i] > max:
                max = lst[j].coords[i]
        if max - min > max_spread:
            max_spread = max - min
            index = i
    return index

def get_median(lst:List[Datum], split_index:int) -> float:
    coor_lst = []
    for i in range(len(lst)):
        coor_lst.append(lst[i].coords[split_index])
    coor_lst.sort()
    mid = len(coor_lst) // 2
    return (coor_lst[mid] + coor_lst[~mid]) / 2

def knn_helper(k:int,point:tuple[int],leaveschecked:int,knnlist:List[Datum],datum_to_distance_map:dict,cur) -> (int,List[Datum],dict):
    if isinstance(cur, NodeLeaf):
        leaveschecked += 1
        for datum in cur.data:
            distance = datum_to_point_distance(datum=datum, point=point)
            if len(knnlist) == k and (distance < datum_to_distance_map[knnlist[-1]] or (distance == datum_to_distance_map[knnlist[-1]] and datum.code < knnlist[-1].code)):
                del datum_to_distance_map[knnlist.pop()]
            if len(knnlist) < k:
                for i in range(len(knnlist)):
                    if distance < datum_to_distance_map[knnlist[i]]:
                        knnlist.insert(i, datum)
                        break
                if datum not in knnlist:
                    knnlist.append(datum)
                datum_to_distance_map[datum] = distance

    else: # cur is a splitting node
        bb1 = []
        bb2 = []
        for i in range(len(point)):
            bb1.append([None,None])
            bb2.append([None,None])
        left_child_bb = get_bounding_box(node=cur.leftchild,bb=bb1)
        right_child_bb = get_bounding_box(node=cur.rightchild,bb=bb2)
        left_bb_distance = bb_to_point_distance(bb=left_child_bb,point=point)
        right_bb_distance = bb_to_point_distance(bb=right_child_bb,point=point)
        other_bb_distance = None

        if (left_bb_distance <= right_bb_distance and (len(knnlist) < k or left_bb_distance <= datum_to_distance_map[knnlist[-1]])): # considering bb that is equal in distance to furthest point
            # visit left subtree
            (leaveschecked,knnlist,datum_to_distance_map) = knn_helper(k,point,leaveschecked,knnlist,datum_to_distance_map,cur.leftchild)
            other_bb_distance = right_bb_distance
            other_child = cur.rightchild
        elif (right_bb_distance < left_bb_distance and (len(knnlist) < k or right_bb_distance <= datum_to_distance_map[knnlist[-1]])):
            # visit right subtree
            (leaveschecked,knnlist,datum_to_distance_map) = knn_helper(k,point,leaveschecked,knnlist,datum_to_distance_map,cur.rightchild)
            other_bb_distance = left_bb_distance
            other_child = cur.leftchild
        
        if other_bb_distance != None and (len(knnlist) < k or other_bb_distance <= datum_to_distance_map[knnlist[-1]]):
            # visit other child
            (leaveschecked,knnlist,datum_to_distance_map) = knn_helper(k,point,leaveschecked,knnlist,datum_to_distance_map,other_child)

    return (leaveschecked,knnlist,datum_to_distance_map)

def datum_to_point_distance(datum:Datum,point:tuple[int]) -> int:
    distance = 0
    for i in range(len(point)):
        distance += ((datum.coords[i] - point[i]) ** 2)
    return distance

def get_bounding_box(node, bb:List[List[int]]) -> List[List[int]]:
    if node == None:
        return bb
    if isinstance(node, NodeLeaf):
        for i in range(len(node.data)):
            for j in range(len(node.data[i].coords)):
                if bb[j][0] == None or node.data[i].coords[j] < bb[j][0]:
                    bb[j][0] = node.data[i].coords[j]
                if bb[j][1] == None or node.data[i].coords[j] > bb[j][1]:
                    bb[j][1] = node.data[i].coords[j]
    else: # node is an internal Node
        bb = get_bounding_box(node.leftchild, bb)
        bb = get_bounding_box(node.rightchild, bb)
    return bb

def bb_to_point_distance(bb:List[List[int]],point:tuple[int]) -> int:
    distance = 0
    for i in range(len(point)):
        if point[i] not in range(bb[i][0], bb[i][1]):
            distance += min((bb[i][0] - point[i]) ** 2, (bb[i][1] - point[i]) ** 2)
    return distance
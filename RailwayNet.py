import re

node_list = []
link_list = []
node_dic = {}
node_header = ""
link_header = ""

station_node = []
segment_node = []


def toStr(List):
    string = ''
    for i in range(len(List) - 1):
        if List[i] == None:
            string += ','
        else:
            string += str(List[i]) + ","
    if List[len(List) - 1] != None:
        string += str(List[len(List) - 1])
    return string


def output(minPoints, eps):
    import DBSCAN
    global segment_node
    clusters, noise, segment_node = DBSCAN.getCentralNode(station_node, eps, minPoints, segment_node)
    import os
    if not os.path.exists(r'.\new file'):
        os.mkdir(r'.\new file')
    node_file = open(r'.\new file\node.csv', "w", 1)
    node_file.write(node_header)
    segment_node.extend(noise)
    for node in segment_node:
        cell = [None, node.node_id, None, None, None, 0, None, None, 0, node.x_location, node.y_location, None, None]
        node_file.write(toStr(cell) + '\n')
    for cluster in clusters:
        cell = [None, cluster[0].node_id, None, None, None, 0, None, None, 0, cluster[0].x_location,
                cluster[0].y_location, None, None]
        node_file.write(toStr(cell) + '\n')
    node_file.close()

    link_file = open(r'.\new file\link.csv', "w", 1)
    link_file.write(link_header)
    link_id = 0
    for link in link_list:
        if (link.from_node.node_id == link.to_node.node_id):
            continue
        link_id += 1
        length = link.length
        check_geometry(link)
        geometry = '"LINESTRING ('
        for arr in link.geometry:
            geometry += (str(arr[0])) + " " + str(arr[1]) + ","
        geometry += ')"'
        cell = [None, link_id, None, link.from_node.node_id, link.to_node.node_id, None, length, None, None, None,
                'railway', 30, geometry, None, None]
        link_file.write(toStr(cell) + '\n')
    link_file.close()


def get_var_node():
    global station_node, segment_node
    for node in node_list:
        if (node.connect_number >= 3 or node.connect_number == 1):
            station_node.append(node)
        else:
            segment_node.append(node)


def check_geometry(link):
    if link.from_node.node_id==22 and link.to_node.node_id==21:
        a=1
    if len(link.geometry)==0:
        return
    if not link.from_node.is_changing and not link.to_node.is_changing:
        return
    elif link.from_node.is_changing and not link.to_node.is_changing:
        if check_acute_angle([link.geometry[1][0], link.geometry[1][1]], [link.geometry[0][0], link.geometry[0][1]],
                       [link.from_node.x_location, link.from_node.y_location]):
            link.geometry.clear()
        else:
            link.geometry.insert(0, [link.from_node.x_location, link.from_node.y_location])
        return
    elif link.to_node.is_changing and not link.from_node.is_changing:
        if check_acute_angle([link.geometry[-2][0], link.geometry[-2][1]], [link.geometry[-1][0], link.geometry[-1][1]],
                       [link.to_node.x_location, link.to_node.y_location]):
            link.geometry.clear()
        else:
            link.geometry.append([link.to_node.x_location,link.to_node.y_location])
        return
    else:
        from_acute_angle=check_acute_angle([link.geometry[1][0], link.geometry[1][1]], [link.geometry[0][0], link.geometry[0][1]],
                       [link.from_node.x_location, link.from_node.y_location])
        to_acute_angle=check_acute_angle([link.geometry[-2][0], link.geometry[-2][1]], [link.geometry[-1][0], link.geometry[-1][1]],
                       [link.to_node.x_location, link.to_node.y_location])
        if not from_acute_angle and not to_acute_angle:
            link.geometry.insert(0,[link.from_node.x_location,link.from_node.y_location])
            link.geometry.append([link.to_node.x_location,link.to_node.y_location])
        else:
            link.geometry.clear()


def check_acute_angle(org, intersection, new):
    import numpy as np
    org_ = np.asarray(org)
    intersection_ = np.asarray(intersection)
    new_ = np.asarray(new)
    vec1 = org_ - intersection_
    vec2 = new_ - intersection_
    aaa=np.dot(vec1, vec2)
    return np.dot(vec1, vec2) > 0


def handle_geometry(cells):
    geometry = []
    cell = cells[12:len(cells) - 2]
    for index in range(0, len(cell)):
        subcell = cell[index].split(' ')
        x = re.findall(r'-?\d+\.?\d*e?-?\d*?', subcell[1])
        y = re.findall(r'-?\d+\.?\d*e?-?\d*?', subcell[2])
        a = [float(x[0]), float(y[0])]
        geometry.append(a)

    return geometry


def read_node(node_file_name, link_file_name):
    global node_header, link_header
    global node_list, node_dic, link_list
    node_file = open(node_file_name, "r", 1)
    node_header = node_file.readline()
    str = node_file.readline()
    while str != '':
        cells = str.split(',')
        node = Node(int(cells[1]), float(cells[9]), float(cells[10]))
        node_list.append(node)
        node_dic.update({node.node_id: node})
        str = node_file.readline()
    node_file.close()
    link_file = open(link_file_name, "r", 1)
    link_header = link_file.readline()
    str = link_file.readline()
    while str != '':
        cells = str.split(',')
        node_dic[int(cells[3])].connect_number += 1
        node_dic[int(cells[4])].connect_number += 1
        link = Link(node_dic[int(cells[3])], node_dic[int(cells[4])], cells[6], int(cells[1]))
        link.geometry = handle_geometry(cells)
        link_list.append(link)
        str = link_file.readline()

    link_file.close()


class Node:
    def __init__(self, node_id, x_location, y_location):
        self.node_id = node_id
        self.x_location = x_location
        self.y_location = y_location
        self.connect_number = 0
        self.cluster_id = 0
        self.is_changing=False


class Link:
    def __init__(self, from_node, to_node, length, link_id):
        self.from_node = from_node
        self.to_node = to_node
        self.geometry = None
        self.length = length
        self.link_id = link_id


def main(node_file_name, link_file_name, minPoints, eps):
    read_node(node_file_name, link_file_name)
    get_var_node()
    output(minPoints, eps)


if __name__ == "__main__":
    node_file_name = r'.\node.csv'
    link_file_name = r'.\link.csv'
    main(node_file_name, link_file_name, 3, 0.001)

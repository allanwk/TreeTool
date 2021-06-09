import numpy as np
import csv
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem
import sys
import csv
import codecs

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(200,200,800,400)
        self.setWindowTitle("Árvore Genealógica")
        self.displayed_people = []
        self.usedx={}
        self.visited = []
        self.person_width = 50
        self.level_heigth = 50
        self.spacing = 20
        self.people = []

    def show_people(self, people):
        self.people = people
        for person in people:
            y = int(person.level * (self.level_heigth + self.spacing))
            x = int(400 + (person.x * (self.person_width + self.spacing)))
            self.displayed_people.append(QtWidgets.QListWidget(self))
            self.displayed_people[-1].addItem(QListWidgetItem(person.name))
            self.displayed_people[-1].setGeometry(QtCore.QRect(x, y, self.person_width, self.level_heigth))
            self.displayed_people[-1].show()

    def convert_x(self, x):
        return int(400 + (x * (self.person_width + self.spacing)))

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        for person in self.people:
            x1 = int(400 + (person.x * (self.person_width + self.spacing)))
            y1 = int(person.level * (self.level_heigth + self.spacing))
            for rel in person.partners:                    
                for partner in rel.partners:
                    if partner.name != person.name:
                        x2 = int(400 + (partner.x * (self.person_width + self.spacing)))
                        y2 = int(partner.level * (self.level_heigth + self.spacing))
                        if rel.divorced:
                            qp.setPen(QColor(255,0,0))
                        qp.drawLine(x1+self.person_width/2, y1+self.level_heigth/2, x2+self.person_width/2, y2+self.level_heigth/2)
                        if rel.divorced:
                            qp.setPen(QColor(0,0,0))
                        if len(rel.children) > 0:
                            relx = self.person_width/2 + (x1 + x2)/2
                            qp.drawLine(relx, y1+self.level_heigth/2, relx, y1+self.level_heigth+self.spacing/2)

            if len(person.parent_relationship.partners) > 0:
                qp.drawLine(x1+self.person_width/2, y1, x1 + self.person_width/2, y1-self.spacing/2)
            if len(person.parent_relationship.children) > 1:
                siblings = person.parent_relationship.children.copy()
                siblings.sort(key = lambda p: p.x)
                if person.x == siblings[0].x:
                    leftx = self.convert_x(siblings[0].x) + self.person_width/2
                    rightx = self.convert_x(siblings[-1].x) + self.person_width/2
                    qp.drawLine(leftx, y1-self.spacing/2, rightx, y1-self.spacing/2)
                """
                if person.x == siblings[0].x:
                    qp.drawLine(x1+self.person_width/2, y1-self.spacing/2, x1 + self.person_width, y1-self.spacing/2)
                    qp.drawLine(siblings_x, y1-self.spacing/2, siblings_x, y1-(self.spacing/2)-self.level_heigth/2)
                elif person.x == siblings[-1].x:
                    qp.drawLine(x1-self.spacing, y1-self.spacing/2, x1 + self.person_width/2, y1-self.spacing/2)
                else:
                    qp.drawLine(x1-self.spacing/2, y1-self.spacing/2, x1 + self.person_width, y1-self.spacing/2)
                """
        qp.end()
        
        


class Person:
    def __init__(self, name=None, partners=None):
        self.name = name
        if partners is None:
            partners = []
        self.partners = partners
        self.parent_relationship = Partnership(children=[self])
        self.id = None
        self.level = None
        self.x = 0

    def __str__(self):
        return "Person: {}, level {}, x={}, {}".format(self.name, self.level, self.x, self.partners)

class Partnership:
    def __init__(self, partners=None, children=None):
        if partners is None:
            partners = []
        self.partners = partners
        if children is None:
            children = []
        self.children = children
        self.id = None
        self.divorced = False
    
    def __str__(self):
        return "Relationship between {} and {}\nChildren: {}".format(self.partners[0].name, self.partners[1].name, self.children)

def establish_relationship(p1, p2):
    r = Partnership([p1, p2])
    p1.partners.append(r)
    p2.partners.append(r)
    
def set_active_relationship(p1, p2):
    print("p1", p1.name)
    for rel in p1.partners:
        for partner in rel.partners:
            print(partner.name)
            if partner.name != p1.name and partner.name != p2.name:
                rel.divorced = True
    print("p2", p2.name)
    for rel in p2.partners:
        for partner in rel.partners:
            print(partner.name)
            if partner.name != p1.name and partner.name != p2.name:
                rel.divorced = True

def add_children(p1, p2, children):
    if type(children) != list:
        children = [children]
    for relationship in p1.partners:
        for p in relationship.partners:
            if p.name != p1.name and p.name == p2.name:
                rel = relationship
    for child in children:
        rel.children.append(child)
        child.parent_relationship = rel

highest = [None, float('inf')]
people_ls = []
def count_people(person, visited=[], count=0, level=0, checkHighest=False, clear_list=False):
    if person.name not in visited:
        person.id = count
        person.level = level
        count += 1
        visited.append(person.name)
        if clear_list:
            people_ls.clear()
        people_ls.append(person)
        if level < highest[1] and checkHighest:
            highest[0] = person
            highest[1] = level
        if person.parent_relationship != None:
            for parent in person.parent_relationship.partners:
                if parent.name not in visited:
                    count = count_people(parent, visited, count, level-1, checkHighest)
        for relationship in person.partners:
            for p in relationship.partners:
                if p.name not in visited:
                    count = count_people(p, visited, count, level, checkHighest)
            for child in relationship.children:
                if child.name not in visited:
                    count = count_people(child, visited, count, level+1, checkHighest)
    return count

people_per_level = {}
def get_adjacency(person, person_adjacency, visited=[]):
    if person.name not in visited:
        print(person)
        visited.append(person.name)
        if person.level not in people_per_level:
            people_per_level[person.level] = 0
        people_per_level[person.level] += 1
        if person.parent_relationship != None:
            for parent in person.parent_relationship.partners:
                person_adjacency[parent.id][person.id] = 3
                get_adjacency(parent, person_adjacency, visited)
        for relationship in person.partners:
            for p in relationship.partners:
                if p.name not in visited:
                    if relationship.divorced:
                        person_adjacency[person.id][p.id] = 2
                    else:
                        person_adjacency[person.id][p.id] = 1
                    get_adjacency(p, person_adjacency, visited)
            for child in relationship.children:
                person_adjacency[person.id][child.id] = 3
                get_adjacency(child, person_adjacency, visited)

usedx = {}
people_to_show = []
def put(person):
    people_to_show.append(person)
    print("Starting at", person.name)
    if person.level not in usedx:
        usedx[person.level] = []
    if person.level-1 not in usedx:
        usedx[person.level-1] = []
    if len(person.parent_relationship.partners) != 0:
        people_left = len(person.parent_relationship.partners[0].parent_relationship.children)
        for sibling in person.parent_relationship.partners[0].parent_relationship.children:
            if sibling.name != person.parent_relationship.partners[0].name:
                people_left += len(sibling.partners)
        leftmost = person.x - people_left + 0.5
        leftmost += len(person.parent_relationship.partners[0].partners) - 1
        people_right = len(person.parent_relationship.partners[1].parent_relationship.children)
        for sibling in person.parent_relationship.partners[1].parent_relationship.children:
            if sibling.name != person.parent_relationship.partners[1].name:
                people_right += len(sibling.partners)
        rightmost = person.x + people_right + 0.5
        rightmost += len(person.parent_relationship.partners[1].partners) - 1

        try:
            left_dist = leftmost - max([a for a in usedx[person.level-1] if a <= leftmost])
        except:
            left_dist = float('inf')
        try:
            right_dist = max([a for a in usedx[person.level-1] if a >= rightmost]) - rightmost
        except:
            right_dist = float('inf')
        print(left_dist, right_dist)
        offset = 0
        if left_dist < 1:
            offset = 1 - left_dist
        elif right_dist < 1:
            offset = -1 + right_dist * (-1)

        person.parent_relationship.partners[0].x = person.x - 0.5 + offset
        person.parent_relationship.partners[1].x = person.x + 0.5 + offset
        usedx[person.level-1].append(person.x - 0.5 + offset)
        usedx[person.level-1].append(person.x + 0.5 + offset)
        counter = 1
        parent = person.parent_relationship.partners[0]
        for rel in parent.partners:
            for p in rel.partners:
                if p.name != parent.name and p.name != person.parent_relationship.partners[1].name:
                    print(p.name, 'parent[0]')
                    people_to_show.append(p)
                    p.x = person.x - (0.5 + counter) + offset
                    counter += 1
        for sibling in parent.parent_relationship.children:
            if sibling.name != parent.name:
                people_to_show.append(sibling)
                sibling.x = person.x - (0.5 + counter) + offset
                usedx[person.level - 1].append(sibling.x)
                counter += 1
                for rel in sibling.partners:
                    for p in rel.partners:
                        if p.name != sibling.name:
                            people_to_show.append(p)
                            p.x = person.x - (0.5 + counter) + offset
                            usedx[person.level - 1].append(p.x)
                            counter += 1
        counter = 1
        parent = person.parent_relationship.partners[1]
        for rel in parent.partners:
            for p in rel.partners:
                if p.name != parent.name and p.name != person.parent_relationship.partners[0].name:
                    print(p.name, 'parent[1]')
                    people_to_show.append(p)
                    p.x = person.x + (0.5 + counter) + offset
                    counter += 1
        for sibling in parent.parent_relationship.children:
            if sibling.name != parent.name:
                people_to_show.append(sibling)
                sibling.x = person.x + (0.5 + counter) + offset
                usedx[person.level - 1].append(sibling.x)
                counter += 1
                for rel in sibling.partners:
                    for p in rel.partners:
                        if p.name != sibling.name:
                            people_to_show.append(p)
                            p.x = person.x + (0.5 + counter) + offset
                            usedx[person.level - 1].append(p.x)
                            counter += 1
        for parent in person.parent_relationship.partners:
            put(parent)

def rearrange(level):
    repositioned = []
    people = [p for p in people_to_show if p.level == level]
    people.sort(key = lambda p: p.x)
    for p in people:
        if len(p.parent_relationship.partners) != 0:
            #check if it is the rightmost sibling

            siblings = p.parent_relationship.children.copy()
            siblings.sort(key = lambda p: p.x)
            siblings_x = 0
            for sib in siblings:
                siblings_x += sib.x
            siblings_x /= len(siblings)

            if p.x != siblings[-1].x:
                print("skipping", p.name, ' not rightmost sibling')
                continue
            repositioned.append(p.name)
            expected_x = (p.parent_relationship.partners[0].x + p.parent_relationship.partners[1].x)/2
            
            offset = expected_x - siblings_x
            print(p.name, p.x, p.parent_relationship.partners[0].x, p.parent_relationship.partners[1].x, offset)
            
            if offset < 0:
                print("triggering recursion from ", p.name)
                offset_above(p.parent_relationship.partners[0], -offset, level-1)
                continue
            for p2 in people:
                if p2.name != p.name:
                    if p2.x >= p.x:
                        p2.x += offset
            
            for sibling in p.parent_relationship.children:
                sibling.x += offset
                if sibling.name != p.name:
                    for rel in sibling.partners:
                        for partner in rel.partners:
                            if partner.name != sibling.name and partner.name not in repositioned:
                                partner.x += offset
            
            if len(p.partners) > 1:
                for rel in p.partners:
                    for partner in rel.partners:
                        if partner.name != p.name and partner.x < p.x:
                            partner.x += offset


        else:
            print("skipping", p.name, ' no parents')

def offset_above(p, offset, level):
    print("recursion at ", p)
    people = [pe for pe in people_to_show if pe.level == level and pe.x >= p.x]
    people.sort(key = lambda p: p.x)
    for p2 in people:
        if p2.name != p.name:
            if p2.x >= p.x:
                p2.x += offset

    for sibling in p.parent_relationship.children:
        sibling.x += offset
        if sibling.name != p.name:
            for rel in sibling.partners:
                for partner in rel.partners:
                    if partner.name != sibling.name and partner.name not in repositioned:
                        partner.x += offset
    if len(p.parent_relationship.partners) != 0:
        offset_above(p.parent_relationship.partners[0], offset, level-1)

def save_tree(person):
    person_adjacency = np.zeros((n_people, n_people), dtype=int)
    get_adjacency(person, person_adjacency)
    np.savetxt('adjacency.txt', person_adjacency, fmt='%d')
    dict_data = [{'id': person.id, 'name': person.name} for person in people_ls]
    csv_cols = ['id', 'name']
    with codecs.open('data.csv', 'w', "utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = csv_cols, lineterminator='\n')
        writer.writeheader()
        for data in dict_data:
            writer.writerow(data)

def load_tree():
    with codecs.open('data.csv', 'r', "utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        people = [Person(row['name']) for row in reader]
    
    adj = np.loadtxt('adjacency.txt', dtype=int)
    n_lines = adj.shape[0]
    for i in range(n_lines):
        for j in range(i+1, n_lines):
            if adj[i][j] == 1 or adj[i][j] == 2:
                establish_relationship(people[i], people[j])
    for i in range(n_lines):
        for j in range(i+1, n_lines):
            if adj[i][j] == 1:
                set_active_relationship(people[i], people[j])
            if adj[i][j] == 3:
                for k in range(i + 1, n_lines):
                    if adj[k][j] == 3:
                        second_parent = people[k].name
                        parents = [people[i].name, people[k].name]
                        for rel in people[i].partners:
                            if rel.partners[0].name in parents and rel.partners[1].name in parents:
                                add_children(rel.partners[0], rel.partners[1], people[j])
    return people[0]

#Test tree
allan = Person('Allan')
livia = Person('Livia')
amelie = Person('Amelie')
jack = Person('Jack')
ruby = Person('Ruby')
john = Person('John')
lucas = Person('Lucas')
manuel = Person('Manuel')
establish_relationship(allan, livia)
establish_relationship(amelie, Person('Joe'))
rose = Person('Rose')
establish_relationship(jack, rose)
add_children(jack, rose, Person("Joao"))
establish_relationship(amelie, jack)
set_active_relationship(amelie, jack)
establish_relationship(john, ruby)
establish_relationship(manuel, Person("Jane"))
add_children(allan, livia, amelie)
add_children(allan, livia, manuel)
add_children(allan, livia, Person("Claudia"))
james = Person('James')
establish_relationship(james, Person('Janice'))
add_children(ruby, john, james)
add_children(ruby, john, jack)
add_children(amelie, jack, lucas)
add_children(amelie, jack, Person('jkj'))
add_children(ruby, john, Person('Joaquim'))
daggie = Person('Daggie')
luiz = Person('Luiz')
g = Person('Gláucia')
p = Person('Paulo')
o = Person('Christel')
h =Person('Herbert')
establish_relationship(h,o)
add_children(h,o,daggie)
establish_relationship(g, p)
add_children(g, p, livia)
establish_relationship(daggie, luiz)
add_children(daggie, luiz, allan)
fred = Person('Frederico')
lili = Person('Lili')
establish_relationship(fred, lili)
add_children(fred, lili, luiz)


n_people = count_people(lucas, checkHighest=True)
n_people = count_people(highest[0], visited=[], clear_list=True)
put(lucas)

for i in range(1,7):
    rearrange(i)

generation_above = [p for p in people_to_show if p.level == lucas.level - 1]
visited = set()
for person in generation_above:
    for rel in person.partners:
        visited.add(rel)

app = QApplication(sys.argv)
win = Window()
win.show()
win.show_people(people_to_show)
sys.exit(app.exec_())

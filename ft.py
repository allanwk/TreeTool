import numpy as np
import csv
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem
import sys

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(200,200,800,600)
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
            x = int(600 + (person.x * (self.person_width + self.spacing)))
            self.displayed_people.append(QtWidgets.QListWidget(self))
            self.displayed_people[-1].addItem(QListWidgetItem(person.name))
            self.displayed_people[-1].setGeometry(QtCore.QRect(x, y, self.person_width, self.level_heigth))
            self.displayed_people[-1].show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        for person in self.people:
            x1 = int(600 + (person.x * (self.person_width + self.spacing)))
            y1 = int(person.level * (self.level_heigth + self.spacing))
            for rel in person.partners:
                for partner in rel.partners:
                    if partner.name != person.name:
                        x2 = int(600 + (partner.x * (self.person_width + self.spacing)))
                        y2 = int(partner.level * (self.level_heigth + self.spacing))
                        qp.drawLine(x1, y1, x2, y2)
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
    
    def __str__(self):
        return "Relationship between {} and {}\nChildren: {}".format(self.partners[0].name, self.partners[1].name, self.children)

def establish_relationship(p1, p2):
    r = Partnership([p1, p2])
    p1.partners.append(r)
    p2.partners.append(r)
    
def add_children(p1, p2, children):
    if type(children) != list:
        children = [children]
    for relationship in p1.partners:
        for p in relationship.partners:
            if p.name != p1.name:
                rel = relationship
    for child in children:
        rel.children.append(child)
        child.parent_relationship = rel

def count_people(person, visited=[], count=0, level=0):
    if person.name not in visited:
        person.id = count
        person.level = level
        count += 1
        visited.append(person.name)
        if person.parent_relationship != None:
            for parent in person.parent_relationship.partners:
                if parent.name not in visited:
                    count = count_people(parent, visited, count, level-1)
        for relationship in person.partners:
            for p in relationship.partners:
                if p.name not in visited:
                    count = count_people(p, visited, count, level)
            for child in relationship.children:
                if child.name not in visited:
                    count = count_people(child, visited, count, level+1)
    return count

roots = []
leaves = []
people_per_level = {}
def get_adjacency(person, visited=[]):
    if person.name not in visited:
        print(person)
        visited.append(person.name)
        if person.level not in people_per_level:
            people_per_level[person.level] = 0
        people_per_level[person.level] += 1
        if person.parent_relationship != None:
            for parent in person.parent_relationship.partners:
                person_adjacency[parent.id][person.id] = 2
                get_adjacency(parent, visited)
        else:
            roots.append(person)
        if len(person.partners) == 0:
            leaves.append(person)
        for relationship in person.partners:
            if len(relationship.children) == 0:
                leaves.append(person)
            for p in relationship.partners:
                if p.name not in visited:
                    person_adjacency[person.id][p.id] = 1
                    get_adjacency(p, visited)
            for child in relationship.children:
                person_adjacency[person.id][child.id] = 2
                get_adjacency(child, visited)

usedx = {}
people_to_show = []
def put(person):
    people_to_show.append(person)
    print("Starting at", person)
    if person.level not in usedx:
        usedx[person.level] = []
    if person.level-1 not in usedx:
        usedx[person.level-1] = []
    if len(person.parent_relationship.partners) != 0:
       
        leftmost = person.x - len(person.parent_relationship.partners[0].parent_relationship.children) + 0.5
        rightmost = person.x + len(person.parent_relationship.partners[1].parent_relationship.children) + 0.5
        
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
            for sibling in p.parent_relationship.children:
                sibling.x += offset
                if sibling.name != p.name:
                    for rel in sibling.partners:
                        for partner in rel.partners:
                            if partner.name != sibling.name and partner.name not in repositioned:
                                partner.x += offset
            for p2 in people:
                if p2.name != p.name:
                    if p2.x >= p.x:
                        p2.x += offset
        else:
            print("skipping", p.name, ' no parents')

allan = Person('Allan')
livia = Person('Livia')
amelie = Person('Amelie')
jack = Person('Jack')
ruby = Person('Ruby')
john = Person('John')
lucas = Person('Lucas')
manuel = Person('Manuel')
establish_relationship(john, ruby)
establish_relationship(allan, livia)
establish_relationship(amelie, jack)
establish_relationship(manuel, Person("Jane"))
add_children(allan, livia, amelie)
add_children(allan, livia, manuel)
add_children(ruby, john, Person('James'))
add_children(ruby, john, jack)
add_children(amelie, jack, lucas)
daggie = Person('Daggie')
luiz = Person('Luiz')
g = Person('Gláucia')
p = Person('Paulo')
establish_relationship(g, p)
add_children(g, p, livia)
establish_relationship(daggie, luiz)
add_children(daggie, luiz, allan)


n_people = count_people(daggie)
person_adjacency = np.zeros((n_people, n_people), dtype=int)
get_adjacency(daggie)
print(people_per_level)
print(person_adjacency)
put(lucas)
rearrange(1)
rearrange(2)
rearrange(3)
app = QApplication(sys.argv)
win = Window()
win.show()
win.show_people(people_to_show)

sys.exit(app.exec_())

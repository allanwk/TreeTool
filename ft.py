import numpy as np
import csv
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QMenu, QAction, QLineEdit, QPushButton, QMessageBox
import sys
import csv
import codecs

class ListWidget(QtWidgets.QListWidget):
    def __init__(self, *args, **kwargs):
        super(ListWidget, self).__init__(*args, **kwargs)
    
    def setPerson(self, person):
        self.person = person
        
class PersonForm(QMainWindow):
    def __init__(self, parent=None):
        super(PersonForm, self).__init__(parent)
        self.setGeometry(200, 200, 200, 200)
        self.initUI()
    
    def setPerson(self, origin_person, person_type, second_parent_id=None):
        self.origin_person = origin_person
        self.second_parent_id = second_parent_id
        self.person_type = person_type
        if person_type == 'edit':
            self.nameTxtBox.setText(origin_person.name)

    def initUI(self):
        self.nameTxtBox = QLineEdit(self)
        self.nameTxtBox.move(20,20)
        self.nameTxtBox.resize(140,20)

        self.submitBtn = QPushButton("Concluído", self)
        self.submitBtn.clicked.connect(self.handle_click)
        self.submitBtn.move(20, 60)

        self.cancelBtn = QPushButton("Cancelar", self)
        self.cancelBtn.clicked.connect(self.close)
        self.cancelBtn.move(20, 90)

    def handle_click(self):
        name = self.nameTxtBox.text()
        p = Person(name)
        if self.person_type == 'sibling':
            self.parent().addSibling(self.origin_person, p)
        elif self.person_type == 'partner':
            self.parent().addPartner(self.origin_person, p)
        elif self.person_type == 'expartner':
            self.parent().addExPartner(self.origin_person, p)
        elif self.person_type == 'parent':
            self.parent().addParent(self.origin_person, p)
        elif self.person_type == 'edit':
            self.origin_person.name = name
            self.parent().update_view()
        elif self.person_type == 'child':
            self.parent().addChild(self.origin_person, self.second_parent_id, p)
        self.close()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.handle_click()

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
        self.shown_ids = []
        self.focus_person = jim

    def show_people(self, people):
        self.people = people
        self.shown_ids = [p.id for p in self.people]
        for person in people:
            y = int(person.level * (self.level_heigth + self.spacing))
            x = int(400 + (person.x * (self.person_width + self.spacing)))
            self.displayed_people.append(ListWidget(self))
            self.displayed_people[-1].setPerson(person)
            self.displayed_people[-1].installEventFilter(self)
            self.displayed_people[-1].addItem(QListWidgetItem(person.name))
            self.displayed_people[-1].addItem(QListWidgetItem(str(person.x)))
            self.displayed_people[-1].setGeometry(QtCore.QRect(x, y, self.person_width, self.level_heigth))
            self.displayed_people[-1].show()

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.ContextMenu:
            self.menu = QMenu(self)
            editAction = QAction('Editar', self)
            editAction.triggered.connect(lambda: self.showEditForm(event, source))
            deleteAction = QAction("Excluir", self)
            deleteAction.triggered.connect(lambda: self.deletePerson(event, source))
            addChildAction = QAction("Adicionar filho", self)
            addChildAction.triggered.connect(lambda: self.showParentOptions(event, source))
            addSiblingAction = QAction('Adicionar irmão', self)
            addSiblingAction.triggered.connect(lambda: self.showSiblingForm(event, source))
            addPartnerAction = QAction('Adicionar cônjuge atual', self)
            addPartnerAction.triggered.connect(lambda: self.showPartnerForm(event, source))
            addExPartnerAction = QAction('Adicionar cônjuge divorciado', self)
            addExPartnerAction.triggered.connect(lambda: self.showExPartnerForm(event, source))
            addParentAction = QAction('Adicionar pai/mãe', self)
            addParentAction.triggered.connect(lambda: self.showParentForm(event, source))
            setAsFocusAction = QAction('Mostrar árvore com foco nesta pessoa', self)
            setAsFocusAction.triggered.connect(lambda: self.changeFocus(event, source))
            self.menu.addAction(editAction)
            self.menu.addAction(deleteAction)
            self.menu.addAction(addChildAction)
            self.menu.addAction(addSiblingAction)
            self.menu.addAction(addPartnerAction)
            self.menu.addAction(addExPartnerAction)
            self.menu.addAction(addParentAction)
            self.menu.addAction(setAsFocusAction)
            self.menu.popup(QtGui.QCursor.pos())
        return super().eventFilter(source, event)

    def changeFocus(self, event, source):
        self.focus_person = source.person
        generate_tree_info(self.focus_person, checkHighest=True)
        generate_tree_info(highest[0], clear_list=True)
        self.update_view()
        self.update()

    def showEditForm(self, event, source):
        self.form = PersonForm(self)
        self.form.setPerson(source.person, 'edit')
        self.form.show()

    def showSiblingForm(self, event, source):
        self.form = PersonForm(self)
        self.form.setPerson(source.person, 'sibling')
        self.form.show()

    def deletePerson(self, event, source):
        if source.person.name != 'Desconhecido':
            self.msg = QMessageBox()
            self.msg.setIcon(QMessageBox.Question)
            self.msg.setText("Deseja mesmo excluir {}".format(source.person.name))
            self.msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            retval = self.msg.exec_()
            update = False
            if retval == QMessageBox.Ok:
                #Se tiver filhos, apenas tornar a pessoa desconhecida
                for rel in source.person.partners:
                    if len(rel.children) != 0:
                        update = True
                        if bool(rel.partners[0].name == 'Desconhecido') ^ bool(rel.partners[1] == 'Desconhecido'):
                            removeCouple(rel)
                        elif rel.partners[0].name != 'Desconhecido':
                            rel.partners[0].name = 'Desconhecido'
                        elif rel.partners[1].name != 'Desconhecido':
                            rel.partners[1].name = 'Desconhecido'
                        
            if update:
                self.update_view()
    
    def showParentOptions(self, event, source):
        if len(source.person.partners) > 1:
            self.submenu = QMenu(self)
            actions = []
            for rel in source.person.partners:
                for partner in rel.partners:
                    if partner.id != source.person.id:
                        actions.append(QAction(partner.name, self))
            for action in actions:
                action.triggered.connect(lambda: self.showChildForm(source.person, action.text()))
                self.submenu.addAction(action)
            self.submenu.setTitle("Filho com:")
            self.submenu.popup(QtGui.QCursor.pos())
        elif len(source.person.partners) == 1:
            for partner in source.person.partners[0].partners:
                if partner.id != source.person.id:
                    self.showChildForm(source.person, partner.id)
    
    def showChildForm(self, person, second_parent_id):
        self.form = PersonForm(self)
        self.form.setPerson(person, 'child', second_parent_id)
        self.form.show()

    def addChild(self, person, second_parent_id, child):
        for rel in person.partners:
            for partner in rel.partners:
                if partner.id == second_parent_id:
                    add_children(person, partner, child)
                    child.level = person.level + 1
                    generate_tree_info(highest[0], clear_list=True)
        self.update_view()

    def addSibling(self, person, sibling):
        person.parent_relationship.children.append(sibling)
        sibling.level = person.level
        sibling.parent_relationship = person.parent_relationship
        self.update_view()
        
    def showPartnerForm(self, event, source):
        self.form = PersonForm(self)
        self.form.setPerson(source.person, 'partner')
        self.form.show()
    
    def addPartner(self, person, partner):
        establish_relationship(person, partner)
        partner.level = person.level
        set_active_relationship(person, partner)
        self.update_view()
    
    def showExPartnerForm(self, event, source):
        self.form = PersonForm(self)
        self.form.setPerson(source.person, 'expartner')
        self.form.show()
    
    def addExPartner(self, person, partner):
        rel = establish_relationship(person, partner)
        partner.level = person.level
        rel.divorced = True
        self.update_view()

    def showParentForm(self, event, source):
        self.form = PersonForm(self)
        self.form.setPerson(source.person, 'parent')
        self.form.show()
    
    def addParent(self, person, parent):
        if len(person.parent_relationship.partners) == 0: 
            unknown = Person('Desconhecido')
            rel = establish_relationship(parent, unknown)
            for sibling in person.parent_relationship.children:
                rel.children.append(sibling)
                sibling.parent_relationship = rel
            generate_tree_info(parent, clear_list=True)
        
        else:
            for partner in person.parent_relationship.partners:
                if partner.name == 'Desconhecido':
                    partner.name = parent.name
        self.update_view()


    def clear_tree(self):
        for widget in self.displayed_people:
            widget.setParent(None)
        self.displayed_people.clear()

    def update_view(self):
        generate_positions(self.focus_person, lowest_level[0])
        self.clear_tree()
        self.show_people(people_to_show)

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
                    if partner.id != person.id and partner.id in self.shown_ids:
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

            if len(person.parent_relationship.partners) > 0 and person.parent_relationship.partners[0].id in self.shown_ids:
                qp.drawLine(x1+self.person_width/2, y1, x1 + self.person_width/2, y1-self.spacing/2)
            if len(person.parent_relationship.children) > 1:
                shown_siblings = 0
                for sib in person.parent_relationship.children:
                    if sib.id in self.shown_ids:
                        shown_siblings += 1
                if shown_siblings > 1:
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
        self.groupped = False

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
        if len(self.partners) > 0:
            return "Relationship between {} and {}\nChildren: {}".format(self.partners[0].name, self.partners[1].name, self.children)
        return "Empty relationship with children {}".format(self.children)

def establish_relationship(p1, p2):
    r = Partnership([p1, p2])
    p1.partners.append(r)
    p2.partners.append(r)
    return r
    
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

def removeCouple(rel):
    for partner in rel.partners:
        del partner
    rel.partners.clear()

highest = [None, float('inf')]
lowest_level = [-1]
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
        if level > lowest_level[0]:
            print("Found lowest level", level)
            lowest_level[0] = level
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

def generate_tree_info(person, highest = [], lowest_level = [], checkHighest=False, clear_list=False):
    highest.clear()
    highest = [None, float('inf')]
    people_ls.clear()
    lowest_level = [-1]
    print("lowest level", lowest_level[0])
    return count_people(person, checkHighest=checkHighest, clear_list=clear_list, visited=[])

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
ancestors = []
def put(person, focus_person_id=None):
    ancestors.append(person.id)
    if person.id != focus_person_id:
        people_to_show.append(person)
    print("Starting at", person.name)
    if person.level not in usedx:
        usedx[person.level] = []
    if person.level-1 not in usedx:
        usedx[person.level-1] = []
    
    if len(person.parent_relationship.partners) != 0:
        #Cálculo do número de pessoas à esquerda e direita no bloco acima,
        #considerando pais, tios e cônjuges dos tios
        people_left = len(person.parent_relationship.partners[0].parent_relationship.children)
        people_left += len(person.parent_relationship.partners[0].partners) - 1
        for sibling in person.parent_relationship.partners[0].parent_relationship.children:
            if sibling.id != person.parent_relationship.partners[0].id:
                people_left += len(sibling.partners)
        leftmost = person.x - people_left + 0.5
        leftmost += len(person.parent_relationship.partners[0].partners) - 1

        people_right = len(person.parent_relationship.partners[1].parent_relationship.children)
        people_right += len(person.parent_relationship.partners[1].partners) - 1
        for sibling in person.parent_relationship.partners[1].parent_relationship.children:
            if sibling.id != person.parent_relationship.partners[1].id:
                people_right += len(sibling.partners)
        rightmost = person.x + people_right + 0.5
        rightmost += len(person.parent_relationship.partners[1].partners) - 1

        try:
            left_dist = leftmost - max([a for a in usedx[person.level-1]])
        except:
            left_dist = float('inf')
        try:
            right_dist = max([a for a in usedx[person.level-1]]) - rightmost
        except:
            right_dist = float('inf')
        
        offset = 0
        if left_dist < 1:
            offset = people_left - left_dist
        """
        elif right_dist < 1:
            offset = -people_right - right_dist
        """
        print(people_left, people_right)
        print(left_dist, right_dist, offset)

        #Posicionando pais
        person.parent_relationship.partners[0].x = person.x - 0.5 + offset
        person.parent_relationship.partners[1].x = person.x + 0.5 + offset
        usedx[person.level-1].append(person.x - 0.5 + offset)
        usedx[person.level-1].append(person.x + 0.5 + offset)
        counter = 1
        parent = person.parent_relationship.partners[0]

        #Divórcios
        for rel in parent.partners:
            for p in rel.partners:
                if p.id != parent.id and p.id != person.parent_relationship.partners[1].id:
                    print(p.name, 'parent[0]')
                    people_to_show.append(p)
                    p.x = person.x - (0.5 + counter) + offset
                    counter += 1
                    usedx[person.level - 1].append(p.x)
        #Tios e conjuges
        for sibling in parent.parent_relationship.children:
            if sibling.id != parent.id:
                people_to_show.append(sibling)
                sibling.x = person.x - (0.5 + counter) + offset
                usedx[person.level - 1].append(sibling.x)
                counter += 1
                for rel in sibling.partners:
                    for p in rel.partners:
                        if p.id != sibling.id:
                            people_to_show.append(p)
                            p.x = person.x - (0.5 + counter) + offset
                            usedx[person.level - 1].append(p.x)
                            counter += 1
        counter = 1
        parent = person.parent_relationship.partners[1]
        for rel in parent.partners:
            for p in rel.partners:
                if p.id != parent.id and p.id != person.parent_relationship.partners[0].id:
                    print(p.name, 'parent[1]')
                    people_to_show.append(p)
                    p.x = person.x + (0.5 + counter) + offset
                    counter += 1
                    usedx[person.level - 1].append(p.x)
        for sibling in parent.parent_relationship.children:
            if sibling.id != parent.id:
                people_to_show.append(sibling)
                sibling.x = person.x + (0.5 + counter) + offset
                usedx[person.level - 1].append(sibling.x)
                counter += 1
                for rel in sibling.partners:
                    for p in rel.partners:
                        if p.id != sibling.id:
                            people_to_show.append(p)
                            p.x = person.x + (0.5 + counter) + offset
                            usedx[person.level - 1].append(p.x)
                            counter += 1
        for parent in person.parent_relationship.partners:
            put(parent)

def generate_positions(focus_person, n_levels):
    focus_person.x = 0
    usedx.clear()
    ancestors.clear()
    people_to_show.clear()
    put(focus_person, focus_person.id)
    if len(focus_person.parent_relationship.partners) > 0:
        generation_above = [p for p in people_to_show if p.level == focus_person.level - 1]
        generation_above.sort(key=lambda p: p.x)
        visited = []
        for person in generation_above:
            for rel in person.partners: 
                if rel not in visited and rel.partners[0] in people_to_show and rel.partners[1] in people_to_show:
                    visited.append(rel)
                    focus_rel = False
                    for child in rel.children:
                        if child.id == focus_person.id:
                            focus_rel = True
                            break
                    propagate_down(rel, focus_rel)
    else:
        propagate_down(focus_person.parent_relationship, True)
        
    for i in range(1, n_levels+1):
        rearrange(i, focus_person.level, focus_person)    
    

def propagate_down(rel, activate_recursion=False):
    if len(rel.children) > 0:
        print('prop', rel)
        if len(rel.partners) > 0:
            parent_level = rel.partners[0].level
            targetx = min(rel.partners[0].x, rel.partners[1].x)
        else:
            parent_level = rel.children[0].level - 1
            targetx = 0
        if parent_level not in usedx:
            usedx[parent_level] = []
        if parent_level+1 not in usedx:
            usedx[parent_level+1] = []

        
        people = 0
        for child in rel.children:
            people += 1
            for relationship in child.partners:
                people += 1
        
        leftmost = targetx - people + 1
        print(people, leftmost)

        try:
            left_dist = leftmost - max([a for a in usedx[parent_level+1]])
        except:
            left_dist = float('inf')
        
        offset = 0
        if left_dist < 1:
            if people == 1:
                offset = 1
            else:
                offset = abs(left_dist) + 1
        print(left_dist, offset)

        counter = 0
        for child in rel.children:
            people_to_show.append(child)
            child.x = targetx - counter + offset
            counter += 1
            usedx[parent_level + 1].append(child.x)
            print(child.name, child.x)
            for relationship in child.partners:
                for partner in relationship.partners:
                    if partner.id != child.id:
                        people_to_show.append(partner)
                        partner.x = targetx - counter + offset
                        counter += 1
                        usedx[parent_level + 1].append(partner.x)
                        print(partner.name, partner.x)

        if activate_recursion:
            for child in sorted(rel.children, key=lambda c: c.x):
                for relationship in sorted(child.partners, key=lambda r: (r.partners[0].x + r.partners[1].x)/2):
                    propagate_down(relationship, activate_recursion)

def rearrange(level, key_level, focus_person):
    print("rearranging level", level)
    repositioned = []
    people = [p for p in people_to_show if p.level == level]
    people.sort(key = lambda p: p.x)
    for p in people:
        if len(p.parent_relationship.partners) != 0:
            if p.parent_relationship.partners[0] not in people_to_show or p.parent_relationship.partners[1] not in people_to_show:
                print("skipping", p.name, ' no parents shown')
                continue
            #check if it is the rightmost sibling

            siblings = [sib for sib in p.parent_relationship.children if sib in people_to_show]
            siblings.sort(key = lambda p: p.x)
            siblings_x = 0
            for sib in siblings:
                siblings_x += sib.x
            siblings_x /= len(siblings)

            if p.x != siblings[-1].x:
                print("skipping", p.name, ' not rightmost sibling')
                continue
            repositioned.append(p.id)
            expected_x = (p.parent_relationship.partners[0].x + p.parent_relationship.partners[1].x)/2
            
            #Se a pessoa em foco tiver mais de um relacinamento,
            #os filhos de divórcios devem ser posicionados abaixo do pai
            #mais a esquerda
            if p.level >= focus_person.level:
                if p.parent_relationship.divorced:
                    expected_x = min(p.parent_relationship.partners[0].x, p.parent_relationship.partners[1].x)
            
            offset = expected_x - siblings_x
            print(p.name, p.x, p.parent_relationship.partners[0].x, p.parent_relationship.partners[1].x, offset)
            
            if offset < 0:
                print("triggering recursion from ", p.name, offset)
                offset_above(p.parent_relationship.partners[1], -2 * offset, level-1, ancestors, p.id in ancestors)
                continue
            for p2 in people:
                if p2.id != p.id:
                    if p2.x >= p.x:
                        p2.x += offset
            
            for sibling in p.parent_relationship.children:
                sibling.x += offset
                if sibling.id != p.id:
                    for rel in sibling.partners:
                        for partner in rel.partners:
                            if partner.id != sibling.id and partner.id not in repositioned:
                                partner.x += offset
            
            if len(p.partners) > 1 or p.level >= key_level:
                for rel in p.partners:
                    for partner in rel.partners:
                        if partner.id != p.id and partner.x < p.x:
                            partner.x += offset
                            

        else:
            print("skipping", p.name, ' no parents')

def offset_subtree(person, caller_rel, offset, visited=[]):
    if person.id not in visited and person in people_to_show:
        print("offsetsubtree", person, offset, visited)
        person.x += offset
        visited.append(person.id)
        if person.parent_relationship != None:
            for parent in person.parent_relationship.partners:
                if parent.id not in visited:
                    offset_subtree(parent, caller_rel, offset, visited)
            for sibling in person.parent_relationship.children:
                if sibling.id != person.id:
                    offset_subtree(sibling, caller_rel, offset, visited)
        for relationship in person.partners:
            for p in relationship.partners:
                if p.id not in visited:
                    offset_subtree(p, caller_rel, offset, visited)
            if relationship is not caller_rel:
                for child in relationship.children:
                    if child.id not in visited:
                        offset_subtree(child, caller_rel, offset, visited)

def offset_above(p, offset, level, ancestors, called_by_ancestor=True):
    print(p.name, p.x)
    print("recursion at ", p, ancestors, called_by_ancestor)
    
    people = [pe for pe in people_to_show if pe.level == level and pe.x >= p.x]
    people.sort(key = lambda p: p.x)
    for p2 in people:
        p2.x += offset
    
    if len(p.parent_relationship.partners) != 0:
        offset_subtree(p.parent_relationship.partners[0], p.parent_relationship, offset, [])

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
joe = Person('Joe')
jim = Person('Jim')
pam = Person('Pam')
c = Person('Cris')

establish_relationship(jim, pam)
add_children(jim, pam, c)
add_children(jim, pam, Person('claud'))
add_children(jim, pam, Person('cladaud'))
add_children(jim, pam, Person('clauaddd'))
establish_relationship(allan, livia)
establish_relationship(amelie, jack)
establish_relationship(amelie, joe)
set_active_relationship(amelie, jack)
establish_relationship(john, ruby)
establish_relationship(john, Person('Jane'))
set_active_relationship(john, ruby)

add_children(ruby, john, jim)
add_children(allan, livia, amelie)
add_children(ruby, john, jack)
add_children(amelie, jack, lucas)
add_children(amelie, joe, Person('asfs'))


generate_tree_info(amelie, checkHighest=True)
generate_tree_info(highest[0], clear_list=True)
print("level", lowest_level[0])
#n_people = count_people(lucas, checkHighest=True)
#n_people = count_people(highest[0], visited=[], clear_list=True)
generate_positions(amelie, lowest_level[0])

app = QApplication(sys.argv)
win = Window()
win.show()
win.focus_person = amelie
win.show_people(people_to_show)
sys.exit(app.exec_())

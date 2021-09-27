from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QMenu, QAction, QLineEdit, QPushButton, QMessageBox
import sys
import csv
from tree_utils import *
from buchheim import buchheim, apply_offset
import os

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
    
    def setPerson(self, origin_person, person_type):
        self.origin_person = origin_person
        self.person_type = person_type
        if person_type == 'edit':
            self.nameTxtBox.setText(origin_person.name)
    
    def setRel(self, rel, person_type):
        self.rel = rel
        self.person_type = person_type

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
            partnership = self.origin_person.parent_relationship
            if partnership is None:
                partnership = Partnership()
                partnership.isPlaceholder = True
                partnership.add_children(self.origin_person)
            partnership.add_children(p)
            #self.parent().addSibling(self.origin_person, p)
        elif self.person_type == 'partner':
            self.parent().addPartner(self.origin_person, p)
        elif self.person_type == 'parent':
            self.parent().addParent(self.origin_person, p)
        elif self.person_type == 'edit':
            self.origin_person.name = name
            self.parent().update_view()
        elif self.person_type == 'child':
            self.rel.add_children(p)

        self.parent().update_view()
        self.close()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.handle_click()

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(200,200,800,400)
        self.setWindowTitle("Árvore Genealógica")
        self.displayed_rels = []
        self.usedx={}
        self.visited = []
        self.person_width = 50
        self.level_heigth = 50
        self.spacing = 20
        self.displayed_people = []
        self.shown_ids = []
        self.save_path = None
        self.rels = None
        self.focus_rel = None
        self.init_menubar()
        self.yoffset = self.menubar.frameGeometry().height()

    def init_menubar(self):
        self.menubar = self.menuBar()
        save_menu = QtWidgets.QMenu("Arquivo", self)
        self.menubar.addMenu(save_menu)
        load_action = QtWidgets.QAction('Abrir', self)
        load_action.triggered.connect(self.open_file)
        new_action = QtWidgets.QAction('Novo', self)
        new_action.triggered.connect(self.new_file)
        save_action = QtWidgets.QAction('Salvar', self)
        save_action.triggered.connect(self.save_file)
        save_as_action = QtWidgets.QAction('Salvar como', self)
        save_as_action.triggered.connect(self.save_as_file)

        save_menu.addAction(load_action)
        save_menu.addAction(new_action)
        save_menu.addAction(save_action)
        save_menu.addAction(save_as_action)

    def open_file(self):
        qfd = QtWidgets.QFileDialog(self)
        path = qfd.getOpenFileName(self, 'Selecione um arquivo')[0]
        if path == '':
            return
        rels = load_tree(path)
        self.rels = rels
        self.focus_rel = rels[0]
        self.update_view()
        self.save_path = path

    def new_file(self):
        self.focus_rel = None
        self.rels = None
        self.update_view()
        self.save_path = None

    def save_file(self):
        save_tree(self.save_path)

    def save_as_file(self):
        qfd = QtWidgets.QFileDialog(self)
        path = qfd.getSaveFileName(self, 'Selecione como')[0]
        filename = os.path.basename(path)
        extension = os.path.splitext(path)[1]
        if ret == qm.Yes:
            if extension == '':
                save_tree(path + '.csv')
            elif extension == '.csv':
                save_tree(path)

    def recursive_show(self, dt):
        if dt in self.displayed_rels:
            for child in dt.children:
                self.recursive_show(child)
            return
        self.displayed_rels.append(dt)
        partnership = dt.tree
        y = self.convert_y(dt.y)
        
        for index, partner in enumerate(partnership.partners):
            x = dt.x * 2
            if index == 0 and len(partnership.partners) == 1:
                x += 0.5
            elif index == 1:
                x += 1
            x = self.convert_x(x)
            person_widget = ListWidget(self)
            self.displayed_people.append(person_widget)
            partner.x = x
            partner.y = y
            person_widget.setPerson(partner)
            person_widget.installEventFilter(self)
            person_widget.addItem(QListWidgetItem(partner.name))
            person_widget.setGeometry(QtCore.QRect(x, y, self.person_width, self.level_heigth))
            person_widget.show()
       
        
        for child in dt.children:
            self.recursive_show(child)
    
    def show_siblings(self, root):
        p1, p2 = self.focus_rel.partners
        if p1.parent_relationship is not None:
            i = 1
            for rel in p1.parent_relationship.children:
                if rel != self.focus_rel:
                    rel.y = root.y
                    rel.x = root.x - i
                    
                i+=1

    def clear_tree(self):
        for widget in self.displayed_people:
            widget.setParent(None)
        self.displayed_people.clear()
        self.displayed_rels.clear()

    def update_view(self):
        self.clear_tree()
        if self.focus_rel is None:
            self.update()
            return
        
        down = buchheim(self.focus_rel)
        up = buchheim(self.focus_rel, inverse=True)

        if down.x > up.x:
            apply_offset(up, down.x - up.x, 0)
        elif up.x > down.x:
            apply_offset(down, up.x - down.x, 0)

        yoff = up.y - down.y
        apply_offset(down, 0, yoff)

        self.recursive_show(up)
        self.recursive_show(down)
        self.show_siblings(down)
        self.update()


    def convert_x(self, x):
        return int((x * (self.person_width + self.spacing)))

    def convert_y(self, level):
        return int(self.yoffset + level * (self.level_heigth + self.spacing))

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        shown_relationships = list(map(lambda dt: dt.tree, self.displayed_rels))
        for dt in self.displayed_rels:
            partnership = dt.tree
            if len(partnership.partners) == 2:
                #Linhas de relacionamento
                p1, p2 = partnership.partners
                x1 = int(p1.x + self.person_width)
                x2 = int(p2.x)
                y = int(p1.y + self.level_heigth / 2)
                qp.drawLine(x1, y, x2, y)
            
                #Linha vertical para conectar com os filhos
                if len(partnership.children) > 0:
                    x = int(p1.x + self.person_width + self.spacing / 2)
                    y1 = int(p1.y + self.level_heigth / 2)
                    y2 = int(p1.y + self.level_heigth + self.spacing / 2)
                    qp.drawLine(x, y1, x, y2)

            for partner in partnership.partners:
                if partner.parent_relationship is not None and partner.parent_relationship in shown_relationships:
                    x = int(partner.x + self.person_width / 2)
                    y1 = int(partner.y)
                    y2 = int(partner.y - self.spacing / 2)
                    qp.drawLine(x, y1, x, y2)

                    if partner.parent_relationship.isPlaceholder == False:
                        xp = int(partner.parent_relationship.partners[0].x + self.person_width + self.spacing / 2)
                        qp.drawLine(x, y2, xp, y2)

        qp.end()
    
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
            addParentAction = QAction('Adicionar pai/mãe', self)
            addParentAction.triggered.connect(lambda: self.showParentForm(event, source))
            setAsFocusAction = QAction('Mostrar árvore com foco nesta pessoa', self)
            setAsFocusAction.triggered.connect(lambda: self.changeFocus(event, source))
            self.menu.addAction(editAction)
            self.menu.addAction(deleteAction)
            self.menu.addAction(addChildAction)
            self.menu.addAction(addSiblingAction)
            self.menu.addAction(addPartnerAction)
            self.menu.addAction(addParentAction)
            self.menu.addAction(setAsFocusAction)
            self.menu.popup(QtGui.QCursor.pos())
        return super().eventFilter(source, event)

    def changeFocus(self, event, source):
        self.focus_rel = source.person.partnership
        self.update_view()
    
    def showEditForm(self, event, source):
        self.form = PersonForm(self)
        self.form.setPerson(source.person, 'edit')
        self.form.show()

    def showSiblingForm(self, event, source):
        self.form = PersonForm(self)
        self.form.setPerson(source.person, 'sibling')
        self.form.show()

    def deletePerson(self, event, source):
        pass
    
    def showParentOptions(self, event, source):
        partnership = source.person.partnership
        self.form = PersonForm(self)
        self.form.setRel(partnership, 'child')
        self.form.show()

    def showPartnerForm(self, event, source):
        pass
    
    def showParentForm(self, event, source):
        pass
    



def main():
    

    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
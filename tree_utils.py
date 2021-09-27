import csv
relationships = []
people = []

class Person:
    def __init__(self, name=None):
        self.name = name
        self.partnership = Partnership(self)
        self.y = None
        self.x = 0
        self.parent_relationship = None
        people.append(self)

    def __str__(self):
        return "Person: {}, level {}, x={}".format(self.name, self.y, self.x)

class Partnership:
    def __init__(self, *partners):
        self.partners = []
        self.establish_relationship(partners)
        self.children = []
        self.isPlaceholder = False
    
    def establish_relationship(self, *partners):
        for partner in partners[0]:
            partner.partnership = self
            self.partners.append(partner)
    
    def add_children(self, *ch):
        for child in ch:
            self.children.append(child.partnership)
            child.parent_relationship = self

    def __getitem__(self, key):
        if isinstance(key, int) or isinstance(key, slice): 
            return self.children[key]
        if isinstance(key, str):
            for child in self.children:
                if child.node == key: return child
    
    def __len__(self):
        return len(self.children)
    
    def __str__(self):
        if len(self.partners) == 2:
            return "Partnership: {} and {}".format(self.partners[0], self.partners[1])
        else:
            return "Partnership: {}".format(self.partners[0])

def update_relationships():
    relationships.clear()
    for person in people:
        if person.partnership not in relationships:
            relationships.append(person.partnership)


def save_tree(file):
    with open(file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        update_relationships()
        names = [person.name for person in people]
        for person in people:
            writer.writerow([person.name])

        for rel in relationships:
            row = [names.index(partner.name) for partner in rel.partners]
            for child_rel in rel.children:
                for child in child_rel.partners:
                    if child.parent_relationship == rel:
                        row.append(names.index(child.name))
            if len(row) > 1:
                writer.writerow(row)

def load_tree(file):
    people.clear()
    children_to_add = {}
    with open(file, 'r', newline='') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            if row[0].isalpha():
                Person(row[0])
            else:
                row = list(map(int, row))
                partner1 = people[row[0]]
                partner2 = people[row[1]]
                p = Partnership(partner1, partner2)
                if len(row) > 2:
                    children_ids = row[2:]
                    if p not in children_to_add:
                        children_to_add[p] = []
                    for child_id in children_ids:
                        children_to_add[p].append(people[child_id])
    
    for partnership, children in children_to_add.items():
        for child in children:
            partnership.add_children(child)

    update_relationships()
    return relationships
    



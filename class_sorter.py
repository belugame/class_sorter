import sys
from itertools import chain

from redbaron import RedBaron
from redbaron.nodes import ClassNode, EndlNode


class FileSorter(object):
    def __init__(self, file_name):
        with open(file_name, "r") as source_code:
            self.node = RedBaron(source_code.read())

    def sort(self):
        sorted_node = RedBaron(" ")
        for n in self.node:
            if type(n) == ClassNode:
                c = ClassSorter(n).sort()[0]
                sorted_node.append(c)
            else:
                sorted_node.append(n)
        del sorted_node[0]  # delete empty line needed to init new node
        return sorted_node


class ClassSorter(object):

    def __init__(self, class_node):
        self.node = class_node

    def clone_only_root(self, node):
        """ Clones class header and returns it with only a pass statement in it. """
        return RedBaron(node.dumps().split("\n")[0] + "\n    pass")

    def remove_empty_lines(self, node):
        """ Removes empty lines non-recursively (only between root nodes)"""
        new = self.clone_only_root(node)
        for n in node:
            if type(n) == EndlNode:
                continue
            while len(n) > 1 and not str(n[-1]).strip():
                n.pop()
            new[0].append(n)
        del new[0][0]  # delete "pass" needed to init new class
        return new

    def insert_comment_at_old_position(self, comment_node, new_code):
        """
        Assume that a comment node is always in reference to the node that is following. Hence look where the position
        of the node in the original code was and insert the commend before it, restoring the original comment-node
        order.
        """
        next_node_in_original_code = list(comment_node.next_generator())[1]
        # Finds methods:
        node_after_comment = new_code.find(next_node_in_original_code .type,
                                           name=next_node_in_original_code.name)
        if not node_after_comment:  # 2nd try: Finds variables
            def finder(node):
                return node.value == next_node_in_original_code.name.value
            node_after_comment = new_code.find(
                    next_node_in_original_code.type, target=finder)
        index = new_code.root[0].index(node_after_comment)
        new_code.root[0].insert(index, comment_node)

    def sort(self):
        """
        Sort class members as:
        - doc string
        - class variables
        - methods
        Leave comments where they were
        """
        # methods: setup, setupclass etc or check if exists in parent class, then test_
        stripped_node = self.remove_empty_lines(self.node)
        assignments = self.get_assignments(stripped_node)
        methods = self.get_methods(stripped_node)
        strings = self.get_strings(stripped_node)
        comments = self.get_comments(self.node)

        members = chain(assignments, ["\n"], chain.from_iterable([[m, "\n"] for m in methods]))
        if strings:
            docstring = strings.data[0]
            comments += strings.data[1:]
            members = chain([docstring, "\n"], members)

        sorted_node = self.clone_only_root(self.node)
        for n in chain(members):
            sorted_node[0].append(n)

        # Delete temporarily needed "pass" statement
        del sorted_node[0][0]

        for c in comments:
            self.insert_comment_at_old_position(c, sorted_node)

        return sorted_node

    def get_assignments(self, node):
        assignments = sorted(node.root[0].node_list.find_all("AssignmentNode", recursive=False),
                             key=lambda a: a.dumps())
        return assignments or []

    def get_methods(self, node):
        methods = sorted(node.root[0].node_list.find_all("def", recursive=False), key=lambda d: d.name)
        return methods or []

    def get_strings(self, node):
        strings = node.root[0].node_list.find_all("StringNode", recursive=False)
        return strings or []

    def get_comments(self, node):
        __import__("pudb").set_trace()
        return node.root[0].node_list.find_all("comment", recursive=False)


if __name__ == "__main__":
    sorted_file = FileSorter(sys.argv[1]).sort()
    print sorted_file.dumps()

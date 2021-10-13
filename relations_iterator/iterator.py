import typing

from relations_iterator.relation_tree import ConfigurableRelationTree, RelationTree


from abc import ABC, abstractmethod


class AbstractRelationTreeIterator(ABC):
    @abstractmethod
    def get_iterator(self, tree: typing.Optional[RelationTree] = None):
        pass

    def __iter__(self):
        return self.get_iterator()


class RelationTreeIterator(AbstractRelationTreeIterator):
    def __init__(self, *, tree: ConfigurableRelationTree):
        self.tree = tree

    def get_iterator(self, tree: typing.Optional[RelationTree] = None):
        tree = tree if tree is not None else self.tree.tree
        for node, subtree in tree.items():
            yield node
            for relation, subnodes in subtree.items():
                yield from self.get_iterator(subnodes)

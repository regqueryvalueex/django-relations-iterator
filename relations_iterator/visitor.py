from abc import ABC, abstractmethod

from relations_iterator.relation_tree import TreeNode


class AbstractVisitor(ABC):
    @abstractmethod
    def visit(self, node: TreeNode):
        pass

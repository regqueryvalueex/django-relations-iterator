import typing

from django.db.models import Model

RelationTree = typing.Dict['TreeNode', typing.Dict[Model, 'RelationTree']]
RelationTreeConfig = typing.Dict[str, 'RelationTreeConfig']


class TreeNode:
    def __init__(self, *, instance: Model):
        self.instance = instance

    @property
    def model_class(self):
        return type(self.instance)

    def __hash__(self):
        return hash(f'{str(self.model_class)}-{self.instance.id}')

    def __repr__(self):
        return f'<{type(self).__name__} for {repr(self.instance).strip("<>")}>'


class ConfigurableRelationTree:
    def __init__(self, *, root: Model, structure: RelationTreeConfig):
        self.root = root
        self.structure = structure
        self.tree = self._collect()

    def _collect(
        self,
        *,
        instance: typing.Optional[Model] = None,
        structure: typing.Optional[RelationTreeConfig] = None
    ) -> RelationTree:
        root = instance if instance is not None else self.root
        structure = structure if structure is not None else self.structure
        subtree = {}
        tree = {self.get_node(instance=root): subtree}

        for relation, substructure in structure.items():
            related_instances = self._get_related_instances(instance=root, relation=relation)
            related_model = root._meta.get_field(relation).related_model
            subtree[related_model] = {}
            for related_instance in related_instances:
                subtree[related_model].update(self._collect(instance=related_instance, structure=substructure))

        return tree

    def _get_related_instances(self, *, instance: Model, relation: str) -> typing.List[Model]:
        field = instance._meta.get_field(relation)
        if field.one_to_one:
            instance = getattr(instance, relation, None)
            related_instances = [instance] if instance is not None else []
        else:
            related_instances = list(getattr(instance, relation).all())
        return related_instances

    def get_node(self, *, instance: Model) -> TreeNode:
        return TreeNode(instance=instance)

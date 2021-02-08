# stdlib
from enum import Enum
import inspect
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

# third party
from google.protobuf.reflection import GeneratedProtocolMessageType
from nacl.signing import VerifyKey

# syft relative
from ..... import lib
from .....decorators.syft_decorator_impl import syft_decorator
from .....proto.core.node.common.action.get_set_property_pb2 import (
    GetOrSetPropertyAction as GetOrSetPropertyAction_PB,
)
from ....common.serde.deserialize import _deserialize
from ....common.uid import UID
from ....io.address import Address
from ....store.storeable_object import StorableObject
from ...abstract.node import AbstractNode
from .common import ImmediateActionWithoutReply
from .run_class_method_action import RunClassMethodAction
from ....common.serde.serializable import bind_protobuf


class PropertyActions(Enum):
    SET = 1
    GET = 2
    DEL = 3

@bind_protobuf
class GetOrSetPropertyAction(ImmediateActionWithoutReply):
    def __init__(
        self,
        path: str,
        _self: Any,
        id_at_location: UID,
        address: Address,
        args: Union[Tuple[Any, ...], List[Any]],
        kwargs: Dict[Any, Any],
        action: PropertyActions,
        set_arg: Optional[Any] = None,
        msg_id: Optional[UID] = None,
    ):
        super().__init__(address, msg_id=msg_id)
        self.path = path
        self.id_at_location = id_at_location
        self.set_arg = set_arg
        self._self = _self
        self.action = action
        self.args = args
        self.kwargs = kwargs

    def intersect_keys(
        self, left: Dict[VerifyKey, UID], right: Dict[VerifyKey, UID]
    ) -> Dict[VerifyKey, UID]:
        return RunClassMethodAction.intersect_keys(left, right)

    def execute_action(self, node: AbstractNode, verify_key: VerifyKey) -> None:
        method = node.lib_ast.query(self.path).object_ref
        resolved_self = node.store.get_object(key=self._self.id_at_location)
        result_read_permissions = resolved_self.read_permissions

        resolved_args = []
        for arg in self.args:
            r_arg = node.store[arg.id_at_location]
            result_read_permissions = self.intersect_keys(
                result_read_permissions, r_arg.read_permissions
            )
            resolved_args.append(r_arg.data)

        resolved_kwargs = {}
        for arg_name, arg in self.kwargs.items():
            r_arg = node.store[arg.id_at_location]
            result_read_permissions = self.intersect_keys(
                result_read_permissions, r_arg.read_permissions
            )
            resolved_kwargs[arg_name] = r_arg.data

        if not inspect.isdatadescriptor(method):
            raise ValueError(f"{method} not an actual property!")

        (
            upcasted_args,
            upcasted_kwargs,
        ) = lib.python.util.upcast_args_and_kwargs(resolved_args, resolved_kwargs)

        data = resolved_self.data

        if self.action == PropertyActions.SET:
            result = method.__set__(data, *upcasted_args, **upcasted_kwargs)
        elif self.action == PropertyActions.GET:
            result = method.__get__(data, *upcasted_args, **upcasted_kwargs)
        elif self.action == PropertyActions.DEL:
            result = method.__del__(data, *upcasted_args, **upcasted_kwargs)
        else:
            raise ValueError(f"{self.action} not a valid action!")

        if lib.python.primitive_factory.isprimitive(value=result):
            result = lib.python.primitive_factory.PrimitiveFactory.generate_primitive(
                value=result, id=self.id_at_location
            )
        else:
            if hasattr(result, "id"):
                try:
                    if hasattr(result, "_id"):
                        # set the underlying id
                        result._id = self.id_at_location
                    else:
                        result.id = self.id_at_location

                    assert result.id == self.id_at_location
                except AttributeError:
                    raise Exception("MAKE VALID SCHEMA")

        if not isinstance(result, StorableObject):
            result = StorableObject(
                id=self.id_at_location,
                data=result,
                read_permissions=result_read_permissions,
            )

        node.store[self.id_at_location] = result

    @syft_decorator(typechecking=True)
    def _object2proto(self) -> GetOrSetPropertyAction_PB:
        """Returns a protobuf serialization of self.
        As a requirement of all objects which inherit from Serializable,
        this method transforms the current object into the corresponding
        Protobuf object so that it can be further serialized.
        :return: returns a protobuf object
        :rtype: GetOrSetPropertyAction_PB
        .. note::
            This method is purely an internal method. Please use object.serialize() or one of
            the other public serialization methods if you wish to serialize an
            object.
        """
        return GetOrSetPropertyAction_PB(
            path=self.path,
            id_at_location=self.id_at_location.serialize(),
            args=list(map(lambda x: x.serialize(), self.args)),
            kwargs={k: v.serialize() for k, v in self.kwargs.items()},
            address=self.address.serialize(),
            _self=self._self.serialize(),
            msg_id=self.id.serialize(),
            action=self.action.value,
        )

    @staticmethod
    def _proto2object(
        proto: GetOrSetPropertyAction_PB,
    ) -> "GetOrSetPropertyAction":
        """Creates a GetOrSetPropertyAction from a protobuf
        As a requirement of all objects which inherit from Serializable,
        this method transforms a protobuf object into an instance of this class.
        :return: returns an instance of GetOrSetPropertyAction
        :rtype: GetOrSetPropertyAction
        .. note::
            This method is purely an internal method. Please use syft.deserialize()
            if you wish to deserialize an object.
        """

        return GetOrSetPropertyAction(
            path=proto.path,
            id_at_location=_deserialize(blob=proto.id_at_location),
            address=_deserialize(blob=proto.address),
            _self=_deserialize(blob=proto._self),
            msg_id=_deserialize(blob=proto.msg_id),
            args=tuple(_deserialize(blob=x) for x in proto.args),
            kwargs={k: _deserialize(blob=v) for k, v in proto.kwargs.items()},
            action=PropertyActions(proto.action),
        )

    @staticmethod
    def get_protobuf_schema() -> GeneratedProtocolMessageType:
        """Return the type of protobuf object which stores a class of this type
        As a part of serialization and deserialization, we need the ability to
        lookup the protobuf object type directly from the object type. This
        static method allows us to do this.
        Importantly, this method is also used to create the reverse lookup ability within
        the metaclass of Serializable. In the metaclass, it calls this method and then
        it takes whatever type is returned from this method and adds an attribute to it
        with the type of this class attached to it. See the MetaSerializable class for details.
        :return: the type of protobuf object which corresponds to this class.
        :rtype: GeneratedProtocolMessageType
        """

        return GetOrSetPropertyAction_PB

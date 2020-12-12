# stdlib
import sys
from typing import List
from typing import Optional

# third party
from google.protobuf.reflection import GeneratedProtocolMessageType
from loguru import logger
import openmined_psi as psi
from packaging import version

# syft relative
from ...core.common.uid import UID
from ...core.store.storeable_object import StorableObject
from ...proto.util.vendor_bytes_pb2 import VendorBytes as VendorBytes_PB
from ...util import aggressive_set_attr
from ...util import get_fully_qualified_name


class SyRequest:
    def __init__(self, data: psi.proto_request = None):
        """Constructor method for the request Protobuf object.
        Returns:
            proto_request object.
        """
        if data:
            self.data = data
        else:
            self.data = psi.proto_request()

    def encrypted_elements_size(self) -> int:
        """Count of encrypted items in the request."""
        return self.data.encrypted_elements_size()

    def encrypted_elements(self, idx: int = None) -> list:  # type: ignore
        """Encrypted items in the request
        Args:
            idx: If provided, returns the item at the idx position. Otherwise, returns all elements.
        """
        if idx is not None:
            return self.data.encrypted_elements(idx)

        return self.data.encrypted_elements()  # type: ignore

    def add_encrypted_elements(self, el: bytes) -> None:
        """Add an item to the encrypted items in the request.
        Args:
            el: bytes buffer of the new item.
        """
        return self.data.add_encrypted_elements(el)

    def clear_encrypted_elements(self) -> None:
        """Clear the encrypted items in the request."""
        return self.data.clear_encrypted_elements()

    def reveal_intersection(self) -> bool:
        """Get reveal_intersection flag value"""
        return self.data.reveal_intersection()

    def clear_reveal_intersection(self) -> bool:
        """Reset reveal_intersection flag value"""
        return self.data.clear_reveal_intersection()

    def set_reveal_intersection(self, state: bool) -> bool:
        """Set reveal_intersection flag value"""
        return self.data.set_reveal_intersection(state)

    def save(self) -> bytes:
        """Save the protobuffer to wire format"""
        return self.data.save()

    def load(self, data: bytes) -> None:
        """Load the protobuffer from wire format"""
        return self.data.load(data)

    @classmethod
    def Load(cls, data: bytes) -> "SyRequest":
        """Load the protobuffer from wire format"""
        return cls(psi.cpp_proto_request.Load(data))


class SyRequestWrapper(StorableObject):
    def __init__(self, value: object):
        super().__init__(
            data=value,
            id=getattr(value, "id", UID()),
            tags=getattr(value, "tags", []),
            description=getattr(value, "description", ""),
        )
        self.value = value

    def _data_object2proto(self) -> VendorBytes_PB:
        proto = VendorBytes_PB()
        proto.obj_type = get_fully_qualified_name(obj=self.value)
        proto.vendor_lib = "openmined_psi"
        proto.vendor_lib_version = psi.__version__
        proto.content = self.value.save()  # type: ignore

        return proto

    @staticmethod
    def _data_proto2object(proto: VendorBytes_PB) -> "SyRequest":  # type: ignore
        vendor_lib = proto.vendor_lib
        lib_version = version.parse(proto.vendor_lib_version)

        if vendor_lib not in sys.modules:
            raise Exception(
                f"{vendor_lib} version: {proto.vendor_lib_version} is required"
            )
        else:
            if lib_version > version.parse(psi.__version__):
                log = f"Warning {lib_version} > local version {psi.__version__}"
                print(log)
                logger.info(log)

        sy_request = SyRequest()
        sy_request.load(proto.content)
        return sy_request

    @staticmethod
    def get_data_protobuf_schema() -> GeneratedProtocolMessageType:
        return VendorBytes_PB

    @staticmethod
    def get_wrapped_type() -> type:
        return SyRequest

    @staticmethod
    def construct_new_object(
        id: UID,
        data: StorableObject,
        description: Optional[str],
        tags: Optional[List[str]],
    ) -> StorableObject:
        data.id = id
        data.tags = tags
        data.description = description
        return data


aggressive_set_attr(
    obj=SyRequest,
    name="serializable_wrapper_type",
    attr=SyRequestWrapper,
)

# stdlib
import sys
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple

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


class SyServerSteup:
    def __init__(self, data: psi.proto_server_setup = None):
        if data:
            self.data = data
        else:
            self.data = psi.proto_server_setup()

    def bits(self) -> bytes:
        """Return the serialized setup message"""
        return self.data.bits()

    def set_bits(self, *args: Tuple[Any, ...], **kwargs: Any) -> bytes:
        """Set the serialized setup message"""
        return self.data.set_bits(args, kwargs)

    def clear_bits(self) -> None:
        """Clear the serialized setup message"""
        return self.data.clear_bits()

    def save(self) -> bytes:
        """Save the protobuffer to wire format"""
        return self.data.save()

    def load(self, data: bytes) -> None:
        """Load the protobuffer from wire format"""
        return self.data.load(data)

    @classmethod
    def Load(cls, data: bytes) -> "SyServerSteup":
        """Load the protobuffer from wire format"""
        return cls(data=psi.proto_server_setup.Load(data))


class SyServerSetupWrapper(StorableObject):
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
    def _data_proto2object(proto: VendorBytes_PB) -> "SyServerSteup":  # type: ignore
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

        sy_server_setup = SyServerSteup()
        sy_server_setup.load(proto.content)
        return sy_server_setup

    @staticmethod
    def get_data_protobuf_schema() -> GeneratedProtocolMessageType:
        return VendorBytes_PB

    @staticmethod
    def get_wrapped_type() -> type:
        return SyServerSteup

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
    obj=SyServerSteup,
    name="serializable_wrapper_type",
    attr=SyServerSetupWrapper,
)

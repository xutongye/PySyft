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
from ...util import aggressive_set_particular_attr
from ...util import get_fully_qualified_name


class ServerSetupWrapper(StorableObject):
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
    def _data_proto2object(proto: VendorBytes_PB) -> psi.proto_server_setup:
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

        server_setup = psi.proto_server_setup()
        server_setup.load(proto.content)
        return server_setup

    @staticmethod
    def get_data_protobuf_schema() -> GeneratedProtocolMessageType:
        return VendorBytes_PB

    @staticmethod
    def get_wrapped_type() -> type:
        return psi.proto_server_setup

    @staticmethod
    def construct_new_object(
        id: UID,
        data: StorableObject,
        description: Optional[str],
        tags: Optional[List[str]],
    ) -> StorableObject:
        aggressive_set_particular_attr(obj=data, name="id", attr=id)
        aggressive_set_particular_attr(obj=data, name="tags", attr=tags)
        aggressive_set_particular_attr(obj=data, name="description", attr=description)
        return data


aggressive_set_attr(
    obj=psi.proto_server_setup,
    name="serializable_wrapper_type",
    attr=ServerSetupWrapper,
)

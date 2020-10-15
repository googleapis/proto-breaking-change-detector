from google.protobuf import descriptor_pb2 as desc

desc_set = desc.FileDescriptorSet()
with open("/Users/xiaozhenliu/proto-breaking-change-detector/test/testdata/protos/example/address_book.pb", "rb") as file:
    desc_set.ParseFromString(file.read())

for file in desc_set.file:
    print(file.message_type)
import sys, struct
from ctypes import *

class IMAGE_DOS_HEADER(Structure):
    _fields_ = [
        ('e_magic', c_ushort),
        ('e_cblp', c_ushort),
        ('e_cp', c_ushort),
        ('e_crlc', c_ushort),
        ('e_cparhdr', c_ushort),
        ('e_minalloc', c_ushort),
        ('e_maxalloc', c_ushort),
        ('e_ss', c_ushort),
        ('e_sp', c_ushort),
        ('e_csum', c_ushort),
        ('e_ip', c_ushort),
        ('e_cs', c_ushort),
        ('e_lfarlc', c_ushort),
        ('e_ovno', c_ushort),
        ('e_res1', c_ushort * 4),
        ('e_oemid', c_ushort),
        ('e_oeminfo', c_ushort),
        ('e_res2', c_ushort * 10),
        ('e_lfanew', c_long)
    ]

IMAGE_FILE_MACHINE_I386 = 0x014c

class IMAGE_FILE_HEADER(Structure):
    _fields_ = [
        ('Machine', c_ushort),
        ('NumberOfSections', c_ushort),
        ('TimeDateStamp', c_uint),
        ('PointerToSymbolTable', c_uint),
        ('NumberOfSymbols', c_uint),
        ('SizeOfOptionalHeader', c_ushort),
        ('Characteristics', c_ushort)
    ]

class IMAGE_DATA_DIRECTORY(Structure):
    _fields_ = [
        ('VirtualAddress', c_uint),
        ('Size', c_uint)
    ]

IMAGE_NUMBEROF_DIRECTORY_ENTRIES = 16
IMAGE_DIRECTORY_ENTRY_EXPORT     = 0
IMAGE_DIRECTORY_ENTRY_IMPORT     = 1
IMAGE_DIRECTORY_ENTRY_BASERELOC  = 5
IMAGE_DIRECTORY_ENTRY_TLS        = 9

class IMAGE_OPTIONAL_HEADER(Structure):
    _fields_ = [
        ('Magic', c_ushort),
        ('MajorLinkerVersion', c_ubyte),
        ('MinorLinkerVersion', c_ubyte),
        ('SizeOfCode', c_uint),
        ('SizeOfInitializedData', c_uint),
        ('SizeOfUninitializedData', c_uint),
        ('AddressOfEntryPoint', c_uint),
        ('BaseOfCode', c_uint),
        ('BaseOfData', c_uint),
        ('ImageBase', c_uint),
        ('SectionAlignment', c_uint),
        ('FileAlignment', c_uint),
        ('MajorOperatingSystemVersion', c_short),
        ('MinorOperatingSystemVersion', c_short),
        ('MajorImageVersion', c_short),
        ('MinorImageVersion', c_short),
        ('MajorSubsystemVersion', c_short),
        ('MinorSubsystemVersion', c_short),
        ('Win32VersionValue', c_uint),
        ('SizeOfImage', c_uint),
        ('SizeOfHeaders', c_uint),
        ('CheckSum', c_uint),
        ('Subsystem', c_short),
        ('DllCharacteristics', c_short),
        ('SizeOfStackReserve', c_uint),
        ('SizeOfStackCommit', c_uint),
        ('SizeOfHeapReserve', c_uint),
        ('SizeOfHeapCommit', c_uint),
        ('LoaderFlags', c_uint),
        ('NumberOfRvaAndSizes', c_uint),
        ('DataDirectory',
            IMAGE_DATA_DIRECTORY * IMAGE_NUMBEROF_DIRECTORY_ENTRIES),
    ]

class IMAGE_NT_HEADERS(Structure):
    _fields_ = [
        ('Signature', c_uint),
        ('FileHeader', IMAGE_FILE_HEADER),
        ('OptionalHeader', IMAGE_OPTIONAL_HEADER)
    ]

IMAGE_SIZEOF_SHORT_NAME = 8

class IMAGE_SECTION_HEADER_Misc(Union):
    _fields_ = [
        ('PhysicalAddress', c_uint),
        ('VirtualSize', c_uint)
    ]

class IMAGE_SECTION_HEADER(Structure):
    _fields_ = [
        ('Name', c_char * 8),
        ('Misc', IMAGE_SECTION_HEADER_Misc),
        ('VirtualAddress', c_uint),
        ('SizeOfRawData', c_uint),
        ('PointerToRawData', c_uint),
        ('PointerToRelocations', c_uint),
        ('PointerToLinenumbers', c_uint),
        ('NumberOfRelocations', c_short),
        ('NumberOfLinenumbers', c_short),
        ('Characteristics', c_uint)
    ]

class IMAGE_EXPORT_DIRECTORY(Structure):
    _fields_ = [
        ('Characteristics', c_uint),
        ('TimeDateStamp', c_uint),
        ('MajorVersion', c_short),
        ('MinorVersion', c_short),
        ('Name', c_uint),
        ('Base', c_uint),
        ('NumberOfFunctions', c_uint),
        ('NumberOfNames', c_uint),
        ('AddressOfFunctions', c_uint),
        ('AddressOfNames', c_uint),
        ('AddressOfNameOrdinals', c_uint)
    ]

class IMAGE_IMPORT_DESCRIPTOR_Union(Union):
    _fields_ = [
        ('Characteristics', c_uint),
        ('OriginalFirstThunk', c_uint)
    ]

class IMAGE_IMPORT_DESCRIPTOR(Structure):
    _anonymous_ = ('DummyUnionName', )
    _fields_ = [
        ('DummyUnionName', IMAGE_IMPORT_DESCRIPTOR_Union),
        ('TimeDateStamp', c_uint),
        ('ForwarderChain', c_uint),
        ('Name', c_uint),
        ('FirstThunk', c_uint)
    ]

IMAGE_ORDINAL_FLAG32 = 0x80000000

class IMAGE_THUNK_DATA32(Union):
    _fields_ = [
        ('ForwarderString', c_uint),
        ('Function', c_uint),
        ('Ordinal', c_uint),
        ('AddressOfData', c_uint)
    ]

class IMAGE_IMPORT_BY_NAME(Structure):
    _fields_ = [
        ('Hint', c_ushort),
    ]

class ImportedFunction:
    pass

class IMAGE_BASE_RELOCATION(Structure):
    _fields_ = [
        ('VirtualAddress', c_uint),
        ('SizeOfBlock', c_uint)
    ]

class IMAGE_FIXUP_ENTRY(Structure):
    _pack_ = 1
    _fields_ = [
        ('Offset', c_uint, 12),
        ('Type', c_uint, 4)
    ]

class IMAGE_TLS_DIRECTORY32(Structure):
    _fields_ = [
        ('StartAddressOfRawData', c_uint),
        ('EndAddressOfRawData', c_uint),
        ('AddressOfIndex', c_uint),
        ('AddressOfCallBacks', c_uint),
        ('SizeOfZeroFill', c_uint),
        ('Characteristics', c_uint)
    ]

def ctype_encode(obj):
    ret = []
    if not hasattr(obj, '_fields_'): return obj
    for name, field in obj._fields_:
        value = getattr(obj, name)
        if isinstance(value, Structure):
            ret.append({name: ctype_encode(value)})
        if hasattr(value, '_length_'):
            ret.append({name: [ctype_encode(x) for x in value]})
        else:
            ret.append({name: value})
    return ret

def roundup(num, align):
    return (num + align - 1) / align * align

class Address(int):
    def __init__(self, offset):
        self.addr = offset

    def apply(self, base):
        self.addr += base
        return self.addr

    def unapply(self, base):
        self.addr -= base
        return self.addr

    def __int__(self):
        return self.addr

class Section:
    def __init__(self):
        self._ro = []
        self._ra = []
        self._rva = []
        self._va = []
        self._buf = []

    # add the `real offset', `real address',
    # `relative virtual address' and `virtual
    # address' respectively to the offset given.
    def ro(self, addr):  self._ro.append(addr)  ; return addr
    def ra(self, addr):  self._ra.append(addr)  ; return addr
    def rva(self, addr): self._rva.append(addr) ; return addr
    def va(self, addr):  self._va.append(addr)  ; return addr

    def apply(self, image_base=0, virtual_offset=0, raw_offset=0):
        for addr in self._ro:  addr.apply(raw_offset)
        for addr in self._ra:  addr.apply(image_base + raw_offset)
        for addr in self._rva: addr.apply(virtual_offset)
        for addr in self._va:  addr.apply(image_base + virtual_offset)
        # apply the addresses to each child Section
        for section in self._buf:
            if isinstance(section, Section):
                section.apply(image_base, virtual_offset, raw_offset)

    def unapply(self, image_base=0, virtual_offset=0, raw_offset=0):
        for addr in self._ro:  addr.unapply(raw_offset)
        for addr in self._ra:  addr.unapply(image_base + raw_offset)
        for addr in self._rva: addr.unapply(virtual_offset)
        for addr in self._va:  addr.unapply(image_base + virtual_offset)
        # apply the addresses to each child Section
        for section in self._buf:
            if isinstance(section, Section):
                section.unapply(image_base, virtual_offset, raw_offset)

    def __iadd__(self, other):
        self._buf.append(other)
        return self

    def __len__(self):
        return len(str(self))

    def encode(self, obj, field=None, offset=0):
        if isinstance(obj, Address):
            return struct.pack('L', int(obj) + offset)

        if isinstance(obj, Section):
            # apply the offset so far
            x.apply(virtual_offset=offset, raw_offset=offset)
            ret = str(x)
            x.unapply(virtual_offset=offset, raw_offset=offset)
            return ret

        if hasattr(field, '_length_'):
            ret = ''
            for x in obj:
                tmp = self.encode(x, field._type_, offset)
                offset += len(tmp)
                ret += tmp
            # append padding
            return ret + '\x00' * (field._length_ - len(ret))

        if isinstance(obj, str):
            #print 'instance', type(obj), field
            return obj

        if hasattr(field, '_type_'):
            return struct.pack(field._type_, obj)

        if isinstance(obj, Structure):
            ret = ''
            for name, field in obj._fields_:
                tmp = self.encode(getattr(obj, name), field, offset)
                offset += len(tmp)
                ret += tmp
            return ret

        #print 'else', type(obj), offset, field
        # else...
        size = sizeof(field)
        buf = create_string_buffer(size)
        memmove(byref(buf), byref(obj), size)
        return buf[:size]

    def __str__(self):
        return ''.join([self.encode(x) for x in self._buf])

class Penis:
    def read(self, fname=None, raw=None):
        # get the entire contents of the pe file
        self.raw = raw if raw else file(fname, 'rb').read()

    # relative virtual address to raw offset
    def rva2ro(self, rva):
        for section in self.ImageSectionHeaders:
            if rva >= section.VirtualAddress and \
                    rva < section.VirtualAddress + section.SizeOfRawData:
                return rva - section.VirtualAddress + section.PointerToRawData
        raise Exception('Invalid Relative Virtual Address', hex(rva))

    # virtual address to raw offset
    def va2ro(self, rva):
        return self.rva2ro(rva - self.ImageNtHeaders.OptionalHeader.ImageBase)

    def parse(self):
        # parse Image Dos Header
        self.ImageDosHeader = IMAGE_DOS_HEADER.from_buffer_copy(self.raw)
        print ctype_encode(self.ImageDosHeader)

        # parse Image Nt Headers
        self.ImageNtHeaders = IMAGE_NT_HEADERS.from_buffer_copy(self.raw,
                self.ImageDosHeader.e_lfanew)
        print ctype_encode(self.ImageNtHeaders)

        # parse the Image Section Headers
        self.ImageSectionHeaders = []
        for index in xrange(self.ImageNtHeaders.FileHeader.NumberOfSections):
            # extract the Image Section Header
            offset = self.ImageDosHeader.e_lfanew + sizeof(c_uint) + \
                sizeof(IMAGE_FILE_HEADER) + \
                self.ImageNtHeaders.FileHeader.SizeOfOptionalHeader
            ImageSectionHeader = IMAGE_SECTION_HEADER.from_buffer_copy(self.raw,
                    offset + index * sizeof(IMAGE_SECTION_HEADER))

            # extract the Data from the Header
            ImageSectionHeader.raw = self.raw[
                    ImageSectionHeader.PointerToRawData:
                    ImageSectionHeader.PointerToRawData +
                    ImageSectionHeader.SizeOfRawData]

            # add the header
            self.ImageSectionHeaders.append(ImageSectionHeader)
            print ctype_encode(ImageSectionHeader)

        # parse the Import Address Table
        ImportAddressTableSection = \
            self.ImageNtHeaders.OptionalHeader.DataDirectory[
                    IMAGE_DIRECTORY_ENTRY_IMPORT]
        self.ImportAddressTable = []
        if ImportAddressTableSection.VirtualAddress and \
                ImportAddressTableSection.Size:
            # find the address
            offsetImageImportDescriptor = self.rva2ro(
                    ImportAddressTableSection.VirtualAddress)
            while True:
                # extract the Image Import Descriptor
                ImageImportDescriptor = \
                    IMAGE_IMPORT_DESCRIPTOR.from_buffer_copy(self.raw,
                        offsetImageImportDescriptor)
                offsetImageImportDescriptor += sizeof(IMAGE_IMPORT_DESCRIPTOR)

                # last Image Import Descriptor ends with a zero-structure
                if ImageImportDescriptor.Characteristics == 0: break

                # resolve library name
                library = self.rva2ro(ImageImportDescriptor.Name)
                library = self.raw[library:self.raw.find('\x00', library)]

                # resolve thunkOut and thunkIn
                thunkOut = self.rva2ro(ImageImportDescriptor.FirstThunk)
                thunkIn = thunkOut if \
                    ImageImportDescriptor.OriginalFirstThunk == 0 else \
                    self.rva2ro(ImageImportDescriptor.OriginalFirstThunk)

                # check if all lookups were successful
                if not library or not thunkOut or not thunkIn: break

                # thunk address of each Imported API
                thunkAddress = ImageImportDescriptor.FirstThunk
                while True:
                    entry = ImportedFunction()
                    thunk = IMAGE_THUNK_DATA32.from_buffer_copy(self.raw,
                            thunkIn)
                    if thunk.Function == 0: break

                    # Import by Ordinal rather than Function Name
                    if thunk.Ordinal & IMAGE_ORDINAL_FLAG32:
                        entry.ordinal = thunk.Ordinal & 0xffff
                        entry.function = None
                    # Import by Function Name
                    else:
                        nameOffset = self.rva2ro(thunk.AddressOfData)
                        importByName = IMAGE_IMPORT_BY_NAME.from_buffer_copy(
                                self.raw, nameOffset)
                        entry.ordinal = importByName.Hint
                        entry.function = create_string_buffer(
                                self.raw[nameOffset+2:]).value
                    entry.thunk = thunkAddress
                    entry.library = library

                    # add this entry
                    self.ImportAddressTable.append(entry)

                    thunkIn += sizeof(IMAGE_THUNK_DATA32)
                    thunkAddress += sizeof(IMAGE_THUNK_DATA32)

        # parse the Relocation Data
        RelocationDataSection = \
            self.ImageNtHeaders.OptionalHeader.DataDirectory[
                    IMAGE_DIRECTORY_ENTRY_BASERELOC]
        self.RelocationTable = []
        if RelocationDataSection.VirtualAddress and RelocationDataSection.Size:
            offsetImageBaseRelocation = \
                self.rva2ro(RelocationDataSection.VirtualAddress)
            while True:
                # extract Image Base Relocation object
                ImageBaseRelocation = IMAGE_BASE_RELOCATION.from_buffer_copy(
                        self.raw, offsetImageBaseRelocation)
                if ImageBaseRelocation.SizeOfBlock == 0: break

                offsetImageFixupEntry = offsetImageBaseRelocation + \
                    sizeof(IMAGE_BASE_RELOCATION)
                countImageFixupEntry = (ImageBaseRelocation.SizeOfBlock -
                    sizeof(IMAGE_BASE_RELOCATION)) / sizeof(IMAGE_FIXUP_ENTRY)

                # extract all Image Fixup Entries
                entries = (IMAGE_FIXUP_ENTRY * countImageFixupEntry). \
                    from_buffer_copy(self.raw, offsetImageFixupEntry)

                # add each entry
                for entry in entries:
                    if entry.Type != 3:
                        raise Exception('Unknown Relocation Type',
                                str(entry.Type))
                    self.RelocationTable.append(
                            ImageBaseRelocation.VirtualAddress + entry.Offset)

                # next block
                offsetImageBaseRelocation += ImageBaseRelocation.SizeOfBlock

            # sort the list of relocations
            self.RelocationTable.sort()

        # parse the Thread Local Storage info
        ThreadLocalStorageSection = \
            self.ImageNtHeaders.OptionalHeader.DataDirectory[
                    IMAGE_DIRECTORY_ENTRY_TLS]
        self.ThreadLocalStorageCallbacks = []
        if ThreadLocalStorageSection.VirtualAddress and \
                ThreadLocalStorageSection.Size:
            offsetImageTlsDirectory = self.rva2ro(
                    ThreadLocalStorageSection.VirtualAddress)
            ImageTlsDirectory = IMAGE_TLS_DIRECTORY32.from_buffer_copy(
                    self.raw, offsetImageTlsDirectory)
            offsetCallback = self.va2ro(ImageTlsDirectory.AddressOfCallBacks)
            while True:
                callback = c_uint.from_buffer_copy(self.raw,
                        offsetCallback).value
                if callback == 0: break

                self.ThreadLocalStorageCallbacks.append(callback)
                offsetCallback += sizeof(c_uint)

    # returns a section object
    def _create_iat(self):
        s = Section()
        names = Section()
        entries = Section()
        thunks = Section()

        libraries = sorted(set([entry.library for entry in
            self.ImportAddressTable]))
        for library in libraries:
            ImageImportDescriptor = IMAGE_IMPORT_DESCRIPTOR()
            ImageImportDescriptor.OriginalFirstThunk = \
                s.rva(Address(len(entries)))
            ImageImportDescriptor.TimeDateStamp = 0
            ImageImportDescriptor.ForwarderChain = -1
            ImageImportDescriptor.Name = s.rva(Address(len(names)))
            names += entry.library + '\x00'
            s += ImageImportDescriptor

            for entry in filter(lambda x: x.library == library,
                    self.ImportAddressTable):
                ImageImportByName = IMAGE_IMPORT_BY_NAME()
                ImageImportByName.Hint = 0
                names += ImageImportByName
                names += entry.function + '\x00'
                entries += IMAGE_THUNK_DATA32()

            # add an empty entry
            entries += IMAGE_THUNK_DATA32()

        # append an empty Image Import Descriptor
        s += IMAGE_IMPORT_DESCRIPTOR()

        # add each function entry
        s += entries

        # add all strings
        s += names
        return s

    def create(self, fname=True):
        # this buffer will contain the entire pe file
        buf = Section()

        # copy the ImageDosHeader
        buf += self.ImageDosHeader

        # copy the part between ImageNtHeaders and ImageDosHeader
        buf += self.raw[sizeof(self.ImageDosHeader):
                self.ImageDosHeader.e_lfanew]

        # copy the ImageNtHeaders
        buf += self.ImageNtHeaders

        # calculate size of all sections together
        # aligned nicely to the Section Alignment
        size = sum([roundup(len(section.raw),
                self.ImageNtHeaders.OptionalHeader.SectionAlignment)
                for section in self.ImageSectionHeaders])

        # copy the ImageSectionHeaders
        offset = self.ImageDosHeader.e_lfanew + sizeof(c_uint) + \
                sizeof(IMAGE_FILE_HEADER) + \
                self.ImageNtHeaders.FileHeader.SizeOfOptionalHeader

        # copy the headers of each section
        for section in self.ImageSectionHeaders:
            buf += section

        offset = roundup(len(buf),
                self.ImageNtHeaders.OptionalHeader.FileAlignment)
        buf += '\x00' * (offset - len(buf))

        # create all data sections etc

        # create Import Address Table
        iat = self._create_iat()

        # create Thread Local Storage

        # copy all sections
        relative_virtual_address = roundup(len(buf),
            self.ImageNtHeaders.OptionalHeader.SectionAlignment)
        for section in self.ImageSectionHeaders:
            section.PointerToRawData = len(buf)
            section.SizeOfRawData = len(section.raw)
            section.VirtualAddress = relative_virtual_address
            section.Misc.VirtualSize = roundup(section.SizeOfRawData,
                    self.ImageNtHeaders.OptionalHeader.SectionAlignment)
            relative_virtual_address += section.Misc.VirtualSize
            buf += section.raw + '\x00' * (roundup(section.SizeOfRawData,
                    self.ImageNtHeaders.OptionalHeader.FileAlignment) -
                    section.SizeOfRawData)

        # write the contents to a file
        buf = str(buf)
        if fname: file(fname, 'wb').write(buf)
        return buf

if __name__ == '__main__':
    # set a default parameter..
    sys.argv = (sys.argv[0], 'yasm.exe')
    if len(sys.argv) == 1:
        print 'Usage: %s <filename>' % sys.argv[0]
        exit(0)

    pe = Penis()
    pe.read(sys.argv[1])
    pe.parse()

    for dir in pe.ImageNtHeaders.OptionalHeader.DataDirectory:
        print 'datadir 0x%08x 0x%08x' % (dir.VirtualAddress, dir.Size)

    for section in pe.ImageSectionHeaders:
        print 'section %-8s 0x%08x 0x%08x 0x%08x 0x%08x' % (section.Name,
                section.VirtualAddress, section.Misc.VirtualSize,
                section.PointerToRawData, section.SizeOfRawData)

    for entry in pe.ImportAddressTable:
        print 'iat %s %d %s 0x%08x' % (entry.library, entry.ordinal,
                entry.function, entry.thunk)

    for x in pe.RelocationTable:
        print 'reloc 0x%08x' % x

    for cb in pe.ThreadLocalStorageCallbacks:
        print 'tls 0x%08x' % cb

    pe.create(sys.argv[1].replace('.exe', '.out.exe'))

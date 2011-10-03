from MemoryRange import MemoryRange
from MemoryStruct import MemoryStruct

class MemoryLib(MemoryRange):
  
  op_rts = 0x4e75
  
  def __init__(self, addr, lib, context):
    name = lib.get_name()
    MemoryRange.__init__(self, name, addr, lib.get_total_size())
    self.lib = lib
    self.ctx = context
    
    self.begin_addr = addr
    self.base_addr = addr + lib.get_neg_size()
    self.end_addr = self.base_addr + lib.get_pos_size()
    
    self.pos_mem = MemoryStruct(name, self.base_addr, lib.get_pos_struct())

  def __str__(self):
    return "%s base=%06x %s" %(MemoryRange.__str__(self),self.base_addr,str(self.lib))

  def set_trace(self, on):
    MemoryRange.set_trace(self, on)
    self.pos_mem.set_trace(on)

  def get_base_addr(self):
    return self.base_addr

  def get_pos_mem(self):
    return self.pos_mem

  def is_inside(self, addr):
    return ((addr >= self.begin_addr) and (addr < self.end_addr))

  def read_mem(self, width, addr):
    # pos range -> redirect to struct
    if addr >= self.base_addr:
      return self.pos_mem.read_mem(width, addr)
    # trap lib call and return RTS opcode
    elif(width == 1):
      val = self.op_rts
      self.trace_read(width, addr, val, text="TRAP")
      off = (self.base_addr - addr) / 6
      self.lib.call_vector(off,self,self.ctx)
      return val
    # invalid access to neg area
    else:
      raise InvalidMemoryAccessError(width, addr)

  def write_mem(self, width, addr, val):
    # pos range -> redirect to struct
    if addr >= self.base_addr:
      return self.pos_mem.write_mem(width, addr, val)
    # writes to neg area are not allowed for now
    else:
      raise InvalidMemoryAccessError(width, addr)

  def set_data(self, data, offset):
    # pos range -> redirect to struct
    if addr >= self.base_addr:
      return self.pos_mem.set_data(data, offset)
    # writes to neg area are not allowed for now
    else:
      raise InvalidMemoryAccessError(width, addr)

  def get_data(self, offset, size):
    # pos range -> redirect to struct
    if addr >= self.base_addr:
      return self.pos_mem.get_data(offset, size)
    # writes to neg area are not allowed for now
    else:
      raise InvalidMemoryAccessError(width, addr)

  def get_cstring(self, offset):
    # pos range -> redirect to struct
    if addr >= self.base_addr:
      return self.pos_mem.get_cstring(offset)
    # writes to neg area are not allowed for now
    else:
      raise InvalidMemoryAccessError(width, addr)

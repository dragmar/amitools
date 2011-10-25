from MemoryLayout import MemoryLayout
from Exceptions import InvalidMemoryAccessError

class MainMemory(MemoryLayout):
  
  def __init__(self, size):
    MemoryLayout.__init__(self, "main", 0, size)
    self.invalid_access = []
    self.force_quit = False
    self.exit_ex = None
    
  def get_read_funcs(self):
    return ( lambda addr: self.read_mem(0,addr),
             lambda addr: self.read_mem(1,addr),
             lambda addr: self.read_mem(2,addr))

  def get_write_funcs(self):
    return ( lambda addr,val: self.write_mem(0,addr,val),
             lambda addr,val: self.write_mem(1,addr,val),
             lambda addr,val: self.write_mem(2,addr,val))

  def read_mem(self, width, addr):
    try:
      if self.force_quit and width == 1:
        return 0x4e70 # RESET opcode
      return MemoryLayout.read_mem(self, width, addr)
    except InvalidMemoryAccessError as e:
      self.trace_read(e.width, e.addr, 0, text="OUT!");
      e.state = self.ctx.cpu.get_state()
      e.pc_range_offset = self.get_range_offset(e.state['pc'])
      self.invalid_access.append(e)
      self.force_quit = True
      return 0
    except BaseException as e:
      e.state = self.ctx.cpu.get_state()
      e.pc_range_offset = self.get_range_offset(e.state['pc'])
      self.exit_ex = e
      self.force_quit = True
      return 0

  def write_mem(self, width, addr, val):
    try:
      return MemoryLayout.write_mem(self, width, addr, val)
    except InvalidMemoryAccessError as e:
      self.trace_write(e.width, e.addr, 0, text="OUT!")
      e.state = self.ctx.cpu.get_state()
      e.pc_range_offset = self.get_range_offset(e.state['pc'])
      self.invalid_access.append(e)
      self.force_quit = True
      return None
    except BaseException as e:
      e.state = self.ctx.cpu.get_state()
      e.pc_range_offset = self.get_range_offset(e.state['pc'])
      self.exit_ex = e
      self.force_quit = True
      return 0
  
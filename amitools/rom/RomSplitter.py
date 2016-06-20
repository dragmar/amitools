import fnmatch

import KickRom
import RemusFile
import amitools.util.DataDir as DataDir
from amitools.binfmt.BinImage import *


class RomSplitter:
  def __init__(self, split_data_path=None):
    # get data file path
    if split_data_path is None:
      split_data_path = DataDir.ensure_data_sub_dir("splitdata")
    # setup remus file set
    self.rfs = RemusFile.RemusFileSet()
    self.rfs.load(split_data_path)
    # state
    self.chk_sum = None
    self.rom_data = None
    self.remus_rom = None

  def find_rom(self, rom_path):
    """load ROM and try to find a matching dat file.
       Returns True if ROM was matched"""
    self.rom_data = KickRom.Loader.load(rom_path)
    # get check sum
    kh = KickRom.Helper(self.rom_data)
    if kh.is_kick_rom():
      self.chk_sum = kh.read_check_sum()
    else:
      self.chk_sum = kh.calc_check_sum()
    # search rom in Remus data base
    self.remus_rom = self.rfs.find_rom(self.rom_data, self.chk_sum)
    return self.remus_rom

  def print_rom(self, out, show_entries=False):
    rom = self.remus_rom
    out("@%08x  +%08x  sum=%08x  sum_off=%08x  %s" % \
        (rom.base_addr, rom.size, rom.chk_sum, rom.sum_off, rom.name))
    if show_entries:
      for e in rom.entries:
        self.print_entry(out, e)

  def print_entry(self, out, entry):
    out("  @%06x  +%06x  =%06x  relocs=#%5d  %s" % \
        (entry.offset, entry.size, entry.offset+entry.size,
         len(entry.relocs), entry.name))

  def print_entries(self, out, entries):
    for e in entries:
      self.print_entry(out, e)

  def get_all_entries(self):
    return self.remus_rom.entries

  def query_entries(self, query_str):
    res = []
    for e in self.remus_rom.entries:
      if fnmatch.fnmatch(e.name, query_str):
        res.append(e)
    return res

  def extract_entry(self, entry):
    """return data, relocs"""
    data = self.rom_data[entry.offset:entry.offset+entry.size]
    relocs = entry.relocs
    return data, relocs

  def extract_bin_img(self, entry):
    data, relocs = self.extract_entry(entry)
    # create a bin image
    bi = BinImage(BIN_IMAGE_TYPE_HUNK)
    seg = Segment(SEGMENT_TYPE_CODE, len(data), data)
    bi.add_segment(seg)
    # create reloc for target segment
    rl = Relocations(seg.id)
    # add offsets
    for o in relocs:
      r = Reloc(o)
      rl.add_reloc(r)
    seg.add_reloc(seg.id, rl)
    # return final binary image
    return bi
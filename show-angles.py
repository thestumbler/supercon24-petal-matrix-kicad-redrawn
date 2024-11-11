#!/usr/bin/env python

from dataclasses import dataclass

tests = [
  '		(property "Reference" "LED26"',
  '			(at 1.605281 -1.193121 79)',
  '--',
  '		(property "Reference" "LED27"',
  '			(at 1.605283 -1.193109 65)',
  '--',
]

# There are 8 "chains" of LEDs:
# LED 0 ~ 8
# LED 8 ~ 14
# LED 15 ~ 21
# LED 22 ~ 28
# LED 29 ~ 35
# LED 36 ~ 42
# LED 43 ~ 49
# LED 50 ~ 56


@dataclass
class Part:
  refdes: str
  posn: list[float]
  angle: float
  valid: False
  def __post_init__(self):
    self.pre = self.refdes.rstrip('0123456789')
    self.seq = int( self.refdes[len(self.pre):] )
    # head = s.rstrip('0123456789')
    # tail = s[len(head):]
  def __repr__(self):
    if self.valid:
      return \
        f'{self.pre:s}.{self.seq:02d} ' \
        f'[ {self.posn[0]:8.3f}, {self.posn[1]:8.3f} ] ' \
        f'{self.angle:>8.1f}'
        # f'{self.valid:>10d}'
        # f'{self.refdes:<10s}'
    else:
      return 'not initialized'
  def __str__(self):
    return self.__repr__()
  def __lt__(a,b):
    return a.seq < b.seq


class Parts(list):
  def __str__(self):
    return '\n'.join(str(p) for p in self)
  def __repr__(self):
    return self.__str__()

class Parser:
  parts = Parts()
  pline = 0
  def __init__(self):
    pass

  def read(self, fname):
    if fname is not None:
      self.fname = fname
      with open(self.fname) as fp:
        for line in fp:
          fields = []
          for f in line.split():
            fields.append( f.strip(' ()"') )
          if self.pline == 0:
            if fields[0]=='at':
              self.posn = [ float(fields[1]), float(fields[2]) ]
              self.angle = float(fields[3])
              self.pline = 1
          elif self.pline == 1:
            if fields[0]=='property' and fields[1]=='Reference':
              self.refdes = fields[2]
              self.pline = 2;
            else:
              self.pline = 0
          elif self.pline == 2:
            if fields[0]=='--':
              self.valid = True
              self.pline = 0
              self.parts.append( \
                Part( self.refdes, self.posn, self.angle, self.valid )
              )
    self.parts.sort()
    return self.parts

fname = "led-angles-grep.txt"
parser = Parser()
parts = parser.read(fname);
print(parts)

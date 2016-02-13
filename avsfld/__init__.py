import ctypes as ct
import numpy as np
import os
import xdrlib
import operator as op
import sys

def write(path, v):
  path = os.path.expanduser(path)
  fid = open(path, 'wb')

  lines = []
  # write the ascii header
  lines.append('# AVS field file (written by avsfld.py)\n')
  ndim = len(v.shape)
  lines.append('ndim=%d\n' % ndim)
  for d in xrange(ndim):
    lines.append('dim%d=%d\n' % (d+1, v.shape[d]))
  lines.append('nspace=%d\n' % ndim)
  lines.append('veclen=1\n')

  if v.dtype == ct.c_float:
    lines.append('data=float_le\n')
  else:
    raise NotImplementedError('dtype %s not implemented' % str(v.dtype))
  lines.append('field=uniform\n')
  lines.append(chr(12))
  lines.append(chr(12))

  fid.writelines(lines)
  fid.write(v.swapaxes(0, ndim-1).tostring())
  fid.close()

def read(path):
  path = os.path.expanduser(path)
  fid = open(path, 'rb')

  # read the fld header
  ascii_header = []
  last_form_feed = False
  while True:
    next_char = fid.read(1)
    # end of ascii section
    if next_char == '' or (ord(next_char) == 12 and last_form_feed):
      break
    else:
      ascii_header.append(next_char)
    last_form_feed = ord(next_char) == 12
  header_lines = ("".join(ascii_header)).split("\n")

  # parse fld header
  header = {}
  def parse_line(line):
    split = line.split('=')
    return (split[0], " ".join(split[1:]))

  for k, v in [parse_line(line) for line in header_lines]:
    header[k] = v

  # get interesting info from header
  ndim = int(header['ndim'])
  dimnames = ["dim%d" % (n+1) for n in xrange(ndim)]
  shape = tuple([int(header[dimname]) for dimname in dimnames])

  if header['field'] != 'uniform':
    raise NotImplementedError('field %s not implemented' % header['field'])

  size = reduce(op.mul, shape)
  raw_data = None

  # external
  fname = None
  if 'variable 1 file' in header.keys():
    fid.close()
    p = os.path.dirname(path)
    if p != '': p = '%s/' % p
    fname = "%s%s" % (p,
        header['variable 1 file'].split(' ')[0])
    fid = open(fname, 'rb')

  if header['data'] == 'xdr_float':
    # slow path
    unpacker = xdrlib.Unpacker(fid.read())
    unpacked = unpacker.unpack_farray(size, unpacker.unpack_float)
    raw_data = np.asarray(unpacked, order='F', dtype=ct.c_float)
  elif header['data'] == 'float_le':
    if sys.byteorder != 'little':
      raise NotImplementedError('byte-swapping not implemented')
    raw_data = np.fromfile(fid, dtype=ct.c_float)
  elif header['data'] == 'byte':
    raw_data = np.fromfile(fid, dtype='uint8')
  else:
    raise NotImplementedError('datatype %s not implemented' % header['data'])

  fid.close()
  return raw_data.reshape(tuple(reversed(shape))).swapaxes(0,ndim-1)


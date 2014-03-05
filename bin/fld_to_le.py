import avsfld
import sys

for f in sys.argv[1:]:
  print('ensuring "%s" is in little endian' % f)
  try:
    v = avsfld.read(f)
    avsfld.write(f, v)
  except:
    print('error processing "%s"' % f)


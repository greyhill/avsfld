from distutils.core import setup

setup(
        name = 'avsfld',
        version = '0.0.1',
        author = 'Madison McGaffin',
        author_email = 'greyhill@gmail.com',
        packages = [ 'avsfld' ],
        scripts = [ 'bin/fld_to_le' ],
        url = 'http://github.com/greyhill/avsfld',
        description = 'Read/write AVS .fld files',
        install_requires = [
            'numpy',
            ],
        )


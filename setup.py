from distutils.core import setup

setup(
    name='Ojota',
    version='0.1.4',
    author='Felipe Lerena, Juan Pedro Fisanoti, Ezequiel Chan, Nicolas Sarubbi, Hernan Lozano, Nicolas Bases',
    author_email='flerena@msa.com.ar, fisadev@gmail.com, echan@msa.com.ar, nicosarubi@gmail.com, hernantz@gmail.com, nmbases@gmai.com',
    packages=['ojota'],
    scripts=[],
    url='http://pypi.python.org/pypi/Ojota/',
    license='LICENSE.txt',
    description='Flat File Database with ORM',
    long_description=open('README.txt').read(),
    install_requires=['pyaml'],
)

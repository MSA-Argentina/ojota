from ojota import Persona, Animal
from time import time

start = time()
print Persona.all()
print time() - start
start = time()
print Animal.all()
print time() - start

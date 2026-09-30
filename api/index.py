import sys
import os

# Adiciona o diretório backend ao path do Python para conseguir importar o main
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from main import app

# A Vercel precisa exportar o objeto WSGI do Flask
app = app
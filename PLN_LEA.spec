# -*- mode: python ; coding: utf-8 -*-
"""
Arquivo de especificação do PyInstaller para PLN_LEA (Standalone/Onefile).
Execute com: pyinstaller PLN_LEA.spec
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Coleta dados dos modelos spaCy
datas = []
datas += collect_data_files("pt_core_news_sm")
datas += collect_data_files("en_core_web_sm")

# Adiciona dados do spaCy base
datas += collect_data_files('spacy')

# Adiciona dados do thinc (backend do spaCy)
try:
    datas += collect_data_files('thinc')
except Exception:
    pass

# Adiciona dados do ttkbootstrap
try:
    datas += collect_data_files('ttkbootstrap')
except Exception:
    pass

# Adiciona dados do NLTK (corpora)
try:
    import nltk
    nltk_data_path = nltk.data.path[0] if nltk.data.path else None
    if nltk_data_path and os.path.exists(nltk_data_path):
        # Adiciona apenas os recursos necessários
        recursos_nltk = [
            'tokenizers/punkt',
            'tokenizers/punkt_tab',
            'corpora/stopwords',
            'corpora/machado',
            'corpora/gutenberg'
        ]
        for recurso in recursos_nltk:
            recurso_path = os.path.join(nltk_data_path, recurso)
            if os.path.exists(recurso_path):
                datas.append((recurso_path, os.path.join('nltk_data', recurso)))
                print(f"✓ NLTK recurso {recurso} incluído")
            else:
                print(f"⚠ NLTK recurso {recurso} não encontrado")
except Exception as e:
    print(f"Erro ao coletar dados NLTK: {e}")

# Hidden imports necessários
hiddenimports = [
    'spacy',
    'spacy.lang.pt',
    'spacy.lang.en',
    'spacy.pipeline',
    'thinc',
    'thinc.api',
    'thinc.backends',
    'thinc.backends.numpy_ops',
    'cymem',
    'cymem.cymem',
    'preshed',
    'preshed.maps',
    'blis',
    'blis.py',
    'murmurhash',
    'murmurhash.mrmr',
    'wasabi',
    'srsly',
    'srsly.msgpack',
    'srsly.json',
    'catalogue',
    'typer',
    'pydantic',
    'spacytextblob',
    'spacytextblob.spacytextblob',
    'textblob',
    'nltk',
    'nltk.tokenize',
    'nltk.tokenize.punkt',
    'nltk.corpus',
    'nltk.corpus.reader',
    'wikipediaapi',
    'ttkbootstrap',
    'ttkbootstrap.themes',
    'PIL',
    'PIL._tkinter_finder',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'numpy.testing',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# === MODO STANDALONE (ONEFILE) ===
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PLN_LEA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False = sem console (GUI pura)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Adicione: icon='icone.ico' se tiver um ícone
)

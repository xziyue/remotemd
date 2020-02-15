import os

_thisDir, _ = os.path.split(__file__)
projectDir, _ = os.path.split(_thisDir)
srcDir = os.path.join(projectDir, 'src')
htmlDir = os.path.join(projectDir, 'html')
testDir = os.path.join(projectDir, 'test')
editormdDir = os.path.join(projectDir, 'editor.md')
dictionaryDir = os.path.join(projectDir, 'dictionary')
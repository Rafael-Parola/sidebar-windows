' Launcher silencioso para o Sidebar (sem janela preta de terminal)
Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
currentDir = FSO.GetParentFolderName(WScript.ScriptFullName)
mainScript = currentDir & "\main.py"

' Executa com pythonw.exe de forma oculta
WshShell.Run "pythonw.exe """ & mainScript & """", 0, False

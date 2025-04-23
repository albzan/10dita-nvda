; ----------------------------------------------------
; -- 10Dita.iss --
; Setup file for 10Dita
; Author : Alberto Zanella
; ----------------------------------------------------

[Setup]
AppId=10Dita
AppName=10Dita
AppVersion=3.1
DefaultDirName={pf}\10Dita
DefaultGroupName=10Dita
UninstallDisplayIcon={app}\10dita.exe
Compression=lzma2
SolidCompression=yes
OutputDir=userdocs:Inno Setup Examples Output
AlwaysShowComponentsList=no


;List contained in the original SETUP.LST
;Here for reference only.
;;
;File1=@ctl3d32.dll,$(WinSysPathSysFile)
;File2=@Manuale.rtf,$(AppPath)
;File3=@Errore.wav,$(AppPath)
;File4=@DIECIDB.mdb,$(AppPath)
;File5=@Conferma.wav,$(AppPath)
;File6=@avviso2.wav,$(AppPath)
;File7=@avviso1.wav,$(AppPath)
;File8=@Avvio.wav,$(AppPath)
;File9=@FlxGdIT.dll,$(WinSysPath),,$(Shared)
;File10=@MSFLXGRD.OCX,$(WinSysPath),$(DLLSelfRegister),$(Shared)
;File11=@MCIIT.dll,$(WinSysPath),,$(Shared)
;File12=@MCI32.OCX,$(WinSysPath),$(DLLSelfRegister),$(Shared)
;File13=@RCHTXIT.DLL,$(WinSysPath),,$(Shared)
;File14=@RICHED32.DLL,$(WinSysPathSysFile)
;File15=@RICHTX32.OCX,$(WinSysPath),$(DLLSelfRegister),$(Shared)
;File16=@CmCtlIT.dll,$(WinSysPath),,$(Shared)
;File17=@comctl32.ocx,$(WinSysPath),$(DLLSelfRegister),$(Shared)
;File18=@VB5DB.dll,$(WinSysPath),,$(Shared)
;File19=@MSREPL35.DLL,$(WinSysPathSysFile)
;File20=@MSRD2X35.DLL,$(WinSysPathSysFile),$(DLLSelfRegister),
;File21=@expsrv.dll,$(WinSysPathSysFile)
;File22=@vbajet32.dll,$(WinSysPathSysFile)
;File23=@MSJINT35.DLL,$(WinSysPathSysFile)
;File24=@MSJTER35.DLL,$(WinSysPathSysFile)
;File25=@MSJET35.DLL,$(WinSysPathSysFile),$(DLLSelfRegister),
;File26=@DAO350.DLL,$(MSDAOPath),$(DLLSelfRegister),$(Shared)
;File27=@10dita.exe,$(AppPath)
;
[Files]
Source: "COMCAT.DLL"; DestDir: "{sys}"; Flags: onlyifdoesntexist regserver uninsneveruninstall
Source: "comctl32.ocx"; DestDir: "{sys}"; Flags: onlyifdoesntexist regserver uninsneveruninstall
Source: "MCI32.OCX"; DestDir: "{sys}"; Flags: onlyifdoesntexist regserver uninsneveruninstall
Source: "MSFLXGRD.OCX"; DestDir: "{sys}"; Flags: onlyifdoesntexist regserver uninsneveruninstall
Source: "RICHTX32.OCX"; DestDir: "{sys}"; Flags: onlyifdoesntexist regserver uninsneveruninstall
Source: "DAO350.DLL"; DestDir: "{sys}"; Flags: onlyifdoesntexist regserver uninsneveruninstall
Source: "MSRD2X35.DLL"; DestDir: "{sys}"; Flags: onlyifdoesntexist regserver uninsneveruninstall
Source: "MSJET35.DLL"; DestDir: "{sys}"; Flags: onlyifdoesntexist regserver uninsneveruninstall
Source: "msvbvm60.dll"; DestDir: "{sys}"; Flags: onlyifdoesntexist regserver uninsneveruninstall

Source: "*.dll"; DestDir: "{app}"
Source: "*.ocx"; DestDir: "{app}"
Source: "*.wav"; DestDir: "{app}"
Source: "*.tlb"; DestDir: "{app}"
Source: "*.mdb"; DestDir: "{app}"
Source: "Manuale.rtf"; DestDir: "{app}"; Flags: isreadme
Source: "10dita.exe"; DestDir: "{app}"; Flags: ignoreversion;

[Components]
Name: main; Description: main; Flags: fixed; Types: full compact custom;

[Icons]
Name: "{group}\10dita"; Filename: "{app}\10dita.exe"
Name: "{group}\Manuale Utente"; Filename: "{app}\Manuale.rtf"
Name: {commondesktop}\10Dita; Filename: {app}\10Dita.exe; Components: main;

[Languages]
Name: "it"; MessagesFile: "compiler:Languages\Italian.isl"

[Tasks]
Name: desktopicon; Description: "{cm:CreateDesktopIcon}"; Components: main;
;OpenmalariaTools: A pyGTK GUI for the openmalaria scientific application
;Copyright (C) 2005-2010 Swiss Tropical Institute and Liverpool School Of Tropical Medicine
;
;This program is free software: you can redistribute it and/or modify
;it under the terms of the GNU General Public License as published by
;the Free Software Foundation, either version 3 of the License, or
;(at your option) any later version.
;
;This program is distributed in the hope that it will be useful,
;but WITHOUT ANY WARRANTY; without even the implied warranty of
;MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;GNU General Public License for more details.
;
;You should have received a copy of the GNU General Public License
;along with this program.  If not, see <http://www.gnu.org/licenses/>.

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "openmalariaTools"
!define PRODUCT_VERSION "00.01"
!define PRODUCT_PUBLISHER "Swiss TPH"
!define PRODUCT_WEB_SITE "http://www.swisstph.ch"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\openMalaria.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Language Selection Dialog Settings
!define MUI_LANGDLL_REGISTRY_ROOT "${PRODUCT_UNINST_ROOT_KEY}"
!define MUI_LANGDLL_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_LANGDLL_REGISTRY_VALUENAME "NSIS:Language"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!insertmacro MUI_PAGE_LICENSE "license.txt"
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "all_in_one_installer_v00.01.exe"
InstallDir "$PROGRAMFILES\openmalariaTools"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Function .onInit
  !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

Section "openmalariaTools" SEC01
  SetOutPath "$INSTDIR\application\common"
  SetOverwrite try
  File "..\application\common\approxEqual.py"
  File "..\application\common\autoRegressionParameters.csv"
  File "..\application\common\compareCtsout.py"
  File "..\application\common\compareOutput.py"
  File "..\application\common\densities.csv"
  File "..\application\common\om.ico"
  File "..\application\common\policy.txt"
  File "..\application\common\scenario.xsd"
  File "..\application\common\scenario_10.xsd"
  File "..\application\common\scenario_11.xsd"
  File "..\application\common\scenario_12.xsd"
  File "..\application\common\scenario_13.xsd"
  File "..\application\common\scenario_14.xsd"
  File "..\application\common\scenario_15.xsd"
  File "..\application\common\scenario_16.xsd"
  File "..\application\common\scenario_17.xsd"
  File "..\application\common\scenario_18.xsd"
  File "..\application\common\scenario_19.xsd"
  File "..\application\common\scenario_2.xsd"
  File "..\application\common\scenario_20.xsd"
  File "..\application\common\scenario_3.xsd"
  File "..\application\common\scenario_4.xsd"
  File "..\application\common\scenario_5.xsd"
  File "..\application\common\scenario_6.xsd"
  File "..\application\common\scenario_7.xsd"
  File "..\application\common\scenario_8.xsd"
  File "..\application\common\scenario_9.xsd"
  File "..\application\common\settings.lgdfs"
  SetOutPath "$INSTDIR\application\experiment_creator"
  File "..\application\experiment_creator\experiment_creator.jar"
  SetOutPath "$INSTDIR\application\LiveGraph.1.14.Complete\Examples"
  File "..\application\LiveGraph.1.14.Complete\Examples\Demo-DataFile.dat"
  File "..\application\LiveGraph.1.14.Complete\Examples\Demo-DataFileSettings.lgdfs"
  File "..\application\LiveGraph.1.14.Complete\Examples\Demo-DataSeriesSettings.lgdss"
  File "..\application\LiveGraph.1.14.Complete\Examples\Demo-GraphSettings.lggs"
  SetOutPath "$INSTDIR\application\LiveGraph.1.14.Complete"
  File "..\application\LiveGraph.1.14.Complete\LiveGraph-SplashScreen.gif"
  File "..\application\LiveGraph.1.14.Complete\LiveGraph.1.14.Complete.jar"
  File "..\application\LiveGraph.1.14.Complete\LiveGraph.ico"
  File "..\application\LiveGraph.1.14.Complete\readme.txt"
  File "..\application\LiveGraph.1.14.Complete\session.lgdfs"
  File "..\application\LiveGraph.1.14.Complete\session.lgdss"
  File "..\application\LiveGraph.1.14.Complete\session.lggs"
  File "..\application\LiveGraph.1.14.Complete\SoftNetConsultUtils.2.01.slim.jar"
  SetOutPath "$INSTDIR\application\LiveGraph.2.0.beta01.Complete\Examples"
  File "..\application\LiveGraph.2.0.beta01.Complete\Examples\Demo-DataFile.lgdat"
  File "..\application\LiveGraph.2.0.beta01.Complete\Examples\Demo-DataFileSettings.lgdfs"
  File "..\application\LiveGraph.2.0.beta01.Complete\Examples\Demo-DataSeriesSettings.lgdss"
  File "..\application\LiveGraph.2.0.beta01.Complete\Examples\Demo-GraphSettings.lggs"
  SetOutPath "$INSTDIR\application\LiveGraph.2.0.beta01.Complete"
  File "..\application\LiveGraph.2.0.beta01.Complete\LiveGraph-SplashScreen.gif"
  File "..\application\LiveGraph.2.0.beta01.Complete\LiveGraph.2.0.beta01.Complete.jar"
  File "..\application\LiveGraph.2.0.beta01.Complete\LiveGraph.ico"
  File "..\application\LiveGraph.2.0.beta01.Complete\readme.txt"
  File "..\application\LiveGraph.2.0.beta01.Complete\SoftNetConsultUtils.2.01.slim.jar"
  SetOutPath "$INSTDIR\application"
  File "..\application\openMalaria.exe"
  SetOutPath "$INSTDIR\application\schemaTranslator"
  File "..\application\schemaTranslator\SchemaTranslator$BugCorrectionBehaviour.class"
  File "..\application\schemaTranslator\SchemaTranslator$IptiSpBehaviour.class"
  File "..\application\schemaTranslator\SchemaTranslator.class"
  File "..\application\schemaTranslator\SchemaTranslator.jar"
  File "..\application\schemaTranslator\SchemaTranslator.java"
  SetOutPath "$INSTDIR"
  File "..\JavaAppsRun.py"
  File "..\OpenMalariaRun.py"
  File "..\start_gui.pyw"
  CreateDirectory "$SMPROGRAMS\openmalariaTools"
  CreateShortCut "$SMPROGRAMS\openmalariaTools\openmalariaTools.lnk" "$INSTDIR\start_gui.pyw"
  CreateShortCut "$DESKTOP\openmalariaTools.lnk" "$INSTDIR\start_gui.pyw"
  File "..\VirtualTerminal.py"
  File "..\VirtualTerminal_win.py"
  CreateDirectory "$INSTDIR\run_scenarios"
  CreateDirectory "$INSTDIR\run_scenarios\outputs"
  CreateDirectory "$INSTDIR\run_scenarios\scenarios_to_run"
  CreateDirectory "$INSTDIR\examples"
SectionEnd

Section "python" SEC02
  SetOverwrite ifnewer
  File "python-2.6.4.msi"
  ExecWait '"msiexec" /i "$INSTDIR\python-2.6.4.msi"'
SectionEnd

Section "pyGTK Runtime" SEC03
  File "gtk2-runtime-2.16.0-2009-03-22-ash.exe"
  ExecWait "$INSTDIR\gtk2-runtime-2.16.0-2009-03-22-ash.exe"
SectionEnd

Section "pyGTK" SEC04
  File "pygtk-2.16.0.win32-py2.6.exe"
  ExecWait "$INSTDIR\pygtk-2.16.0.win32-py2.6.exe"
SectionEnd

Section "pycairo" SEC05
  File "pycairo-1.8.6.win32-py2.6.exe"
  ExecWait "$INSTDIR\pycairo-1.8.6.win32-py2.6.exe"
SectionEnd

Section "pygobject" SEC06
  File "pygobject-2.20.0.win32-py2.6.exe"
  ExecWait "$INSTDIR\pygobject-2.20.0.win32-py2.6.exe"
SectionEnd

Section -AdditionalIcons
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\openmalariaTools\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\openmalariaTools\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\application\openMalaria.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\application\openMalaria.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) has been successfully uninstalled."
FunctionEnd

Function un.onInit
!insertmacro MUI_UNGETLANGUAGE
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to uninstall $(^Name) and related components ?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\pygobject-2.20.0.win32-py2.6.exe"
  Delete "$INSTDIR\pycairo-1.8.6.win32-py2.6.exe"
  Delete "$INSTDIR\pygtk-2.16.0.win32-py2.6.exe"
  Delete "$INSTDIR\gtk2-runtime-2.16.0-2009-03-22-ash.exe"
  Delete "$INSTDIR\python-2.6.4.msi"
  Delete "$INSTDIR\VirtualTerminal_win.py"
  Delete "$INSTDIR\VirtualTerminal.py"
  Delete "$INSTDIR\start_gui.pyw"
  Delete "$INSTDIR\setup.py"
  Delete "$INSTDIR\setup.exe"
  Delete "$INSTDIR\OpenMalariaRun.py"
  Delete "$INSTDIR\JavaAppsRun.py"
  Delete "$INSTDIR\installer.nsi"
  Delete "$INSTDIR\application\schemaTranslator\SchemaTranslator.java"
  Delete "$INSTDIR\application\schemaTranslator\SchemaTranslator.jar"
  Delete "$INSTDIR\application\schemaTranslator\SchemaTranslator.class"
  Delete "$INSTDIR\application\schemaTranslator\SchemaTranslator$$IptiSpBehaviour.class"
  Delete "$INSTDIR\application\schemaTranslator\SchemaTranslator$$BugCorrectionBehaviour.class"
  Delete "$INSTDIR\application\openMalaria.exe"
  Delete "$INSTDIR\application\LiveGraph.2.0.beta01.Complete\SoftNetConsultUtils.2.01.slim.jar"
  Delete "$INSTDIR\application\LiveGraph.2.0.beta01.Complete\readme.txt"
  Delete "$INSTDIR\application\LiveGraph.2.0.beta01.Complete\LiveGraph.ico"
  Delete "$INSTDIR\application\LiveGraph.2.0.beta01.Complete\LiveGraph.2.0.beta01.Complete.jar"
  Delete "$INSTDIR\application\LiveGraph.2.0.beta01.Complete\LiveGraph-SplashScreen.gif"
  Delete "$INSTDIR\application\LiveGraph.2.0.beta01.Complete\Examples\Demo-GraphSettings.lggs"
  Delete "$INSTDIR\application\LiveGraph.2.0.beta01.Complete\Examples\Demo-DataSeriesSettings.lgdss"
  Delete "$INSTDIR\application\LiveGraph.2.0.beta01.Complete\Examples\Demo-DataFileSettings.lgdfs"
  Delete "$INSTDIR\application\LiveGraph.2.0.beta01.Complete\Examples\Demo-DataFile.lgdat"
  Delete "$INSTDIR\application\LiveGraph.1.14.Complete\SoftNetConsultUtils.2.01.slim.jar"
  Delete "$INSTDIR\application\LiveGraph.1.14.Complete\session.lggs"
  Delete "$INSTDIR\application\LiveGraph.1.14.Complete\session.lgdss"
  Delete "$INSTDIR\application\LiveGraph.1.14.Complete\session.lgdfs"
  Delete "$INSTDIR\application\LiveGraph.1.14.Complete\readme.txt"
  Delete "$INSTDIR\application\LiveGraph.1.14.Complete\LiveGraph.ico"
  Delete "$INSTDIR\application\LiveGraph.1.14.Complete\LiveGraph.1.14.Complete.jar"
  Delete "$INSTDIR\application\LiveGraph.1.14.Complete\LiveGraph-SplashScreen.gif"
  Delete "$INSTDIR\application\LiveGraph.1.14.Complete\Examples\Demo-GraphSettings.lggs"
  Delete "$INSTDIR\application\LiveGraph.1.14.Complete\Examples\Demo-DataSeriesSettings.lgdss"
  Delete "$INSTDIR\application\LiveGraph.1.14.Complete\Examples\Demo-DataFileSettings.lgdfs"
  Delete "$INSTDIR\application\LiveGraph.1.14.Complete\Examples\Demo-DataFile.dat"
  Delete "$INSTDIR\application\experiment_creator\experiment_creator.jar"
  Delete "$INSTDIR\application\common\settings.lgdfs"
  Delete "$INSTDIR\application\common\scenario_9.xsd"
  Delete "$INSTDIR\application\common\scenario_8.xsd"
  Delete "$INSTDIR\application\common\scenario_7.xsd"
  Delete "$INSTDIR\application\common\scenario_6.xsd"
  Delete "$INSTDIR\application\common\scenario_5.xsd"
  Delete "$INSTDIR\application\common\scenario_4.xsd"
  Delete "$INSTDIR\application\common\scenario_3.xsd"
  Delete "$INSTDIR\application\common\scenario_20.xsd"
  Delete "$INSTDIR\application\common\scenario_2.xsd"
  Delete "$INSTDIR\application\common\scenario_19.xsd"
  Delete "$INSTDIR\application\common\scenario_18.xsd"
  Delete "$INSTDIR\application\common\scenario_17.xsd"
  Delete "$INSTDIR\application\common\scenario_16.xsd"
  Delete "$INSTDIR\application\common\scenario_15.xsd"
  Delete "$INSTDIR\application\common\scenario_14.xsd"
  Delete "$INSTDIR\application\common\scenario_13.xsd"
  Delete "$INSTDIR\application\common\scenario_12.xsd"
  Delete "$INSTDIR\application\common\scenario_11.xsd"
  Delete "$INSTDIR\application\common\scenario_10.xsd"
  Delete "$INSTDIR\application\common\scenario.xsd"
  Delete "$INSTDIR\application\common\policy.txt"
  Delete "$INSTDIR\application\common\om.ico"
  Delete "$INSTDIR\application\common\densities.csv"
  Delete "$INSTDIR\application\common\compareOutput.py"
  Delete "$INSTDIR\application\common\compareCtsout.py"
  Delete "$INSTDIR\application\common\autoRegressionParameters.csv"
  Delete "$INSTDIR\application\common\approxEqual.py"

  Delete "$SMPROGRAMS\openmalariaTools\Uninstall.lnk"
  Delete "$SMPROGRAMS\openmalariaTools\Website.lnk"
  Delete "$DESKTOP\openmalariaTools.lnk"
  Delete "$SMPROGRAMS\openmalariaTools\openmalariaTools.lnk"

  RMDir "$SMPROGRAMS\openmalariaTools"
  RMDir "$INSTDIR\application\schemaTranslator"
  RMDir "$INSTDIR\application\LiveGraph.2.0.beta01.Complete\Examples"
  RMDir "$INSTDIR\application\LiveGraph.2.0.beta01.Complete"
  RMDir "$INSTDIR\application\LiveGraph.1.14.Complete\Examples"
  RMDir "$INSTDIR\application\LiveGraph.1.14.Complete"
  RMDir "$INSTDIR\application\experiment_creator"
  RMDir "$INSTDIR\application\common"
  RMDir "$INSTDIR\application"
  RMDir "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd
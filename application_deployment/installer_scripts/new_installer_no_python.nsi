; Script generated by the HM NIS Edit Script Wizard.

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "openmalariaTools"
!define PRODUCT_VERSION "00.07"
!define PRODUCT_PUBLISHER "SwissTPH"
!define PRODUCT_WEB_SITE "www.swisstph.ch"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\openMalaria.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!insertmacro MUI_PAGE_LICENSE "license.txt"
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\openmalariatools.exe"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "openMalariaTools_installer_v00.07.exe"
InstallDir "$PROGRAMFILES\openmalariaTools"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Section "openMalariaTools" SEC01
  SetOutPath "$INSTDIR\examples"
  File "..\examples\scenario1.xml"
  File "..\examples\scenario10.xml"
  File "..\examples\scenario11.xml"
  File "..\examples\scenario12.xml"
  File "..\examples\scenario1DayIntervs.xml"
  File "..\examples\scenario2.xml"
  File "..\examples\scenario3.xml"
  File "..\examples\scenario4.xml"
  File "..\examples\scenario5.xml"
  File "..\examples\scenario6.xml"
  File "..\examples\scenario9.xml"
  File "..\examples\scenarioCohort.xml"
  File "..\examples\scenarioEffectiveDrug.xml"
  File "..\examples\scenarioEmpirical.xml"
  File "..\examples\scenarioESCMTest.xml"
  File "..\examples\scenarioIPT.xml"
  File "..\examples\scenarioMolineaux.xml"
  File "..\examples\scenarioNamawalaArabiensis.xml"
  File "..\examples\scenarioPenny.xml"
  File "..\examples\scenarioR_0.xml"
  File "..\examples\scenarioVC-TS.xml"
  File "..\examples\scenarioVecFullTest.xml"
  File "..\examples\scenarioVecMonthly.xml"
  File "..\examples\scenarioVecTest.xml"
  SetOutPath "$INSTDIR\etc\fonts"
  File "..\etc\fonts\fonts.conf"
  File "..\etc\fonts\fonts.dtd"
  SetOutPath "$INSTDIR\etc\gtk-2.0"
  File "..\etc\gtk-2.0\about.png"
  File "..\etc\gtk-2.0\add.png"
  File "..\etc\gtk-2.0\apply.png"
  File "..\etc\gtk-2.0\broken_image.png"
  File "..\etc\gtk-2.0\cancel.png"
  File "..\etc\gtk-2.0\cdrom_16.png"
  File "..\etc\gtk-2.0\cdrom_24.png"
  File "..\etc\gtk-2.0\clear.png"
  File "..\etc\gtk-2.0\close.png"
  File "..\etc\gtk-2.0\colorselector.png"
  File "..\etc\gtk-2.0\connect.png"
  File "..\etc\gtk-2.0\convert.png"
  File "..\etc\gtk-2.0\delete_16.png"
  File "..\etc\gtk-2.0\delete_24.png"
  File "..\etc\gtk-2.0\dialog_authentication.png"
  File "..\etc\gtk-2.0\dialog_error.png"
  File "..\etc\gtk-2.0\dialog_info.png"
  File "..\etc\gtk-2.0\dialog_question.png"
  File "..\etc\gtk-2.0\dialog_warning.png"
  File "..\etc\gtk-2.0\directory.png"
  File "..\etc\gtk-2.0\disconnect.png"
  File "..\etc\gtk-2.0\document-new.png"
  File "..\etc\gtk-2.0\document-open.png"
  File "..\etc\gtk-2.0\document-print-preview.png"
  File "..\etc\gtk-2.0\document-print.png"
  File "..\etc\gtk-2.0\document-properties.png"
  File "..\etc\gtk-2.0\document-save-as.png"
  File "..\etc\gtk-2.0\document-save.png"
  File "..\etc\gtk-2.0\edit-copy_16.png"
  File "..\etc\gtk-2.0\edit-copy_24.png"
  File "..\etc\gtk-2.0\edit-cut_16.png"
  File "..\etc\gtk-2.0\edit-cut_24.png"
  File "..\etc\gtk-2.0\edit-find-replace.png"
  File "..\etc\gtk-2.0\edit-find.png"
  File "..\etc\gtk-2.0\edit-paste.png"
  File "..\etc\gtk-2.0\edit-redo.png"
  File "..\etc\gtk-2.0\edit-undo.png"
  File "..\etc\gtk-2.0\edit.png"
  File "..\etc\gtk-2.0\execute.png"
  File "..\etc\gtk-2.0\file.png"
  File "..\etc\gtk-2.0\floppy.png"
  File "..\etc\gtk-2.0\font.png"
  File "..\etc\gtk-2.0\format-indent-less.png"
  File "..\etc\gtk-2.0\format-indent-more.png"
  File "..\etc\gtk-2.0\format-justify-center.png"
  File "..\etc\gtk-2.0\format-justify-fill.png"
  File "..\etc\gtk-2.0\format-justify-left.png"
  File "..\etc\gtk-2.0\format-justify-right.png"
  File "..\etc\gtk-2.0\format-text-bold.png"
  File "..\etc\gtk-2.0\format-text-italic.png"
  File "..\etc\gtk-2.0\format-text-strikethrough.png"
  File "..\etc\gtk-2.0\format-text-underline.png"
  File "..\etc\gtk-2.0\fullscreen.png"
  File "..\etc\gtk-2.0\gdk-pixbuf.loaders"
  File "..\etc\gtk-2.0\go-bottom.png"
  File "..\etc\gtk-2.0\go-down.png"
  File "..\etc\gtk-2.0\go-first.png"
  File "..\etc\gtk-2.0\go-home.png"
  File "..\etc\gtk-2.0\go-jump.png"
  File "..\etc\gtk-2.0\go-last.png"
  File "..\etc\gtk-2.0\go-next.png"
  File "..\etc\gtk-2.0\go-previous.png"
  File "..\etc\gtk-2.0\go-top.png"
  File "..\etc\gtk-2.0\go-up.png"
  File "..\etc\gtk-2.0\gtk.immodules"
  File "..\etc\gtk-2.0\gtkrc"
  File "..\etc\gtk-2.0\gtkrc.default"
  File "..\etc\gtk-2.0\harddisk.png"
  File "..\etc\gtk-2.0\help.png"
  File "..\etc\gtk-2.0\iconrc"
  File "..\etc\gtk-2.0\iconrc.in"
  File "..\etc\gtk-2.0\im-multipress.conf"
  File "..\etc\gtk-2.0\index.png"
  File "..\etc\gtk-2.0\info.png"
  File "..\etc\gtk-2.0\leave_fullscreen.png"
  File "..\etc\gtk-2.0\media-ffwd.png"
  File "..\etc\gtk-2.0\media-next.png"
  File "..\etc\gtk-2.0\media-pause.png"
  File "..\etc\gtk-2.0\media-play.png"
  File "..\etc\gtk-2.0\media-prev.png"
  File "..\etc\gtk-2.0\media-record.png"
  File "..\etc\gtk-2.0\media-rewind.png"
  File "..\etc\gtk-2.0\media-stop.png"
  File "..\etc\gtk-2.0\network.png"
  File "..\etc\gtk-2.0\no.png"
  File "..\etc\gtk-2.0\ok.png"
  File "..\etc\gtk-2.0\preferences.png"
  File "..\etc\gtk-2.0\quit.png"
  File "..\etc\gtk-2.0\remove.png"
  File "..\etc\gtk-2.0\revert.png"
  File "..\etc\gtk-2.0\sort_ascending.png"
  File "..\etc\gtk-2.0\sort_descending.png"
  File "..\etc\gtk-2.0\spellcheck.png"
  File "..\etc\gtk-2.0\stock_dnd.png"
  File "..\etc\gtk-2.0\stock_dnd_multiple.png"
  File "..\etc\gtk-2.0\stop.png"
  File "..\etc\gtk-2.0\undelete.png"
  File "..\etc\gtk-2.0\view-refresh.png"
  File "..\etc\gtk-2.0\yes.png"
  File "..\etc\gtk-2.0\zoom-best-fit.png"
  File "..\etc\gtk-2.0\zoom-in.png"
  File "..\etc\gtk-2.0\zoom-original.png"
  File "..\etc\gtk-2.0\zoom-out.png"
  SetOutPath "$INSTDIR\etc\pango"
  File "..\etc\pango\pango.modules"
  SetOutPath "$INSTDIR\lib"
  File "..\lib\charset.alias"
  SetOutPath "$INSTDIR\lib\gtk-2.0\2.10.0\engines"
  File "..\lib\gtk-2.0\2.10.0\engines\libanachron.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libaurora.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libbluecurve.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libblueprint.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libcandido.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libcleanice.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libclearlooks.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libcrux-engine.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libdyndyn.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libexcelsior.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libgflat.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libglide.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libhcengine.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libindustrial.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\liblighthouseblue.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libmetal.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libmgicchikn.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libmist.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libmurrine.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libnimbus.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libnodoka.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libpixmap.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libredmond95.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\librezlooks.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libsmooth.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libthinice.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libubuntulooks.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libwimp.dll"
  File "..\lib\gtk-2.0\2.10.0\engines\libxfce.dll"
  SetOutPath "$INSTDIR\lib\gtk-2.0\2.10.0\loaders"
  File "..\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-ani.dll"
  File "..\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-bmp.dll"
  File "..\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-gif.dll"
  File "..\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-icns.dll"
  File "..\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-ico.dll"
  File "..\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-jpeg.dll"
  File "..\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-pcx.dll"
  File "..\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-png.dll"
  File "..\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-pnm.dll"
  File "..\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-ras.dll"
  File "..\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-tga.dll"
  File "..\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-tiff.dll"
  File "..\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-wbmp.dll"
  File "..\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-xbm.dll"
  File "..\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-xpm.dll"
  SetOutPath "$INSTDIR\lib\gtk-2.0\modules\modules"
  File "..\lib\gtk-2.0\modules\modules\libgail.dll"
  SetOutPath "$INSTDIR\application\common"
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
  File "..\application\common\scenario_21.xsd"
  File "..\application\common\scenario_22.xsd"
  File "..\application\common\scenario_23.xsd"
  File "..\application\common\scenario_24.xsd"
  File "..\application\common\scenario_25.xsd"
  File "..\application\common\scenario_26.xsd"
  File "..\application\common\scenario_27.xsd"
  File "..\application\common\scenario_28.xsd"
  File "..\application\common\scenario_29.xsd"
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
  CreateDirectory "$SMPROGRAMS\openmalariaTools"
  SetOutPath "$INSTDIR"
  CreateShortCut "$SMPROGRAMS\openmalariaTools\openmalariaTools.lnk" "$INSTDIR\openmalariatools.exe"
  CreateShortCut "$DESKTOP\openmalariaTools.lnk" "$INSTDIR\openmalariatool.exe"
  SetOutPath "$INSTDIR\application\schemaTranslator"
  File "..\application\schemaTranslator\SchemaTranslator.jar"
  SetOutPath "$INSTDIR\"
  SetOverwrite ifnewer
  File "..\unicodedata.pyd"
  File "..\openmalariatools.exe"
  File "..\select.pyd"
  File "..\python26.dll"
  File "..\pyexpat.pyd"
  File "..\pangocairo.pyd"
  File "..\pango.pyd"
  File "..\libpng12-0.dll"
  File "..\libpangowin32-1.0-0.dll"
  File "..\libpangocairo-1.0-0.dll"
  File "..\libpango-1.0-0.dll"
  File "..\libgtk-win32-2.0-0.dll"
  File "..\libgthread-2.0-0.dll"
  File "..\libgobject-2.0-0.dll"
  File "..\libgmodule-2.0-0.dll"
  File "..\libglib-2.0-0.dll"
  File "..\libgio-2.0-0.dll"
  File "..\libgdk-win32-2.0-0.dll"
  File "..\libgdk_pixbuf-2.0-0.dll"
  File "..\libcairo-2.dll"
  File "..\libatk-1.0-0.dll"
  File "..\gtk._gtk.pyd"
  File "..\gobject._gobject.pyd"
  File "..\glib._glib.pyd"
  File "..\gio._gio.pyd"
  File "..\cairo._cairo.pyd"
  File "..\bz2.pyd"
  File "..\atk.pyd"
  File "..\_ssl.pyd"
  File "..\_socket.pyd"
  File "..\_hashlib.pyd"
  File "..\_ctypes.pyd"
  File "..\zlib1.dll"
  CreateDirectory "$INSTDIR\run_scenarios"
  CreateDirectory "$INSTDIR\run_scenarios\outputs"
  CreateDirectory "$INSTDIR\run_scenarios\scenarios_to_run"
  CreateDirectory "$INSTDIR\translate_scenarios"
  CreateDirectory "$INSTDIR\translate_scenarios\scenarios_to_translate"
  CreateDirectory "$INSTDIR\translate_scenarios\translated_scenarios"
SectionEnd

Section -AdditionalIcons
  SetOutPath $INSTDIR
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
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure that you want to uninstall $(^Name) and all its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\zlib1.dll"
  Delete "$INSTDIR\_ctypes.pyd"
  Delete "$INSTDIR\_hashlib.pyd"
  Delete "$INSTDIR\_socket.pyd"
  Delete "$INSTDIR\_ssl.pyd"
  Delete "$INSTDIR\atk.pyd"
  Delete "$INSTDIR\bz2.pyd"
  Delete "$INSTDIR\cairo._cairo.pyd"
  Delete "$INSTDIR\gio._gio.pyd"
  Delete "$INSTDIR\glib._glib.pyd"
  Delete "$INSTDIR\gobject._gobject.pyd"
  Delete "$INSTDIR\gtk._gtk.pyd"
  Delete "$INSTDIR\libatk-1.0-0.dll"
  Delete "$INSTDIR\libcairo-2.dll"
  Delete "$INSTDIR\libgdk_pixbuf-2.0-0.dll"
  Delete "$INSTDIR\libgdk-win32-2.0-0.dll"
  Delete "$INSTDIR\libgio-2.0-0.dll"
  Delete "$INSTDIR\libglib-2.0-0.dll"
  Delete "$INSTDIR\libgmodule-2.0-0.dll"
  Delete "$INSTDIR\libgobject-2.0-0.dll"
  Delete "$INSTDIR\libgthread-2.0-0.dll"
  Delete "$INSTDIR\libgtk-win32-2.0-0.dll"
  Delete "$INSTDIR\libpango-1.0-0.dll"
  Delete "$INSTDIR\libpangocairo-1.0-0.dll"
  Delete "$INSTDIR\libpangowin32-1.0-0.dll"
  Delete "$INSTDIR\libpng12-0.dll"
  Delete "$INSTDIR\pango.pyd"
  Delete "$INSTDIR\pangocairo.pyd"
  Delete "$INSTDIR\pyexpat.pyd"
  Delete "$INSTDIR\python26.dll"
  Delete "$INSTDIR\select.pyd"
  Delete "$INSTDIR\openmalariatools.exe"
  Delete "$INSTDIR\unicodedata.pyd"
  Delete "$INSTDIR\application\schemaTranslator\SchemaTranslator.jar"
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
  Delete "$INSTDIR\application\common\scenario_21.xsd"
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
  Delete "$INSTDIR\lib\gtk-2.0\modules\modules\libgail.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-xpm.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-xbm.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-wbmp.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-tiff.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-tga.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-ras.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-pnm.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-png.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-pcx.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-jpeg.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-ico.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-icns.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-gif.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-bmp.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\loaders\libpixbufloader-ani.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libxfce.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libwimp.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libubuntulooks.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libthinice.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libsmooth.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\librezlooks.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libredmond95.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libpixmap.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libnodoka.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libnimbus.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libmurrine.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libmist.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libmgicchikn.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libmetal.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\liblighthouseblue.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libindustrial.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libhcengine.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libglide.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libgflat.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libexcelsior.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libdyndyn.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libcrux-engine.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libclearlooks.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libcleanice.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libcandido.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libblueprint.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libbluecurve.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libaurora.dll"
  Delete "$INSTDIR\lib\gtk-2.0\2.10.0\engines\libanachron.dll"
  Delete "$INSTDIR\lib\charset.alias"
  Delete "$INSTDIR\etc\pango\pango.modules"
  Delete "$INSTDIR\etc\gtk-2.0\zoom-out.png"
  Delete "$INSTDIR\etc\gtk-2.0\zoom-original.png"
  Delete "$INSTDIR\etc\gtk-2.0\zoom-in.png"
  Delete "$INSTDIR\etc\gtk-2.0\zoom-best-fit.png"
  Delete "$INSTDIR\etc\gtk-2.0\yes.png"
  Delete "$INSTDIR\etc\gtk-2.0\view-refresh.png"
  Delete "$INSTDIR\etc\gtk-2.0\undelete.png"
  Delete "$INSTDIR\etc\gtk-2.0\stop.png"
  Delete "$INSTDIR\etc\gtk-2.0\stock_dnd_multiple.png"
  Delete "$INSTDIR\etc\gtk-2.0\stock_dnd.png"
  Delete "$INSTDIR\etc\gtk-2.0\spellcheck.png"
  Delete "$INSTDIR\etc\gtk-2.0\sort_descending.png"
  Delete "$INSTDIR\etc\gtk-2.0\sort_ascending.png"
  Delete "$INSTDIR\etc\gtk-2.0\revert.png"
  Delete "$INSTDIR\etc\gtk-2.0\remove.png"
  Delete "$INSTDIR\etc\gtk-2.0\quit.png"
  Delete "$INSTDIR\etc\gtk-2.0\preferences.png"
  Delete "$INSTDIR\etc\gtk-2.0\ok.png"
  Delete "$INSTDIR\etc\gtk-2.0\no.png"
  Delete "$INSTDIR\etc\gtk-2.0\network.png"
  Delete "$INSTDIR\etc\gtk-2.0\media-stop.png"
  Delete "$INSTDIR\etc\gtk-2.0\media-rewind.png"
  Delete "$INSTDIR\etc\gtk-2.0\media-record.png"
  Delete "$INSTDIR\etc\gtk-2.0\media-prev.png"
  Delete "$INSTDIR\etc\gtk-2.0\media-play.png"
  Delete "$INSTDIR\etc\gtk-2.0\media-pause.png"
  Delete "$INSTDIR\etc\gtk-2.0\media-next.png"
  Delete "$INSTDIR\etc\gtk-2.0\media-ffwd.png"
  Delete "$INSTDIR\etc\gtk-2.0\leave_fullscreen.png"
  Delete "$INSTDIR\etc\gtk-2.0\info.png"
  Delete "$INSTDIR\etc\gtk-2.0\index.png"
  Delete "$INSTDIR\etc\gtk-2.0\im-multipress.conf"
  Delete "$INSTDIR\etc\gtk-2.0\iconrc.in"
  Delete "$INSTDIR\etc\gtk-2.0\iconrc"
  Delete "$INSTDIR\etc\gtk-2.0\help.png"
  Delete "$INSTDIR\etc\gtk-2.0\harddisk.png"
  Delete "$INSTDIR\etc\gtk-2.0\gtkrc.default"
  Delete "$INSTDIR\etc\gtk-2.0\gtkrc"
  Delete "$INSTDIR\etc\gtk-2.0\gtk.immodules"
  Delete "$INSTDIR\etc\gtk-2.0\go-up.png"
  Delete "$INSTDIR\etc\gtk-2.0\go-top.png"
  Delete "$INSTDIR\etc\gtk-2.0\go-previous.png"
  Delete "$INSTDIR\etc\gtk-2.0\go-next.png"
  Delete "$INSTDIR\etc\gtk-2.0\go-last.png"
  Delete "$INSTDIR\etc\gtk-2.0\go-jump.png"
  Delete "$INSTDIR\etc\gtk-2.0\go-home.png"
  Delete "$INSTDIR\etc\gtk-2.0\go-first.png"
  Delete "$INSTDIR\etc\gtk-2.0\go-down.png"
  Delete "$INSTDIR\etc\gtk-2.0\go-bottom.png"
  Delete "$INSTDIR\etc\gtk-2.0\gdk-pixbuf.loaders"
  Delete "$INSTDIR\etc\gtk-2.0\fullscreen.png"
  Delete "$INSTDIR\etc\gtk-2.0\format-text-underline.png"
  Delete "$INSTDIR\etc\gtk-2.0\format-text-strikethrough.png"
  Delete "$INSTDIR\etc\gtk-2.0\format-text-italic.png"
  Delete "$INSTDIR\etc\gtk-2.0\format-text-bold.png"
  Delete "$INSTDIR\etc\gtk-2.0\format-justify-right.png"
  Delete "$INSTDIR\etc\gtk-2.0\format-justify-left.png"
  Delete "$INSTDIR\etc\gtk-2.0\format-justify-fill.png"
  Delete "$INSTDIR\etc\gtk-2.0\format-justify-center.png"
  Delete "$INSTDIR\etc\gtk-2.0\format-indent-more.png"
  Delete "$INSTDIR\etc\gtk-2.0\format-indent-less.png"
  Delete "$INSTDIR\etc\gtk-2.0\font.png"
  Delete "$INSTDIR\etc\gtk-2.0\floppy.png"
  Delete "$INSTDIR\etc\gtk-2.0\file.png"
  Delete "$INSTDIR\etc\gtk-2.0\execute.png"
  Delete "$INSTDIR\etc\gtk-2.0\edit.png"
  Delete "$INSTDIR\etc\gtk-2.0\edit-undo.png"
  Delete "$INSTDIR\etc\gtk-2.0\edit-redo.png"
  Delete "$INSTDIR\etc\gtk-2.0\edit-paste.png"
  Delete "$INSTDIR\etc\gtk-2.0\edit-find.png"
  Delete "$INSTDIR\etc\gtk-2.0\edit-find-replace.png"
  Delete "$INSTDIR\etc\gtk-2.0\edit-cut_24.png"
  Delete "$INSTDIR\etc\gtk-2.0\edit-cut_16.png"
  Delete "$INSTDIR\etc\gtk-2.0\edit-copy_24.png"
  Delete "$INSTDIR\etc\gtk-2.0\edit-copy_16.png"
  Delete "$INSTDIR\etc\gtk-2.0\document-save.png"
  Delete "$INSTDIR\etc\gtk-2.0\document-save-as.png"
  Delete "$INSTDIR\etc\gtk-2.0\document-properties.png"
  Delete "$INSTDIR\etc\gtk-2.0\document-print.png"
  Delete "$INSTDIR\etc\gtk-2.0\document-print-preview.png"
  Delete "$INSTDIR\etc\gtk-2.0\document-open.png"
  Delete "$INSTDIR\etc\gtk-2.0\document-new.png"
  Delete "$INSTDIR\etc\gtk-2.0\disconnect.png"
  Delete "$INSTDIR\etc\gtk-2.0\directory.png"
  Delete "$INSTDIR\etc\gtk-2.0\dialog_warning.png"
  Delete "$INSTDIR\etc\gtk-2.0\dialog_question.png"
  Delete "$INSTDIR\etc\gtk-2.0\dialog_info.png"
  Delete "$INSTDIR\etc\gtk-2.0\dialog_error.png"
  Delete "$INSTDIR\etc\gtk-2.0\dialog_authentication.png"
  Delete "$INSTDIR\etc\gtk-2.0\delete_24.png"
  Delete "$INSTDIR\etc\gtk-2.0\delete_16.png"
  Delete "$INSTDIR\etc\gtk-2.0\convert.png"
  Delete "$INSTDIR\etc\gtk-2.0\connect.png"
  Delete "$INSTDIR\etc\gtk-2.0\colorselector.png"
  Delete "$INSTDIR\etc\gtk-2.0\close.png"
  Delete "$INSTDIR\etc\gtk-2.0\clear.png"
  Delete "$INSTDIR\etc\gtk-2.0\cdrom_24.png"
  Delete "$INSTDIR\etc\gtk-2.0\cdrom_16.png"
  Delete "$INSTDIR\etc\gtk-2.0\cancel.png"
  Delete "$INSTDIR\etc\gtk-2.0\broken_image.png"
  Delete "$INSTDIR\etc\gtk-2.0\apply.png"
  Delete "$INSTDIR\etc\gtk-2.0\add.png"
  Delete "$INSTDIR\etc\gtk-2.0\about.png"
  Delete "$INSTDIR\etc\fonts\fonts.dtd"
  Delete "$INSTDIR\etc\fonts\fonts.conf"
  Delete "$INSTDIR\examples\scenario9.xml"
  Delete "$INSTDIR\examples\scenario6.xml"
  Delete "$INSTDIR\examples\scenario5.xml"
  Delete "$INSTDIR\examples\scenario4.xml"
  Delete "$INSTDIR\examples\scenario3.xml"
  Delete "$INSTDIR\examples\scenario2.xml"
  Delete "$INSTDIR\examples\scenario12.xml"
  Delete "$INSTDIR\examples\scenario11.xml"
  Delete "$INSTDIR\examples\scenario10.xml"
  Delete "$INSTDIR\examples\scenario1.xml"
  Delete "$INSTDIR\openMalariaTools\__init__.pyc"
  Delete "$INSTDIR\openMalariaTools\__init__.py"
  Delete "$INSTDIR\openMalariaTools\utils\__init__.pyc"
  Delete "$INSTDIR\openMalariaTools\utils\__init__.py"
  Delete "$INSTDIR\openMalariaTools\utils\PositionContainer.pyc"
  Delete "$INSTDIR\openMalariaTools\utils\PositionContainer.py"
  Delete "$INSTDIR\openMalariaTools\utils\PathsAndSchema.pyc"
  Delete "$INSTDIR\openMalariaTools\utils\PathsAndSchema.py"
  Delete "$INSTDIR\openMalariaTools\tools_management\__init__.pyc"
  Delete "$INSTDIR\openMalariaTools\tools_management\__init__.py"
  Delete "$INSTDIR\openMalariaTools\tools_management\OpenMalariaRun.pyc"
  Delete "$INSTDIR\openMalariaTools\tools_management\OpenMalariaRun.py"
  Delete "$INSTDIR\openMalariaTools\tools_management\JavaAppsRun.pyc"
  Delete "$INSTDIR\openMalariaTools\tools_management\JavaAppsRun.py"
  Delete "$INSTDIR\openMalariaTools\gui\__init__.pyc"
  Delete "$INSTDIR\openMalariaTools\gui\__init__.py"
  Delete "$INSTDIR\openMalariaTools\gui\VirtualTerminal_win.pyc"
  Delete "$INSTDIR\openMalariaTools\gui\VirtualTerminal_win.py"
  Delete "$INSTDIR\openMalariaTools\gui\ScenariosChoiceDialog.pyc"
  Delete "$INSTDIR\openMalariaTools\gui\ScenariosChoiceDialog.py"
  Delete "$INSTDIR\openMalariaTools\gui\NotebookFrame.pyc"
  Delete "$INSTDIR\openMalariaTools\gui\NotebookFrame.py"
  Delete "$INSTDIR\openMalariaTools\gui\FileViewersContainerDialog.pyc"
  Delete "$INSTDIR\openMalariaTools\gui\FileViewersContainerDialog.py"
  Delete "$INSTDIR\openMalariaTools\gui\FileViewerFrame.pyc"
  Delete "$INSTDIR\openMalariaTools\gui\FileViewerFrame.py"
  Delete "$INSTDIR\openMalariaTools\gui\FileListFrame.pyc"
  Delete "$INSTDIR\openMalariaTools\gui\FileListFrame.py"
  Delete "$INSTDIR\openMalariaTools\gui\ExperimentCreatorDialog.pyc"
  Delete "$INSTDIR\openMalariaTools\gui\ExperimentCreatorDialog.py"
  Delete "$INSTDIR\openMalariaTools\gui\CustomMessageDialogs.pyc"
  Delete "$INSTDIR\openMalariaTools\gui\CustomMessageDialogs.py"
  Delete "$INSTDIR\openMalariaTools\gui\ActualScenariosFoldersFrame.pyc"
  Delete "$INSTDIR\openMalariaTools\gui\ActualScenariosFoldersFrame.py"

  Delete "$SMPROGRAMS\openmalariaTools\Uninstall.lnk"
  Delete "$SMPROGRAMS\openmalariaTools\Website.lnk"
  Delete "$DESKTOP\openmalariaTools.lnk"
  Delete "$SMPROGRAMS\openmalariaTools\openmalariaTools.lnk"

  RMDir "$SMPROGRAMS\openmalariaTools"
  RMDir "$INSTDIR\openMalariaTools\utils"
  RMDir "$INSTDIR\openMalariaTools\tools_management"
  RMDir "$INSTDIR\openMalariaTools\gui"
  RMDir "$INSTDIR\openMalariaTools"
  RMDir "$INSTDIR\lib\gtk-2.0\modules\modules"
  RMDir "$INSTDIR\lib\gtk-2.0\2.10.0\loaders"
  RMDir "$INSTDIR\lib\gtk-2.0\2.10.0\engines"
  RMDir "$INSTDIR\lib"
  RMDir "$INSTDIR\examples"
  RMDir "$INSTDIR\etc\pango"
  RMDir "$INSTDIR\etc\gtk-2.0"
  RMDir "$INSTDIR\etc\fonts"
  RMDir "$INSTDIR\application\schemaTranslator"
  RMDir "$INSTDIR\application\LiveGraph.2.0.beta01.Complete\Examples"
  RMDir "$INSTDIR\application\LiveGraph.2.0.beta01.Complete"
  RMDir "$INSTDIR\application\LiveGraph.1.14.Complete\Examples"
  RMDir "$INSTDIR\application\LiveGraph.1.14.Complete"
  RMDir "$INSTDIR\application\experiment_creator"
  RMDir "$INSTDIR\application\common"
  RMDir "$INSTDIR\application"
  RMDir "$INSTDIR\"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd
# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-11d0e73)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.richtext

###########################################################################
## Class main
###########################################################################

class main ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Dumpit", pos = wx.DefaultPosition, size = wx.Size( 1100,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.HORIZONTAL )

		self.status = wx.richtext.RichTextCtrl( self, wx.ID_ANY, u"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean ac libero vel massa tristique ullamcorper ac et quam. Nunc ultricies dui nibh, ac auctor augue pulvinar sit amet. Nulla malesuada, arcu eu aliquet semper, leo est tincidunt ante, id aliquet tortor leo vel ex. Suspendisse orci lorem, molestie in auctor in, lacinia a felis. Nam molestie sagittis rutrum. Pellentesque tellus mi, posuere sed bibendum quis, laoreet a dui. In vehicula feugiat est, sit amet pellentesque neque porta sit amet. Nam in elit malesuada, imperdiet dolor eu, maximus elit.\n\nDuis tincidunt ante at massa ornare, in vehicula dolor bibendum. Integer eu est interdum, malesuada ex id, rhoncus lectus. Nullam elementum orci in tellus vestibulum porttitor. Etiam vel lectus aliquet, iaculis erat ac, convallis tortor. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Sed bibendum ultrices tempus. Cras diam felis, sodales a lacinia non, rutrum sit amet nisl. Cras dapibus, ex vitae fringilla convallis, mi lacus faucibus lorem, a aliquam ligula orci in quam. Fusce eu erat maximus, volutpat mauris quis, egestas dolor.\n\nPellentesque elementum ultrices dignissim. Integer bibendum elementum auctor. Nulla facilisi. Integer tristique bibendum facilisis. Morbi id risus molestie, tempor diam non, dignissim mauris. In sit amet orci id tellus fringilla cursus. Nam rhoncus lectus a nibh congue, at fermentum elit accumsan. Proin congue nunc velit, at tempor arcu vulputate vitae. Aenean ac diam quis neque gravida ullamcorper. Pellentesque ac erat ex.\n\nMauris lectus risus, consequat quis eros vitae, feugiat fermentum purus. Aenean risus ipsum, dignissim quis consectetur hendrerit, ultrices sed velit. Duis maximus massa tellus, at blandit elit fringilla nec. Ut luctus facilisis mi, non vehicula lorem sagittis vel. Morbi gravida lacus eu sapien condimentum gravida. Vestibulum consectetur auctor est ac efficitur. Aliquam aliquam commodo nibh. Proin ultricies porttitor arcu id accumsan. Maecenas quam eros, egestas vitae fermentum laoreet, efficitur at lacus.\n\nCurabitur id erat eu sapien volutpat ullamcorper. Nulla volutpat dignissim varius. Duis vulputate imperdiet tincidunt. Aenean in leo feugiat, rhoncus erat quis, sollicitudin sapien. Vivamus imperdiet turpis sit amet velit tristique, in dictum dolor pharetra. Duis efficitur magna nec hendrerit congue. In vel luctus purus. ", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
		self.status.SetMinSize( wx.Size( 320,-1 ) )

		bSizer1.Add( self.status, 0, wx.ALL|wx.EXPAND, 5 )

		bSizer3 = wx.BoxSizer( wx.VERTICAL )

		self.tab = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.dPage1 = wx.Panel( self.tab, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer5 = wx.BoxSizer( wx.VERTICAL )

		bSizer6 = wx.BoxSizer( wx.HORIZONTAL )

		self.lInterface = wx.StaticText( self.dPage1, wx.ID_ANY, u"Interface:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lInterface.Wrap( -1 )

		bSizer6.Add( self.lInterface, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		cInterfaceChoices = []
		self.cInterface = wx.Choice( self.dPage1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cInterfaceChoices, 0 )
		self.cInterface.SetSelection( 0 )
		bSizer6.Add( self.cInterface, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.lSpeed = wx.StaticText( self.dPage1, wx.ID_ANY, u"Speed:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lSpeed.Wrap( -1 )

		bSizer6.Add( self.lSpeed, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.nSpeed = wx.SpinCtrl( self.dPage1, wx.ID_ANY, u"1000", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS|wx.TE_PROCESS_ENTER, 0, 30000, 1000 )
		bSizer6.Add( self.nSpeed, 1, wx.ALL, 5 )

		self.bConfigureRead = wx.Button( self.dPage1, wx.ID_ANY, u"Target Read Settings", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6.Add( self.bConfigureRead, 0, wx.ALL, 5 )


		bSizer5.Add( bSizer6, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )

		bSizer61 = wx.BoxSizer( wx.HORIZONTAL )

		self.lChipset = wx.StaticText( self.dPage1, wx.ID_ANY, u"Chipset:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lChipset.Wrap( -1 )

		bSizer61.Add( self.lChipset, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		cChipsetChoices = []
		self.cChipset = wx.Choice( self.dPage1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cChipsetChoices, 0 )
		self.cChipset.SetSelection( 0 )
		self.cChipset.SetMaxSize( wx.Size( 150,-1 ) )

		bSizer61.Add( self.cChipset, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

		self.lTarget = wx.StaticText( self.dPage1, wx.ID_ANY, u"Target:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lTarget.Wrap( -1 )

		bSizer61.Add( self.lTarget, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		cTargetChoices = []
		self.cTarget = wx.Choice( self.dPage1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cTargetChoices, 0 )
		self.cTarget.SetSelection( 0 )
		bSizer61.Add( self.cTarget, 0, wx.ALL, 5 )

		self.lTap = wx.StaticText( self.dPage1, wx.ID_ANY, u"TAP:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lTap.Wrap( -1 )

		bSizer61.Add( self.lTap, 0, wx.ALL, 5 )

		cTapChoices = [ u"0", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9" ]
		self.cTap = wx.Choice( self.dPage1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cTapChoices, 0 )
		self.cTap.SetSelection( 0 )
		self.cTap.Enable( False )
		self.cTap.SetMinSize( wx.Size( 100,-1 ) )

		bSizer61.Add( self.cTap, 0, wx.ALL, 5 )

		self.lIR = wx.StaticText( self.dPage1, wx.ID_ANY, u"IR:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lIR.Wrap( -1 )

		bSizer61.Add( self.lIR, 0, wx.ALL, 5 )

		self.nIR = wx.SpinCtrl( self.dPage1, wx.ID_ANY, u"4", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 64, 0 )
		self.nIR.SetMinSize( wx.Size( 150,-1 ) )

		bSizer61.Add( self.nIR, 0, wx.ALL, 5 )


		bSizer5.Add( bSizer61, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )

		bSizer611 = wx.BoxSizer( wx.HORIZONTAL )

		self.lResetMode = wx.StaticText( self.dPage1, wx.ID_ANY, u"Reset Mode:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lResetMode.Wrap( -1 )

		bSizer611.Add( self.lResetMode, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		cResetModeChoices = []
		self.cResetMode = wx.Choice( self.dPage1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cResetModeChoices, 0 )
		self.cResetMode.SetSelection( 0 )
		bSizer611.Add( self.cResetMode, 1, wx.ALL, 5 )

		self.lResetDelay = wx.StaticText( self.dPage1, wx.ID_ANY, u"Reset Delay:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lResetDelay.Wrap( -1 )

		bSizer611.Add( self.lResetDelay, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.bResetDelay = wx.Button( self.dPage1, wx.ID_ANY, u"Configure", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer611.Add( self.bResetDelay, 0, wx.ALL, 5 )

		self.bSkipInit = wx.CheckBox( self.dPage1, wx.ID_ANY, u"Skip Initialization", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer611.Add( self.bSkipInit, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer5.Add( bSizer611, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5 )

		bSizer6111 = wx.BoxSizer( wx.HORIZONTAL )

		self.lStart = wx.StaticText( self.dPage1, wx.ID_ANY, u"Start:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lStart.Wrap( -1 )

		bSizer6111.Add( self.lStart, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.tStart = wx.TextCtrl( self.dPage1, wx.ID_ANY, u"00000000", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6111.Add( self.tStart, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

		self.lEnd = wx.StaticText( self.dPage1, wx.ID_ANY, u"End:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lEnd.Wrap( -1 )

		bSizer6111.Add( self.lEnd, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.tEnd = wx.TextCtrl( self.dPage1, wx.ID_ANY, u"02000000", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6111.Add( self.tEnd, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

		self.lNandSize = wx.StaticText( self.dPage1, wx.ID_ANY, u"Page Size:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lNandSize.Wrap( -1 )

		bSizer6111.Add( self.lNandSize, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		cNandSizeChoices = [ u"512/2K (O1N)", u"2K/4K (O1N)", u"Auto" ]
		self.cNandSize = wx.Choice( self.dPage1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cNandSizeChoices, 0 )
		self.cNandSize.SetSelection( 2 )
		bSizer6111.Add( self.cNandSize, 1, wx.ALL, 5 )

		self.bECCDisable = wx.CheckBox( self.dPage1, wx.ID_ANY, u"Disable ECC", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6111.Add( self.bECCDisable, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.bBadBlockinData = wx.CheckBox( self.dPage1, wx.ID_ANY, u"Bad Blocks on Data", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6111.Add( self.bBadBlockinData, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer5.Add( bSizer6111, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5 )

		bSizer611112 = wx.BoxSizer( wx.HORIZONTAL )

		self.bConnect = wx.Button( self.dPage1, wx.ID_ANY, u"Connect", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer611112.Add( self.bConnect, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.bConnectRemote = wx.Button( self.dPage1, wx.ID_ANY, u"Connect to Remote", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer611112.Add( self.bConnectRemote, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.bForwardRemote = wx.Button( self.dPage1, wx.ID_ANY, u"Forward to Remote", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer611112.Add( self.bForwardRemote, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.bReconnectRemote = wx.Button( self.dPage1, wx.ID_ANY, u"Reconnect to Remote", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer611112.Add( self.bReconnectRemote, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer5.Add( bSizer611112, 0, wx.ALIGN_CENTER_HORIZONTAL, 5 )

		bSizer6111121 = wx.BoxSizer( wx.HORIZONTAL )

		self.lTargetRemote = wx.StaticText( self.dPage1, wx.ID_ANY, u"Address:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lTargetRemote.Wrap( -1 )

		bSizer6111121.Add( self.lTargetRemote, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.bTargetRemote = wx.TextCtrl( self.dPage1, wx.ID_ANY, u"dumpit.ucomsite.my.id", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6111121.Add( self.bTargetRemote, 1, wx.ALL, 5 )

		self.bUseGDB = wx.CheckBox( self.dPage1, wx.ID_ANY, u"Use GDB", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.bUseGDB.Enable( False )

		bSizer6111121.Add( self.bUseGDB, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer5.Add( bSizer6111121, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5 )

		bSizer61111 = wx.BoxSizer( wx.HORIZONTAL )

		self.bDumpFlash = wx.Button( self.dPage1, wx.ID_ANY, u"Dump Flash", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer61111.Add( self.bDumpFlash, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.bDumpMemory = wx.Button( self.dPage1, wx.ID_ANY, u"Dump Memory", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer61111.Add( self.bDumpMemory, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.bStop = wx.Button( self.dPage1, wx.ID_ANY, u"Stop", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.bStop.Enable( False )

		bSizer61111.Add( self.bStop, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.bNandConfigure = wx.Button( self.dPage1, wx.ID_ANY, u"Configure NAND Controller", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer61111.Add( self.bNandConfigure, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.bEditMetadata = wx.Button( self.dPage1, wx.ID_ANY, u"Edit Metadata", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer61111.Add( self.bEditMetadata, 0, wx.ALL, 5 )


		bSizer5.Add( bSizer61111, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5 )

		bSizer611111 = wx.BoxSizer( wx.HORIZONTAL )

		self.bGo = wx.Button( self.dPage1, wx.ID_ANY, u"Go", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer611111.Add( self.bGo, 0, wx.ALL, 5 )

		self.bHalt = wx.Button( self.dPage1, wx.ID_ANY, u"Halt", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer611111.Add( self.bHalt, 0, wx.ALL, 5 )

		self.bReset = wx.Button( self.dPage1, wx.ID_ANY, u"Reset", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer611111.Add( self.bReset, 0, wx.ALL, 5 )

		self.bHardReset = wx.Button( self.dPage1, wx.ID_ANY, u"Hard Reset", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer611111.Add( self.bHardReset, 0, wx.ALL, 5 )

		self.bExecScript = wx.Button( self.dPage1, wx.ID_ANY, u"Execute Script", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer611111.Add( self.bExecScript, 1, wx.ALL, 5 )

		self.bExecLoader = wx.Button( self.dPage1, wx.ID_ANY, u"Load DCC", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer611111.Add( self.bExecLoader, 1, wx.ALL, 5 )


		bSizer5.Add( bSizer611111, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5 )

		bSizer6111111 = wx.BoxSizer( wx.HORIZONTAL )

		self.bEnableMMU = wx.Button( self.dPage1, wx.ID_ANY, u"Enable MMU", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6111111.Add( self.bEnableMMU, 1, wx.ALL, 5 )

		self.bDisableMMU = wx.Button( self.dPage1, wx.ID_ANY, u"Disable MMU", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6111111.Add( self.bDisableMMU, 1, wx.ALL, 5 )

		self.bExec = wx.Button( self.dPage1, wx.ID_ANY, u"Execute Address", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6111111.Add( self.bExec, 1, wx.ALL, 5 )


		bSizer5.Add( bSizer6111111, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )

		bSizer61111111 = wx.BoxSizer( wx.VERTICAL )

		self.sInfo = wx.richtext.RichTextCtrl( self.dPage1, wx.ID_ANY, u"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean ac libero vel massa tristique ullamcorper ac et quam. Nunc ultricies dui nibh, ac auctor augue pulvinar sit amet. Nulla malesuada, arcu eu aliquet semper, leo est tincidunt ante, id aliquet tortor leo vel ex. Suspendisse orci lorem, molestie in auctor in, lacinia a felis. Nam molestie sagittis rutrum. Pellentesque tellus mi, posuere sed bibendum quis, laoreet a dui. In vehicula feugiat est, sit amet pellentesque neque porta sit amet. Nam in elit malesuada, imperdiet dolor eu, maximus elit.\n\nDuis tincidunt ante at massa ornare, in vehicula dolor bibendum. Integer eu est interdum, malesuada ex id, rhoncus lectus. Nullam elementum orci in tellus vestibulum porttitor. Etiam vel lectus aliquet, iaculis erat ac, convallis tortor. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Sed bibendum ultrices tempus. Cras diam felis, sodales a lacinia non, rutrum sit amet nisl. Cras dapibus, ex vitae fringilla convallis, mi lacus faucibus lorem, a aliquam ligula orci in quam. Fusce eu erat maximus, volutpat mauris quis, egestas dolor.\n\nPellentesque elementum ultrices dignissim. Integer bibendum elementum auctor. Nulla facilisi. Integer tristique bibendum facilisis. Morbi id risus molestie, tempor diam non, dignissim mauris. In sit amet orci id tellus fringilla cursus. Nam rhoncus lectus a nibh congue, at fermentum elit accumsan. Proin congue nunc velit, at tempor arcu vulputate vitae. Aenean ac diam quis neque gravida ullamcorper. Pellentesque ac erat ex.\n\nMauris lectus risus, consequat quis eros vitae, feugiat fermentum purus. Aenean risus ipsum, dignissim quis consectetur hendrerit, ultrices sed velit. Duis maximus massa tellus, at blandit elit fringilla nec. Ut luctus facilisis mi, non vehicula lorem sagittis vel. Morbi gravida lacus eu sapien condimentum gravida. Vestibulum consectetur auctor est ac efficitur. Aliquam aliquam commodo nibh. Proin ultricies porttitor arcu id accumsan. Maecenas quam eros, egestas vitae fermentum laoreet, efficitur at lacus.\n\nCurabitur id erat eu sapien volutpat ullamcorper. Nulla volutpat dignissim varius. Duis vulputate imperdiet tincidunt. Aenean in leo feugiat, rhoncus erat quis, sollicitudin sapien. Vivamus imperdiet turpis sit amet velit tristique, in dictum dolor pharetra. Duis efficitur magna nec hendrerit congue. In vel luctus purus. ", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
		bSizer61111111.Add( self.sInfo, 1, wx.EXPAND |wx.ALL, 5 )

		self.lCurrentDCC = wx.StaticText( self.dPage1, wx.ID_ANY, u"DCC Loader: None", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lCurrentDCC.Wrap( -1 )

		bSizer61111111.Add( self.lCurrentDCC, 0, wx.ALL, 5 )


		bSizer5.Add( bSizer61111111, 1, wx.EXPAND, 5 )

		bSizer60 = wx.BoxSizer( wx.VERTICAL )

		self.tOCDCmd = wx.TextCtrl( self.dPage1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		bSizer60.Add( self.tOCDCmd, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer5.Add( bSizer60, 0, wx.EXPAND, 5 )


		self.dPage1.SetSizer( bSizer5 )
		self.dPage1.Layout()
		bSizer5.Fit( self.dPage1 )
		self.tab.AddPage( self.dPage1, u"Dump", True )
		self.dPage2 = wx.Panel( self.tab, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer8 = wx.BoxSizer( wx.VERTICAL )

		self.pSettingsNull = wx.Panel( self.dPage2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer9 = wx.BoxSizer( wx.VERTICAL )

		self.lNothing = wx.StaticText( self.pSettingsNull, wx.ID_ANY, u"Nothing to see here.", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lNothing.Wrap( -1 )

		bSizer9.Add( self.lNothing, 0, wx.ALL, 5 )


		self.pSettingsNull.SetSizer( bSizer9 )
		self.pSettingsNull.Layout()
		bSizer9.Fit( self.pSettingsNull )
		bSizer8.Add( self.pSettingsNull, 1, wx.EXPAND|wx.ALL, 5 )

		self.pSettingsFT232R = wx.Panel( self.dPage2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.pSettingsFT232R.Hide()

		bSizer91 = wx.BoxSizer( wx.VERTICAL )

		bSizer15 = wx.BoxSizer( wx.HORIZONTAL )

		self.lUSBID = wx.StaticText( self.pSettingsFT232R, wx.ID_ANY, u"USB ID:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lUSBID.Wrap( -1 )

		bSizer15.Add( self.lUSBID, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.tUSBID = wx.TextCtrl( self.pSettingsFT232R, wx.ID_ANY, u"0x0403:0x6001", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer15.Add( self.tUSBID, 1, wx.ALL, 5 )


		bSizer91.Add( bSizer15, 0, wx.EXPAND, 5 )

		bSizer151 = wx.BoxSizer( wx.HORIZONTAL )

		self.lRestoreSerial = wx.StaticText( self.pSettingsFT232R, wx.ID_ANY, u"Restore Serial Code:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lRestoreSerial.Wrap( -1 )

		bSizer151.Add( self.lRestoreSerial, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.tRestoreSerial = wx.TextCtrl( self.pSettingsFT232R, wx.ID_ANY, u"0xffff", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer151.Add( self.tRestoreSerial, 1, wx.ALL, 5 )


		bSizer91.Add( bSizer151, 0, wx.EXPAND, 5 )

		bSizer1512 = wx.BoxSizer( wx.HORIZONTAL )

		self.bConfigureLayoutFT232R = wx.Button( self.pSettingsFT232R, wx.ID_ANY, u"Configure Layout", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer1512.Add( self.bConfigureLayoutFT232R, 1, wx.ALL, 5 )


		bSizer91.Add( bSizer1512, 1, wx.EXPAND, 5 )


		self.pSettingsFT232R.SetSizer( bSizer91 )
		self.pSettingsFT232R.Layout()
		bSizer91.Fit( self.pSettingsFT232R )
		bSizer8.Add( self.pSettingsFT232R, 1, wx.EXPAND |wx.ALL, 5 )

		self.pSettingsGPIOD = wx.Panel( self.dPage2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.pSettingsGPIOD.Hide()

		bSizer912 = wx.BoxSizer( wx.VERTICAL )

		bSizer151222 = wx.BoxSizer( wx.HORIZONTAL )

		self.lGPIODChip = wx.StaticText( self.pSettingsGPIOD, wx.ID_ANY, u"Chip:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lGPIODChip.Wrap( -1 )

		bSizer151222.Add( self.lGPIODChip, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.nGPIODChip = wx.SpinCtrl( self.pSettingsGPIOD, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 100, 0 )
		self.nGPIODChip.SetMinSize( wx.Size( 200,-1 ) )

		bSizer151222.Add( self.nGPIODChip, 0, wx.ALL, 5 )


		bSizer912.Add( bSizer151222, 0, wx.EXPAND, 5 )

		bSizer15122 = wx.BoxSizer( wx.HORIZONTAL )

		self.bConfigureLayoutGPIOD = wx.Button( self.pSettingsGPIOD, wx.ID_ANY, u"Configure Layout", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer15122.Add( self.bConfigureLayoutGPIOD, 1, wx.ALL, 5 )


		bSizer912.Add( bSizer15122, 0, wx.EXPAND, 5 )


		self.pSettingsGPIOD.SetSizer( bSizer912 )
		self.pSettingsGPIOD.Layout()
		bSizer912.Fit( self.pSettingsGPIOD )
		bSizer8.Add( self.pSettingsGPIOD, 1, wx.EXPAND |wx.ALL, 5 )

		self.pSettingsParPort = wx.Panel( self.dPage2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.pSettingsParPort.Hide()

		bSizer9121 = wx.BoxSizer( wx.VERTICAL )

		bSizer1531 = wx.BoxSizer( wx.HORIZONTAL )

		self.lParCable = wx.StaticText( self.pSettingsParPort, wx.ID_ANY, u"Cable:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lParCable.Wrap( -1 )

		bSizer1531.Add( self.lParCable, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		cParCableChoices = [ u"DLC5", u"Wiggler" ]
		self.cParCable = wx.Choice( self.pSettingsParPort, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cParCableChoices, 0 )
		self.cParCable.SetSelection( 0 )
		bSizer1531.Add( self.cParCable, 1, wx.ALL, 5 )


		bSizer9121.Add( bSizer1531, 0, wx.EXPAND, 5 )

		bSizer15131 = wx.BoxSizer( wx.HORIZONTAL )

		self.lParPort = wx.StaticText( self.pSettingsParPort, wx.ID_ANY, u"Port:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lParPort.Wrap( -1 )

		bSizer15131.Add( self.lParPort, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.tParPort = wx.TextCtrl( self.pSettingsParPort, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer15131.Add( self.tParPort, 1, wx.ALL, 5 )


		bSizer9121.Add( bSizer15131, 0, wx.EXPAND, 5 )


		self.pSettingsParPort.SetSizer( bSizer9121 )
		self.pSettingsParPort.Layout()
		bSizer9121.Fit( self.pSettingsParPort )
		bSizer8.Add( self.pSettingsParPort, 1, wx.EXPAND |wx.ALL, 5 )

		self.pSettingsRemoteBitbang = wx.Panel( self.dPage2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.pSettingsRemoteBitbang.Hide()

		bSizer91211 = wx.BoxSizer( wx.VERTICAL )

		bSizer15311 = wx.BoxSizer( wx.HORIZONTAL )

		self.lRBBHost = wx.StaticText( self.pSettingsRemoteBitbang, wx.ID_ANY, u"Host:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lRBBHost.Wrap( -1 )

		bSizer15311.Add( self.lRBBHost, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.tRBBHost = wx.TextCtrl( self.pSettingsRemoteBitbang, wx.ID_ANY, u"127.0.0.1", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer15311.Add( self.tRBBHost, 1, wx.ALL, 5 )


		bSizer91211.Add( bSizer15311, 0, wx.EXPAND, 5 )

		bSizer151311 = wx.BoxSizer( wx.HORIZONTAL )

		self.lRBBPort = wx.StaticText( self.pSettingsRemoteBitbang, wx.ID_ANY, u"Port:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lRBBPort.Wrap( -1 )

		bSizer151311.Add( self.lRBBPort, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.tRBBPort = wx.TextCtrl( self.pSettingsRemoteBitbang, wx.ID_ANY, u"3463", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer151311.Add( self.tRBBPort, 1, wx.ALL, 5 )


		bSizer91211.Add( bSizer151311, 0, wx.EXPAND, 5 )


		self.pSettingsRemoteBitbang.SetSizer( bSizer91211 )
		self.pSettingsRemoteBitbang.Layout()
		bSizer91211.Fit( self.pSettingsRemoteBitbang )
		bSizer8.Add( self.pSettingsRemoteBitbang, 1, wx.EXPAND |wx.ALL, 5 )

		self.pSettingsFT232H = wx.Panel( self.dPage2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.pSettingsFT232H.Hide()

		bSizer911 = wx.BoxSizer( wx.VERTICAL )

		bSizer1521 = wx.BoxSizer( wx.HORIZONTAL )

		self.lFTAdapter = wx.StaticText( self.pSettingsFT232H, wx.ID_ANY, u"Adapter:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lFTAdapter.Wrap( -1 )

		bSizer1521.Add( self.lFTAdapter, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		cFTAdapterChoices = []
		self.cFTAdapter = wx.Choice( self.pSettingsFT232H, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cFTAdapterChoices, 0 )
		self.cFTAdapter.SetSelection( 0 )
		bSizer1521.Add( self.cFTAdapter, 0, wx.ALL, 5 )


		bSizer911.Add( bSizer1521, 0, wx.EXPAND, 5 )

		bSizer152 = wx.BoxSizer( wx.HORIZONTAL )

		self.lUSBID1 = wx.StaticText( self.pSettingsFT232H, wx.ID_ANY, u"USB ID:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lUSBID1.Wrap( -1 )

		bSizer152.Add( self.lUSBID1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.tUSBID1 = wx.TextCtrl( self.pSettingsFT232H, wx.ID_ANY, u"0x0403:0x6014", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer152.Add( self.tUSBID1, 1, wx.ALL, 5 )


		bSizer911.Add( bSizer152, 0, wx.EXPAND, 5 )

		bSizer1511 = wx.BoxSizer( wx.HORIZONTAL )

		self.lChannel = wx.StaticText( self.pSettingsFT232H, wx.ID_ANY, u"Channel:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lChannel.Wrap( -1 )

		bSizer1511.Add( self.lChannel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		cChannelChoices = [ u"0", u"1", u"2", u"3" ]
		self.cChannel = wx.Choice( self.pSettingsFT232H, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cChannelChoices, 0 )
		self.cChannel.SetSelection( 0 )
		bSizer1511.Add( self.cChannel, 1, wx.ALL, 5 )


		bSizer911.Add( bSizer1511, 0, wx.EXPAND, 5 )

		bSizer151111 = wx.BoxSizer( wx.HORIZONTAL )

		rSamplingEdgeChoices = [ u"TCK Rising Edge", u"TCK Falling Edge" ]
		self.rSamplingEdge = wx.RadioBox( self.pSettingsFT232H, wx.ID_ANY, u"Sampling Edge:", wx.DefaultPosition, wx.DefaultSize, rSamplingEdgeChoices, 1, wx.RA_SPECIFY_ROWS )
		self.rSamplingEdge.SetSelection( 0 )
		bSizer151111.Add( self.rSamplingEdge, 1, wx.ALL, 5 )


		bSizer911.Add( bSizer151111, 0, wx.EXPAND, 5 )

		bSizer15121 = wx.BoxSizer( wx.HORIZONTAL )

		self.bConfigureLayoutFT232H = wx.Button( self.pSettingsFT232H, wx.ID_ANY, u"Configure Layout", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer15121.Add( self.bConfigureLayoutFT232H, 1, wx.ALL, 5 )


		bSizer911.Add( bSizer15121, 1, wx.EXPAND, 5 )


		self.pSettingsFT232H.SetSizer( bSizer911 )
		self.pSettingsFT232H.Layout()
		bSizer911.Fit( self.pSettingsFT232H )
		bSizer8.Add( self.pSettingsFT232H, 1, wx.EXPAND |wx.ALL, 5 )


		self.dPage2.SetSizer( bSizer8 )
		self.dPage2.Layout()
		bSizer8.Fit( self.dPage2 )
		self.tab.AddPage( self.dPage2, u"Additional Settings", False )
		self.dPage3 = wx.Panel( self.tab, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer56 = wx.BoxSizer( wx.VERTICAL )

		bSizer57 = wx.BoxSizer( wx.HORIZONTAL )

		self.bDoIDCODE = wx.Button( self.dPage3, wx.ID_ANY, u"IDCODE Scan", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer57.Add( self.bDoIDCODE, 0, wx.ALL, 5 )

		self.bDoBYPASS = wx.Button( self.dPage3, wx.ID_ANY, u"BYPASS Scan", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer57.Add( self.bDoBYPASS, 0, wx.ALL, 5 )

		self.bDoRTCK = wx.Button( self.dPage3, wx.ID_ANY, u"RTCK Scan", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer57.Add( self.bDoRTCK, 0, wx.ALL, 5 )

		self.bUseMPSSE = wx.CheckBox( self.dPage3, wx.ID_ANY, u"Use MPSSE", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer57.Add( self.bUseMPSSE, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer56.Add( bSizer57, 0, wx.EXPAND, 5 )

		self.finderStatus = wx.richtext.RichTextCtrl( self.dPage3, wx.ID_ANY, u"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean ac libero vel massa tristique ullamcorper ac et quam. Nunc ultricies dui nibh, ac auctor augue pulvinar sit amet. Nulla malesuada, arcu eu aliquet semper, leo est tincidunt ante, id aliquet tortor leo vel ex. Suspendisse orci lorem, molestie in auctor in, lacinia a felis. Nam molestie sagittis rutrum. Pellentesque tellus mi, posuere sed bibendum quis, laoreet a dui. In vehicula feugiat est, sit amet pellentesque neque porta sit amet. Nam in elit malesuada, imperdiet dolor eu, maximus elit.\n\nDuis tincidunt ante at massa ornare, in vehicula dolor bibendum. Integer eu est interdum, malesuada ex id, rhoncus lectus. Nullam elementum orci in tellus vestibulum porttitor. Etiam vel lectus aliquet, iaculis erat ac, convallis tortor. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Sed bibendum ultrices tempus. Cras diam felis, sodales a lacinia non, rutrum sit amet nisl. Cras dapibus, ex vitae fringilla convallis, mi lacus faucibus lorem, a aliquam ligula orci in quam. Fusce eu erat maximus, volutpat mauris quis, egestas dolor.\n\nPellentesque elementum ultrices dignissim. Integer bibendum elementum auctor. Nulla facilisi. Integer tristique bibendum facilisis. Morbi id risus molestie, tempor diam non, dignissim mauris. In sit amet orci id tellus fringilla cursus. Nam rhoncus lectus a nibh congue, at fermentum elit accumsan. Proin congue nunc velit, at tempor arcu vulputate vitae. Aenean ac diam quis neque gravida ullamcorper. Pellentesque ac erat ex.\n\nMauris lectus risus, consequat quis eros vitae, feugiat fermentum purus. Aenean risus ipsum, dignissim quis consectetur hendrerit, ultrices sed velit. Duis maximus massa tellus, at blandit elit fringilla nec. Ut luctus facilisis mi, non vehicula lorem sagittis vel. Morbi gravida lacus eu sapien condimentum gravida. Vestibulum consectetur auctor est ac efficitur. Aliquam aliquam commodo nibh. Proin ultricies porttitor arcu id accumsan. Maecenas quam eros, egestas vitae fermentum laoreet, efficitur at lacus.\n\nCurabitur id erat eu sapien volutpat ullamcorper. Nulla volutpat dignissim varius. Duis vulputate imperdiet tincidunt. Aenean in leo feugiat, rhoncus erat quis, sollicitudin sapien. Vivamus imperdiet turpis sit amet velit tristique, in dictum dolor pharetra. Duis efficitur magna nec hendrerit congue. In vel luctus purus. ", wx.DefaultPosition, wx.DefaultSize, 0|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
		bSizer56.Add( self.finderStatus, 1, wx.EXPAND |wx.ALL, 5 )


		self.dPage3.SetSizer( bSizer56 )
		self.dPage3.Layout()
		bSizer56.Fit( self.dPage3 )
		self.tab.AddPage( self.dPage3, u"JTAG Finder (FTDI only)", False )
		self.dPage4 = wx.Panel( self.tab, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer44 = wx.BoxSizer( wx.VERTICAL )

		bSizer45 = wx.BoxSizer( wx.HORIZONTAL )

		self.bEnableAnalytics = wx.CheckBox( self.dPage4, wx.ID_ANY, u"Enable Analytics", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.bEnableAnalytics.SetValue(True)
		bSizer45.Add( self.bEnableAnalytics, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.lUserID = wx.StaticText( self.dPage4, wx.ID_ANY, u"User ID:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lUserID.Wrap( -1 )

		bSizer45.Add( self.lUserID, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.tUserID = wx.TextCtrl( self.dPage4, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
		bSizer45.Add( self.tUserID, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.bRegenUID = wx.Button( self.dPage4, wx.ID_ANY, u"Regenerate", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer45.Add( self.bRegenUID, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer44.Add( bSizer45, 0, wx.EXPAND, 5 )

		self.analytics_stat = wx.richtext.RichTextCtrl( self.dPage4, wx.ID_ANY, u"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean ac libero vel massa tristique ullamcorper ac et quam. Nunc ultricies dui nibh, ac auctor augue pulvinar sit amet. Nulla malesuada, arcu eu aliquet semper, leo est tincidunt ante, id aliquet tortor leo vel ex. Suspendisse orci lorem, molestie in auctor in, lacinia a felis. Nam molestie sagittis rutrum. Pellentesque tellus mi, posuere sed bibendum quis, laoreet a dui. In vehicula feugiat est, sit amet pellentesque neque porta sit amet. Nam in elit malesuada, imperdiet dolor eu, maximus elit.\n\nDuis tincidunt ante at massa ornare, in vehicula dolor bibendum. Integer eu est interdum, malesuada ex id, rhoncus lectus. Nullam elementum orci in tellus vestibulum porttitor. Etiam vel lectus aliquet, iaculis erat ac, convallis tortor. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Sed bibendum ultrices tempus. Cras diam felis, sodales a lacinia non, rutrum sit amet nisl. Cras dapibus, ex vitae fringilla convallis, mi lacus faucibus lorem, a aliquam ligula orci in quam. Fusce eu erat maximus, volutpat mauris quis, egestas dolor.\n\nPellentesque elementum ultrices dignissim. Integer bibendum elementum auctor. Nulla facilisi. Integer tristique bibendum facilisis. Morbi id risus molestie, tempor diam non, dignissim mauris. In sit amet orci id tellus fringilla cursus. Nam rhoncus lectus a nibh congue, at fermentum elit accumsan. Proin congue nunc velit, at tempor arcu vulputate vitae. Aenean ac diam quis neque gravida ullamcorper. Pellentesque ac erat ex.\n\nMauris lectus risus, consequat quis eros vitae, feugiat fermentum purus. Aenean risus ipsum, dignissim quis consectetur hendrerit, ultrices sed velit. Duis maximus massa tellus, at blandit elit fringilla nec. Ut luctus facilisis mi, non vehicula lorem sagittis vel. Morbi gravida lacus eu sapien condimentum gravida. Vestibulum consectetur auctor est ac efficitur. Aliquam aliquam commodo nibh. Proin ultricies porttitor arcu id accumsan. Maecenas quam eros, egestas vitae fermentum laoreet, efficitur at lacus.\n\nCurabitur id erat eu sapien volutpat ullamcorper. Nulla volutpat dignissim varius. Duis vulputate imperdiet tincidunt. Aenean in leo feugiat, rhoncus erat quis, sollicitudin sapien. Vivamus imperdiet turpis sit amet velit tristique, in dictum dolor pharetra. Duis efficitur magna nec hendrerit congue. In vel luctus purus. ", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
		bSizer44.Add( self.analytics_stat, 1, wx.EXPAND |wx.ALL, 5 )


		self.dPage4.SetSizer( bSizer44 )
		self.dPage4.Layout()
		bSizer44.Fit( self.dPage4 )
		self.tab.AddPage( self.dPage4, u"Analytics", False )

		bSizer3.Add( self.tab, 1, wx.EXPAND |wx.ALL, 5 )

		self.progress = wx.Gauge( self, wx.ID_ANY, 5000, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
		self.progress.SetValue( 2500 )
		bSizer3.Add( self.progress, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer1.Add( bSizer3, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.doQuit )
		self.Bind( wx.EVT_IDLE, self.doLoop )
		self.tab.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGING, self.loadNoteBook )
		self.nSpeed.Bind( wx.EVT_TEXT_ENTER, self.doProcessSpeedEntry )
		self.bConfigureRead.Bind( wx.EVT_BUTTON, self.doConfigureRead )
		self.cResetMode.Bind( wx.EVT_CHOICE, self.doProcessResetMode )
		self.bResetDelay.Bind( wx.EVT_BUTTON, self.bDoConfigureReset )
		self.tStart.Bind( wx.EVT_TEXT, self.doHexCheck )
		self.tEnd.Bind( wx.EVT_TEXT, self.doHexCheck )
		self.bConnect.Bind( wx.EVT_BUTTON, self.doConnect )
		self.bConnectRemote.Bind( wx.EVT_BUTTON, self.doConnectRemote )
		self.bForwardRemote.Bind( wx.EVT_BUTTON, self.doForwardRemote )
		self.bReconnectRemote.Bind( wx.EVT_BUTTON, self.doReconnectRemote )
		self.bDumpFlash.Bind( wx.EVT_BUTTON, self.doReadFlash )
		self.bDumpMemory.Bind( wx.EVT_BUTTON, self.doReadMemory )
		self.bStop.Bind( wx.EVT_BUTTON, self.doStop )
		self.bNandConfigure.Bind( wx.EVT_BUTTON, self.doNANDConfigure )
		self.bEditMetadata.Bind( wx.EVT_BUTTON, self.doEditMetadata )
		self.bGo.Bind( wx.EVT_BUTTON, self.doGo )
		self.bHalt.Bind( wx.EVT_BUTTON, self.doHalt )
		self.bReset.Bind( wx.EVT_BUTTON, self.doReset )
		self.bHardReset.Bind( wx.EVT_BUTTON, self.doHardReset )
		self.bExecScript.Bind( wx.EVT_BUTTON, self.doScript )
		self.bExecLoader.Bind( wx.EVT_BUTTON, self.doLoader )
		self.bEnableMMU.Bind( wx.EVT_BUTTON, self.doEnableMMU )
		self.bDisableMMU.Bind( wx.EVT_BUTTON, self.doDisableMMU )
		self.bExec.Bind( wx.EVT_BUTTON, self.doExecAddress )
		self.tOCDCmd.Bind( wx.EVT_KEY_DOWN, self.doProcessCmdArrow )
		self.tOCDCmd.Bind( wx.EVT_TEXT_ENTER, self.doOCDCmdExec )
		self.bConfigureLayoutFT232R.Bind( wx.EVT_BUTTON, self.doOpenFT232RConfig )
		self.bConfigureLayoutGPIOD.Bind( wx.EVT_BUTTON, self.doOpenGPIODConfig )
		self.cFTAdapter.Bind( wx.EVT_CHOICE, self.doFT232AdapterChange )
		self.bConfigureLayoutFT232H.Bind( wx.EVT_BUTTON, self.doOpenFT232HConfig )
		self.bDoIDCODE.Bind( wx.EVT_BUTTON, self.doIDCODE )
		self.bDoBYPASS.Bind( wx.EVT_BUTTON, self.doBYPASS )
		self.bDoRTCK.Bind( wx.EVT_BUTTON, self.doRTCK )
		self.bRegenUID.Bind( wx.EVT_BUTTON, self.doRegenUUID )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def doQuit( self, event ):
		event.Skip()

	def doLoop( self, event ):
		event.Skip()

	def loadNoteBook( self, event ):
		event.Skip()

	def doProcessSpeedEntry( self, event ):
		event.Skip()

	def doConfigureRead( self, event ):
		event.Skip()

	def doProcessResetMode( self, event ):
		event.Skip()

	def bDoConfigureReset( self, event ):
		event.Skip()

	def doHexCheck( self, event ):
		event.Skip()


	def doConnect( self, event ):
		event.Skip()

	def doConnectRemote( self, event ):
		event.Skip()

	def doForwardRemote( self, event ):
		event.Skip()

	def doReconnectRemote( self, event ):
		event.Skip()

	def doReadFlash( self, event ):
		event.Skip()

	def doReadMemory( self, event ):
		event.Skip()

	def doStop( self, event ):
		event.Skip()

	def doNANDConfigure( self, event ):
		event.Skip()

	def doEditMetadata( self, event ):
		event.Skip()

	def doGo( self, event ):
		event.Skip()

	def doHalt( self, event ):
		event.Skip()

	def doReset( self, event ):
		event.Skip()

	def doHardReset( self, event ):
		event.Skip()

	def doScript( self, event ):
		event.Skip()

	def doLoader( self, event ):
		event.Skip()

	def doEnableMMU( self, event ):
		event.Skip()

	def doDisableMMU( self, event ):
		event.Skip()

	def doExecAddress( self, event ):
		event.Skip()

	def doProcessCmdArrow( self, event ):
		event.Skip()

	def doOCDCmdExec( self, event ):
		event.Skip()

	def doOpenFT232RConfig( self, event ):
		event.Skip()

	def doOpenGPIODConfig( self, event ):
		event.Skip()

	def doFT232AdapterChange( self, event ):
		event.Skip()

	def doOpenFT232HConfig( self, event ):
		event.Skip()

	def doIDCODE( self, event ):
		event.Skip()

	def doBYPASS( self, event ):
		event.Skip()

	def doRTCK( self, event ):
		event.Skip()

	def doRegenUUID( self, event ):
		event.Skip()



# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-11d0e73)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.stc

###########################################################################
## Class NANDCodeEdit
###########################################################################

class NANDCodeEdit ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 640,480 ), style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer99 = wx.BoxSizer( wx.VERTICAL )

		self.tTCLCode = wx.stc.StyledTextCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)
		self.tTCLCode.SetUseTabs ( True )
		self.tTCLCode.SetTabWidth ( 4 )
		self.tTCLCode.SetIndent ( 4 )
		self.tTCLCode.SetTabIndents( True )
		self.tTCLCode.SetBackSpaceUnIndents( True )
		self.tTCLCode.SetViewEOL( False )
		self.tTCLCode.SetViewWhiteSpace( False )
		self.tTCLCode.SetMarginWidth( 2, 0 )
		self.tTCLCode.SetIndentationGuides( True )
		self.tTCLCode.SetReadOnly( False );
		self.tTCLCode.SetMarginType ( 1, wx.stc.STC_MARGIN_SYMBOL )
		self.tTCLCode.SetMarginMask ( 1, wx.stc.STC_MASK_FOLDERS )
		self.tTCLCode.SetMarginWidth ( 1, 16)
		self.tTCLCode.SetMarginSensitive( 1, True )
		self.tTCLCode.SetProperty ( "fold", "1" )
		self.tTCLCode.SetFoldFlags ( wx.stc.STC_FOLDFLAG_LINEBEFORE_CONTRACTED | wx.stc.STC_FOLDFLAG_LINEAFTER_CONTRACTED );
		self.tTCLCode.SetMarginType( 0, wx.stc.STC_MARGIN_NUMBER );
		self.tTCLCode.SetMarginWidth( 0, self.tTCLCode.TextWidth( wx.stc.STC_STYLE_LINENUMBER, "_99999" ) )
		self.tTCLCode.MarkerDefine( wx.stc.STC_MARKNUM_FOLDER, wx.stc.STC_MARK_BOXPLUS )
		self.tTCLCode.MarkerSetBackground( wx.stc.STC_MARKNUM_FOLDER, wx.BLACK)
		self.tTCLCode.MarkerSetForeground( wx.stc.STC_MARKNUM_FOLDER, wx.WHITE)
		self.tTCLCode.MarkerDefine( wx.stc.STC_MARKNUM_FOLDEROPEN, wx.stc.STC_MARK_BOXMINUS )
		self.tTCLCode.MarkerSetBackground( wx.stc.STC_MARKNUM_FOLDEROPEN, wx.BLACK )
		self.tTCLCode.MarkerSetForeground( wx.stc.STC_MARKNUM_FOLDEROPEN, wx.WHITE )
		self.tTCLCode.MarkerDefine( wx.stc.STC_MARKNUM_FOLDERSUB, wx.stc.STC_MARK_EMPTY )
		self.tTCLCode.MarkerDefine( wx.stc.STC_MARKNUM_FOLDEREND, wx.stc.STC_MARK_BOXPLUS )
		self.tTCLCode.MarkerSetBackground( wx.stc.STC_MARKNUM_FOLDEREND, wx.BLACK )
		self.tTCLCode.MarkerSetForeground( wx.stc.STC_MARKNUM_FOLDEREND, wx.WHITE )
		self.tTCLCode.MarkerDefine( wx.stc.STC_MARKNUM_FOLDEROPENMID, wx.stc.STC_MARK_BOXMINUS )
		self.tTCLCode.MarkerSetBackground( wx.stc.STC_MARKNUM_FOLDEROPENMID, wx.BLACK)
		self.tTCLCode.MarkerSetForeground( wx.stc.STC_MARKNUM_FOLDEROPENMID, wx.WHITE)
		self.tTCLCode.MarkerDefine( wx.stc.STC_MARKNUM_FOLDERMIDTAIL, wx.stc.STC_MARK_EMPTY )
		self.tTCLCode.MarkerDefine( wx.stc.STC_MARKNUM_FOLDERTAIL, wx.stc.STC_MARK_EMPTY )
		self.tTCLCode.SetSelBackground( True, wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT ) )
		self.tTCLCode.SetSelForeground( True, wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT ) )
		bSizer99.Add( self.tTCLCode, 1, wx.EXPAND |wx.ALL, 5 )

		gSizer4 = wx.GridSizer( 0, 2, 0, 0 )

		self.bApply = wx.Button( self, wx.ID_ANY, u"Apply", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer4.Add( self.bApply, 0, wx.ALL, 5 )

		self.bCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer4.Add( self.bCancel, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )


		bSizer99.Add( gSizer4, 0, wx.EXPAND, 5 )


		self.SetSizer( bSizer99 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.bApply.Bind( wx.EVT_BUTTON, self.doApply )
		self.bCancel.Bind( wx.EVT_BUTTON, self.doCancel )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def doApply( self, event ):
		event.Skip()

	def doCancel( self, event ):
		event.Skip()



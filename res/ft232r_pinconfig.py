# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-11d0e73)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class FT232R_Pin_Config
###########################################################################

class FT232R_Pin_Config ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 380,565 ), style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer33 = wx.BoxSizer( wx.VERTICAL )

		bSizer29 = wx.BoxSizer( wx.HORIZONTAL )

		self.l_Board = wx.StaticText( self, wx.ID_ANY, u"Board:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.l_Board.Wrap( -1 )

		self.l_Board.SetFont( wx.Font( 14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.l_Board.SetMinSize( wx.Size( 72,20 ) )

		bSizer29.Add( self.l_Board, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		c_BoardChoices = []
		self.c_Board = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, c_BoardChoices, 0 )
		self.c_Board.SetSelection( 0 )
		bSizer29.Add( self.c_Board, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer33.Add( bSizer29, 0, wx.ALIGN_RIGHT, 5 )

		bSizer27 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer36 = wx.BoxSizer( wx.VERTICAL )

		bSizer42 = wx.BoxSizer( wx.HORIZONTAL )

		self.l_tdi = wx.StaticText( self, wx.ID_ANY, u"TDI:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.l_tdi.Wrap( -1 )

		self.l_tdi.SetFont( wx.Font( 14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.l_tdi.SetMinSize( wx.Size( 60,20 ) )

		bSizer42.Add( self.l_tdi, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		cfg_tdiChoices = [ u"TX", u"RX", u"RTS", u"CTS", u"DTR", u"DSR", u"DCD", u"RI" ]
		self.cfg_tdi = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_tdiChoices, 0 )
		self.cfg_tdi.SetSelection( 1 )
		bSizer42.Add( self.cfg_tdi, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )


		bSizer36.Add( bSizer42, 0, wx.ALIGN_RIGHT, 5 )

		self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer36.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )

		bSizer421 = wx.BoxSizer( wx.HORIZONTAL )

		self.l_tdo = wx.StaticText( self, wx.ID_ANY, u"TDO:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.l_tdo.Wrap( -1 )

		self.l_tdo.SetFont( wx.Font( 14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.l_tdo.SetMinSize( wx.Size( 60,20 ) )

		bSizer421.Add( self.l_tdo, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		cfg_tdoChoices = [ u"TX", u"RX", u"RTS", u"CTS", u"DTR", u"DSR", u"DCD", u"RI" ]
		self.cfg_tdo = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_tdoChoices, 0 )
		self.cfg_tdo.SetSelection( 2 )
		bSizer421.Add( self.cfg_tdo, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )


		bSizer36.Add( bSizer421, 0, wx.ALIGN_RIGHT, 5 )

		self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer36.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )

		bSizer422 = wx.BoxSizer( wx.HORIZONTAL )

		self.l_tms = wx.StaticText( self, wx.ID_ANY, u"TMS:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.l_tms.Wrap( -1 )

		self.l_tms.SetFont( wx.Font( 14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.l_tms.SetMinSize( wx.Size( 60,20 ) )

		bSizer422.Add( self.l_tms, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		cfg_tmsChoices = [ u"TX", u"RX", u"RTS", u"CTS", u"DTR", u"DSR", u"DCD", u"RI" ]
		self.cfg_tms = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_tmsChoices, 0 )
		self.cfg_tms.SetSelection( 3 )
		bSizer422.Add( self.cfg_tms, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )


		bSizer36.Add( bSizer422, 0, wx.ALIGN_RIGHT, 5 )

		self.m_staticline3 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer36.Add( self.m_staticline3, 0, wx.EXPAND |wx.ALL, 5 )

		bSizer423 = wx.BoxSizer( wx.HORIZONTAL )

		self.l_tck = wx.StaticText( self, wx.ID_ANY, u"TCK:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.l_tck.Wrap( -1 )

		self.l_tck.SetFont( wx.Font( 14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.l_tck.SetMinSize( wx.Size( 60,20 ) )

		bSizer423.Add( self.l_tck, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		cfg_tckChoices = [ u"TX", u"RX", u"RTS", u"CTS", u"DTR", u"DSR", u"DCD", u"RI" ]
		self.cfg_tck = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_tckChoices, 0 )
		self.cfg_tck.SetSelection( 0 )
		bSizer423.Add( self.cfg_tck, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )


		bSizer36.Add( bSizer423, 0, wx.ALIGN_RIGHT, 5 )

		self.m_staticline4 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer36.Add( self.m_staticline4, 0, wx.EXPAND |wx.ALL, 5 )

		bSizer424 = wx.BoxSizer( wx.HORIZONTAL )

		self.l_trst = wx.StaticText( self, wx.ID_ANY, u"TRST:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.l_trst.Wrap( -1 )

		self.l_trst.SetFont( wx.Font( 14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.l_trst.SetMinSize( wx.Size( 60,20 ) )

		bSizer424.Add( self.l_trst, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		cfg_trstChoices = [ u"TX", u"RX", u"RTS", u"CTS", u"DTR", u"DSR", u"DCD", u"RI" ]
		self.cfg_trst = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_trstChoices, 0 )
		self.cfg_trst.SetSelection( 4 )
		bSizer424.Add( self.cfg_trst, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )


		bSizer36.Add( bSizer424, 0, wx.ALIGN_RIGHT, 5 )

		self.m_staticline5 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer36.Add( self.m_staticline5, 0, wx.EXPAND |wx.ALL, 5 )

		bSizer425 = wx.BoxSizer( wx.HORIZONTAL )

		self.l_srst = wx.StaticText( self, wx.ID_ANY, u"SRST:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.l_srst.Wrap( -1 )

		self.l_srst.SetFont( wx.Font( 14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.l_srst.SetMinSize( wx.Size( 60,20 ) )

		bSizer425.Add( self.l_srst, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		cfg_srstChoices = [ u"TX", u"RX", u"RTS", u"CTS", u"DTR", u"DSR", u"DCD", u"RI" ]
		self.cfg_srst = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_srstChoices, 0 )
		self.cfg_srst.SetSelection( 6 )
		bSizer425.Add( self.cfg_srst, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )


		bSizer36.Add( bSizer425, 0, wx.ALIGN_RIGHT, 5 )

		self.m_staticline6 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer36.Add( self.m_staticline6, 0, wx.EXPAND |wx.ALL, 5 )


		bSizer27.Add( bSizer36, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.board = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.board.SetMaxSize( wx.Size( 250,440 ) )

		bSizer27.Add( self.board, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer33.Add( bSizer27, 1, wx.EXPAND|wx.ALIGN_RIGHT, 5 )

		bSizer28 = wx.BoxSizer( wx.HORIZONTAL )

		self.bApply = wx.Button( self, wx.ID_ANY, u"Apply", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer28.Add( self.bApply, 0, wx.ALL, 5 )

		self.bCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer28.Add( self.bCancel, 0, wx.ALL, 5 )

		self.bReset = wx.Button( self, wx.ID_ANY, u"Reset to Defaults", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer28.Add( self.bReset, 0, wx.ALL, 5 )


		bSizer33.Add( bSizer28, 1, wx.ALIGN_RIGHT, 5 )


		self.SetSizer( bSizer33 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.c_Board.Bind( wx.EVT_CHOICE, self.doChangeBoard )
		self.cfg_tdi.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_tdo.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_tms.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_tck.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_trst.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_srst.Bind( wx.EVT_CHOICE, self.doChange )
		self.bApply.Bind( wx.EVT_BUTTON, self.doApply )
		self.bCancel.Bind( wx.EVT_BUTTON, self.doCancel )
		self.bReset.Bind( wx.EVT_BUTTON, self.doReset )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def doChangeBoard( self, event ):
		event.Skip()

	def doChange( self, event ):
		event.Skip()






	def doApply( self, event ):
		event.Skip()

	def doCancel( self, event ):
		event.Skip()

	def doReset( self, event ):
		event.Skip()



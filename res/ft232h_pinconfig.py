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
## Class FT232H_Pin_Config
###########################################################################

class FT232H_Pin_Config ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 650,565 ), style = wx.DEFAULT_DIALOG_STYLE )

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

		cfg_p10Choices = [ u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low", u"RTCK" ]
		self.cfg_p10 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_p10Choices, 0 )
		self.cfg_p10.SetSelection( 6 )
		bSizer36.Add( self.cfg_p10, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

		self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer36.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )

		cfg_p11Choices = [ u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low", u"RTCK" ]
		self.cfg_p11 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_p11Choices, 0 )
		self.cfg_p11.SetSelection( 6 )
		bSizer36.Add( self.cfg_p11, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

		self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer36.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )

		cfg_p12Choices = [ u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low", u"RTCK" ]
		self.cfg_p12 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_p12Choices, 0 )
		self.cfg_p12.SetSelection( 6 )
		bSizer36.Add( self.cfg_p12, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

		self.m_staticline3 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer36.Add( self.m_staticline3, 0, wx.EXPAND |wx.ALL, 5 )

		cfg_p13Choices = [ u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low", u"RTCK" ]
		self.cfg_p13 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_p13Choices, 0 )
		self.cfg_p13.SetSelection( 6 )
		bSizer36.Add( self.cfg_p13, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

		self.m_staticline4 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer36.Add( self.m_staticline4, 0, wx.EXPAND |wx.ALL, 5 )

		cfg_p14Choices = [ u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low", u"RTCK" ]
		self.cfg_p14 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_p14Choices, 0 )
		self.cfg_p14.SetSelection( 6 )
		bSizer36.Add( self.cfg_p14, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

		self.m_staticline5 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer36.Add( self.m_staticline5, 0, wx.EXPAND |wx.ALL, 5 )

		cfg_p15Choices = [ u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low", u"RTCK" ]
		self.cfg_p15 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_p15Choices, 0 )
		self.cfg_p15.SetSelection( 6 )
		bSizer36.Add( self.cfg_p15, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

		self.m_staticline6 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer36.Add( self.m_staticline6, 0, wx.EXPAND |wx.ALL, 5 )

		cfg_p16Choices = [ u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low", u"RTCK" ]
		self.cfg_p16 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_p16Choices, 0 )
		self.cfg_p16.SetSelection( 6 )
		bSizer36.Add( self.cfg_p16, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

		self.m_staticline7 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer36.Add( self.m_staticline7, 0, wx.EXPAND |wx.ALL, 5 )

		cfg_p17Choices = [ u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low", u"RTCK" ]
		self.cfg_p17 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_p17Choices, 0 )
		self.cfg_p17.SetSelection( 6 )
		bSizer36.Add( self.cfg_p17, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

		self.m_staticline8 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer36.Add( self.m_staticline8, 0, wx.EXPAND |wx.ALL, 5 )


		bSizer27.Add( bSizer36, 1, wx.EXPAND, 5 )

		self.board = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.board.SetMaxSize( wx.Size( 250,440 ) )

		bSizer27.Add( self.board, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

		bSizer361 = wx.BoxSizer( wx.VERTICAL )

		cfg_p20Choices = [ u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low", u"RTCK" ]
		self.cfg_p20 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_p20Choices, 0 )
		self.cfg_p20.SetSelection( 6 )
		bSizer361.Add( self.cfg_p20, 0, wx.ALL, 5 )

		self.m_staticline9 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer361.Add( self.m_staticline9, 0, wx.EXPAND |wx.ALL, 5 )

		cfg_p21Choices = [ u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low", u"RTCK" ]
		self.cfg_p21 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_p21Choices, 0 )
		self.cfg_p21.SetSelection( 6 )
		bSizer361.Add( self.cfg_p21, 0, wx.ALL, 5 )

		self.m_staticline10 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer361.Add( self.m_staticline10, 0, wx.EXPAND |wx.ALL, 5 )

		cfg_p22Choices = [ u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low", u"RTCK" ]
		self.cfg_p22 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_p22Choices, 0 )
		self.cfg_p22.SetSelection( 6 )
		bSizer361.Add( self.cfg_p22, 0, wx.ALL, 5 )

		self.m_staticline11 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer361.Add( self.m_staticline11, 0, wx.EXPAND |wx.ALL, 5 )

		cfg_p23Choices = [ u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low", u"RTCK" ]
		self.cfg_p23 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_p23Choices, 0 )
		self.cfg_p23.SetSelection( 6 )
		bSizer361.Add( self.cfg_p23, 0, wx.ALL, 5 )

		self.m_staticline12 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer361.Add( self.m_staticline12, 0, wx.EXPAND |wx.ALL, 5 )

		cfg_p24Choices = [ u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low", u"RTCK" ]
		self.cfg_p24 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_p24Choices, 0 )
		self.cfg_p24.SetSelection( 6 )
		bSizer361.Add( self.cfg_p24, 0, wx.ALL, 5 )

		self.m_staticline13 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer361.Add( self.m_staticline13, 0, wx.EXPAND |wx.ALL, 5 )

		cfg_p25Choices = [ u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low", u"RTCK" ]
		self.cfg_p25 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_p25Choices, 0 )
		self.cfg_p25.SetSelection( 6 )
		bSizer361.Add( self.cfg_p25, 0, wx.ALL, 5 )

		self.m_staticline14 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer361.Add( self.m_staticline14, 0, wx.EXPAND |wx.ALL, 5 )

		cfg_p26Choices = [ u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low", u"RTCK" ]
		self.cfg_p26 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_p26Choices, 0 )
		self.cfg_p26.SetSelection( 6 )
		bSizer361.Add( self.cfg_p26, 0, wx.ALL, 5 )

		self.m_staticline15 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer361.Add( self.m_staticline15, 0, wx.EXPAND |wx.ALL, 5 )

		cfg_p27Choices = [ u"TDI", u"TDO", u"TCK", u"TMS", u"TRST", u"SRST", u"High", u"Low", u"RTCK" ]
		self.cfg_p27 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cfg_p27Choices, 0 )
		self.cfg_p27.SetSelection( 6 )
		bSizer361.Add( self.cfg_p27, 0, wx.ALL, 5 )

		self.m_staticline16 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer361.Add( self.m_staticline16, 0, wx.EXPAND |wx.ALL, 5 )


		bSizer27.Add( bSizer361, 1, wx.EXPAND, 5 )


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
		self.cfg_p10.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_p11.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_p12.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_p13.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_p14.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_p15.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_p16.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_p17.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_p20.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_p21.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_p22.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_p23.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_p24.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_p25.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_p26.Bind( wx.EVT_CHOICE, self.doChange )
		self.cfg_p27.Bind( wx.EVT_CHOICE, self.doChange )
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



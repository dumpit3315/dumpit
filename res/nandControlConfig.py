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
## Class NANDControllerConfig
###########################################################################

class NANDControllerConfig ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 410,280 ), style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer65 = wx.BoxSizer( wx.VERTICAL )

		bSizer68 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer70 = wx.BoxSizer( wx.VERTICAL )

		bSizer69 = wx.BoxSizer( wx.HORIZONTAL )

		self.lPageWidth = wx.StaticText( self, wx.ID_ANY, u"Page Width:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lPageWidth.Wrap( -1 )

		bSizer69.Add( self.lPageWidth, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		cPageWidthChoices = [ u"Auto", u"8-bit", u"16-bit" ]
		self.cPageWidth = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cPageWidthChoices, 0 )
		self.cPageWidth.SetSelection( 0 )
		bSizer69.Add( self.cPageWidth, 0, wx.ALL, 5 )


		bSizer70.Add( bSizer69, 0, wx.EXPAND, 5 )

		bSizer691 = wx.BoxSizer( wx.HORIZONTAL )

		self.bSkipRegInit = wx.CheckBox( self, wx.ID_ANY, u"Skip Register Init:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		bSizer691.Add( self.bSkipRegInit, 1, wx.ALL, 5 )


		bSizer70.Add( bSizer691, 0, wx.EXPAND, 5 )

		bSizer6911 = wx.BoxSizer( wx.HORIZONTAL )

		self.bSkipGPIOInit = wx.CheckBox( self, wx.ID_ANY, u"Skip GPIO Init\n(MSM62XX only):", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		bSizer6911.Add( self.bSkipGPIOInit, 1, wx.ALL, 5 )


		bSizer70.Add( bSizer6911, 0, wx.EXPAND, 5 )

		bSizer69112 = wx.BoxSizer( wx.HORIZONTAL )

		self.bDisableMSM6550Quirks = wx.CheckBox( self, wx.ID_ANY, u"Disable MSM6550 Quirks", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		bSizer69112.Add( self.bDisableMSM6550Quirks, 1, wx.ALL, 5 )


		bSizer70.Add( bSizer69112, 0, wx.EXPAND, 5 )

		bSizer69113 = wx.BoxSizer( wx.HORIZONTAL )

		self.bUseFastAPI = wx.CheckBox( self, wx.ID_ANY, u"Use OpenOCD NAND API", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		bSizer69113.Add( self.bUseFastAPI, 1, wx.ALL, 5 )


		bSizer70.Add( bSizer69113, 0, wx.EXPAND, 5 )

		bSizer691131 = wx.BoxSizer( wx.HORIZONTAL )

		self.bSelect2ndBank = wx.CheckBox( self, wx.ID_ANY, u"Select 2nd Bank", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		bSizer691131.Add( self.bSelect2ndBank, 1, wx.ALL, 5 )


		bSizer70.Add( bSizer691131, 1, wx.EXPAND, 5 )


		bSizer68.Add( bSizer70, 1, 0, 5 )

		bSizer701 = wx.BoxSizer( wx.VERTICAL )

		bSizer692 = wx.BoxSizer( wx.HORIZONTAL )

		self.lCustomCFG1 = wx.StaticText( self, wx.ID_ANY, u"CFG1:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lCustomCFG1.Wrap( -1 )

		bSizer692.Add( self.lCustomCFG1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.tCustomCFG1 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer692.Add( self.tCustomCFG1, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer701.Add( bSizer692, 0, wx.EXPAND, 5 )

		bSizer6912 = wx.BoxSizer( wx.HORIZONTAL )

		self.lCustomCFG2 = wx.StaticText( self, wx.ID_ANY, u"CFG2:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lCustomCFG2.Wrap( -1 )

		bSizer6912.Add( self.lCustomCFG2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.tCustomCFG2 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6912.Add( self.tCustomCFG2, 1, wx.ALL, 5 )


		bSizer701.Add( bSizer6912, 0, wx.EXPAND, 5 )

		bSizer69111 = wx.BoxSizer( wx.HORIZONTAL )

		self.lCustomCFGCMN = wx.StaticText( self, wx.ID_ANY, u"Common\nCFG:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lCustomCFGCMN.Wrap( -1 )

		bSizer69111.Add( self.lCustomCFGCMN, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.tCustomCFGCMN = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer69111.Add( self.tCustomCFGCMN, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer701.Add( bSizer69111, 0, wx.EXPAND, 5 )

		bSizer691111 = wx.BoxSizer( wx.HORIZONTAL )

		self.bCodeEdit = wx.Button( self, wx.ID_ANY, u"Edit Init Code", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer691111.Add( self.bCodeEdit, 0, wx.ALL, 5 )


		bSizer701.Add( bSizer691111, 1, wx.ALIGN_RIGHT, 5 )


		bSizer68.Add( bSizer701, 1, wx.EXPAND, 5 )


		bSizer65.Add( bSizer68, 1, wx.EXPAND, 5 )

		bSizer66 = wx.BoxSizer( wx.HORIZONTAL )

		self.bApply = wx.Button( self, wx.ID_ANY, u"Apply", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer66.Add( self.bApply, 0, wx.ALL, 5 )

		self.bCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer66.Add( self.bCancel, 0, wx.ALL, 5 )


		bSizer65.Add( bSizer66, 0, wx.ALIGN_RIGHT, 5 )


		self.SetSizer( bSizer65 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.bCodeEdit.Bind( wx.EVT_BUTTON, self.doCodeEdit )
		self.bApply.Bind( wx.EVT_BUTTON, self.doApply )
		self.bCancel.Bind( wx.EVT_BUTTON, self.doCancel )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def doCodeEdit( self, event ):
		event.Skip()

	def doApply( self, event ):
		event.Skip()

	def doCancel( self, event ):
		event.Skip()



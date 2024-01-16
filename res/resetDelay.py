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
## Class ResetDelayConfig
###########################################################################

class ResetDelayConfig ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer59 = wx.BoxSizer( wx.VERTICAL )

		bSizer58 = wx.BoxSizer( wx.HORIZONTAL )

		self.lnTRSTWidth = wx.StaticText( self, wx.ID_ANY, u"nTRST Pulse Width:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lnTRSTWidth.Wrap( -1 )

		bSizer58.Add( self.lnTRSTWidth, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.nNTRSTWidth = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 1000, 0 )
		bSizer58.Add( self.nNTRSTWidth, 0, wx.ALL, 5 )


		bSizer59.Add( bSizer58, 1, wx.EXPAND, 5 )

		bSizer581 = wx.BoxSizer( wx.HORIZONTAL )

		self.lnSRSTWidth = wx.StaticText( self, wx.ID_ANY, u"nSRST Pulse Width:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lnSRSTWidth.Wrap( -1 )

		bSizer581.Add( self.lnSRSTWidth, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.nSRSTWidth = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 1000, 0 )
		bSizer581.Add( self.nSRSTWidth, 0, wx.ALL, 5 )


		bSizer59.Add( bSizer581, 1, wx.EXPAND, 5 )

		bSizer582 = wx.BoxSizer( wx.HORIZONTAL )

		self.lNTRSTDelay = wx.StaticText( self, wx.ID_ANY, u"nTRST Delay:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lNTRSTDelay.Wrap( -1 )

		bSizer582.Add( self.lNTRSTDelay, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.nNTRSTDelay = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 1000, 0 )
		bSizer582.Add( self.nNTRSTDelay, 0, wx.ALL, 5 )


		bSizer59.Add( bSizer582, 1, wx.EXPAND, 5 )

		bSizer583 = wx.BoxSizer( wx.HORIZONTAL )

		self.lSRSTDelay = wx.StaticText( self, wx.ID_ANY, u"nSRST Delay:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lSRSTDelay.Wrap( -1 )

		bSizer583.Add( self.lSRSTDelay, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.nSRSTDelay = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 1000, 0 )
		bSizer583.Add( self.nSRSTDelay, 0, wx.ALL, 5 )


		bSizer59.Add( bSizer583, 1, wx.EXPAND, 5 )

		bSizer584 = wx.BoxSizer( wx.HORIZONTAL )

		self.lnResetDelay = wx.StaticText( self, wx.ID_ANY, u"Reset Delay", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lnResetDelay.Wrap( -1 )

		bSizer584.Add( self.lnResetDelay, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.nResetDelay = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 1000, 0 )
		bSizer584.Add( self.nResetDelay, 0, wx.ALL, 5 )


		bSizer59.Add( bSizer584, 1, wx.EXPAND, 5 )

		bSizer5841 = wx.BoxSizer( wx.HORIZONTAL )

		self.bApply = wx.Button( self, wx.ID_ANY, u"Apply", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer5841.Add( self.bApply, 0, wx.ALL, 5 )

		self.bCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer5841.Add( self.bCancel, 0, wx.ALL, 5 )


		bSizer59.Add( bSizer5841, 1, wx.ALIGN_RIGHT, 5 )


		self.SetSizer( bSizer59 )
		self.Layout()
		bSizer59.Fit( self )

		self.Centre( wx.BOTH )

		# Connect Events
		self.bApply.Bind( wx.EVT_BUTTON, self.bDoApply )
		self.bCancel.Bind( wx.EVT_BUTTON, self.bDoCancel )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def bDoApply( self, event ):
		event.Skip()

	def bDoCancel( self, event ):
		event.Skip()



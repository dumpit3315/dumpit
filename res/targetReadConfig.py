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
## Class TargetReadConfig
###########################################################################

class TargetReadConfig ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,275 ), style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer89 = wx.BoxSizer( wx.VERTICAL )

		bSizer91 = wx.BoxSizer( wx.VERTICAL )

		bSizer92 = wx.BoxSizer( wx.HORIZONTAL )

		self.lReadSize = wx.StaticText( self, wx.ID_ANY, u"Read size:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lReadSize.Wrap( -1 )

		bSizer92.Add( self.lReadSize, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.sReadSize = wx.Slider( self, wx.ID_ANY, 2, 2, 256, wx.DefaultPosition, wx.DefaultSize, wx.SL_BOTH|wx.SL_HORIZONTAL )
		bSizer92.Add( self.sReadSize, 1, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer91.Add( bSizer92, 0, wx.EXPAND, 5 )

		self.tReadSize = wx.StaticText( self, wx.ID_ANY, u"512 bytes", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
		self.tReadSize.Wrap( -1 )

		bSizer91.Add( self.tReadSize, 0, wx.ALL|wx.EXPAND, 5 )

		bSizer921 = wx.BoxSizer( wx.HORIZONTAL )

		self.lMaxPass = wx.StaticText( self, wx.ID_ANY, u"Max read pass:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lMaxPass.Wrap( -1 )

		bSizer921.Add( self.lMaxPass, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.sMaxPass = wx.SpinCtrl( self, wx.ID_ANY, u"10", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 2, 30, 0 )
		bSizer921.Add( self.sMaxPass, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.lMaxIdentical = wx.StaticText( self, wx.ID_ANY, u"Max identical pass:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lMaxIdentical.Wrap( -1 )

		bSizer921.Add( self.lMaxIdentical, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.sMaxIdentical = wx.SpinCtrl( self, wx.ID_ANY, u"3", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 2, 30, 0 )
		bSizer921.Add( self.sMaxIdentical, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer91.Add( bSizer921, 0, wx.EXPAND, 5 )

		bSizer9211 = wx.BoxSizer( wx.HORIZONTAL )

		self.bCheckIdentical = wx.CheckBox( self, wx.ID_ANY, u"Check identical dumps:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.bCheckIdentical.SetValue(True)
		bSizer9211.Add( self.bCheckIdentical, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.bDisablePerformanceOpts = wx.CheckBox( self, wx.ID_ANY, u"Disable target-specific performance options:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		bSizer9211.Add( self.bDisablePerformanceOpts, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer91.Add( bSizer9211, 0, wx.EXPAND, 5 )

		bSizer92111 = wx.BoxSizer( wx.HORIZONTAL )

		self.lIdenticalMode = wx.StaticText( self, wx.ID_ANY, u"Identical dumps check mode: ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lIdenticalMode.Wrap( -1 )

		bSizer92111.Add( self.lIdenticalMode, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		cIdenticalModeChoices = [ u"Check per page", u"Check per dump" ]
		self.cIdenticalMode = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cIdenticalModeChoices, 0 )
		self.cIdenticalMode.SetSelection( 0 )
		bSizer92111.Add( self.cIdenticalMode, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer91.Add( bSizer92111, 0, wx.EXPAND, 5 )


		bSizer89.Add( bSizer91, 1, wx.EXPAND, 5 )

		bSizer90 = wx.BoxSizer( wx.HORIZONTAL )

		self.bApply = wx.Button( self, wx.ID_ANY, u"Apply", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer90.Add( self.bApply, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.bCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer90.Add( self.bCancel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer89.Add( bSizer90, 0, wx.ALIGN_RIGHT, 5 )


		self.SetSizer( bSizer89 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.sReadSize.Bind( wx.EVT_SLIDER, self.doChangeReadSize )
		self.bApply.Bind( wx.EVT_BUTTON, self.doApply )
		self.bCancel.Bind( wx.EVT_BUTTON, self.doCancel )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def doChangeReadSize( self, event ):
		event.Skip()

	def doApply( self, event ):
		event.Skip()

	def doCancel( self, event ):
		event.Skip()



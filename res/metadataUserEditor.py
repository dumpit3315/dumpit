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
## Class MetadataEditor
###########################################################################

class MetadataEditor ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 400,320 ), style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer86 = wx.BoxSizer( wx.VERTICAL )

		bSizer88 = wx.BoxSizer( wx.VERTICAL )

		bSizer102 = wx.BoxSizer( wx.HORIZONTAL )

		self.lDeviceName = wx.StaticText( self, wx.ID_ANY, u"Device name:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lDeviceName.Wrap( -1 )

		bSizer102.Add( self.lDeviceName, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.tDeviceName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer102.Add( self.tDeviceName, 1, wx.ALL, 5 )


		bSizer88.Add( bSizer102, 0, wx.EXPAND, 5 )

		bSizer1021 = wx.BoxSizer( wx.HORIZONTAL )

		self.lManufacturer = wx.StaticText( self, wx.ID_ANY, u"Manufacturer:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lManufacturer.Wrap( -1 )

		bSizer1021.Add( self.lManufacturer, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.tManufacturer = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer1021.Add( self.tManufacturer, 1, wx.ALL, 5 )


		bSizer88.Add( bSizer1021, 0, wx.EXPAND, 5 )

		bSizer102111 = wx.BoxSizer( wx.HORIZONTAL )

		self.lDeviceVersion = wx.StaticText( self, wx.ID_ANY, u"Device version:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lDeviceVersion.Wrap( -1 )

		bSizer102111.Add( self.lDeviceVersion, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.tDeviceVersion = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer102111.Add( self.tDeviceVersion, 1, wx.ALL, 5 )


		bSizer88.Add( bSizer102111, 0, wx.EXPAND, 5 )

		bSizer10211 = wx.BoxSizer( wx.HORIZONTAL )

		self.lPerformer = wx.StaticText( self, wx.ID_ANY, u"Performer:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lPerformer.Wrap( -1 )

		bSizer10211.Add( self.lPerformer, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.tPerformer = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer10211.Add( self.tPerformer, 1, wx.ALL, 5 )


		bSizer88.Add( bSizer10211, 0, wx.EXPAND, 5 )

		bSizer102113 = wx.BoxSizer( wx.HORIZONTAL )

		self.lLender = wx.StaticText( self, wx.ID_ANY, u"Lender:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lLender.Wrap( -1 )

		bSizer102113.Add( self.lLender, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.tLender = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer102113.Add( self.tLender, 1, wx.ALL, 5 )


		bSizer88.Add( bSizer102113, 0, wx.EXPAND, 5 )

		bSizer102114 = wx.BoxSizer( wx.HORIZONTAL )

		self.cDisableMetadata = wx.CheckBox( self, wx.ID_ANY, u"Disable metadata:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		bSizer102114.Add( self.cDisableMetadata, 1, wx.ALL, 5 )


		bSizer88.Add( bSizer102114, 0, wx.EXPAND, 5 )


		bSizer86.Add( bSizer88, 1, wx.EXPAND, 5 )

		bSizer87 = wx.BoxSizer( wx.HORIZONTAL )

		self.bApply = wx.Button( self, wx.ID_ANY, u"Apply", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer87.Add( self.bApply, 0, wx.ALL, 5 )

		self.bCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer87.Add( self.bCancel, 0, wx.ALL, 5 )


		bSizer86.Add( bSizer87, 0, wx.ALIGN_RIGHT, 5 )


		self.SetSizer( bSizer86 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.bApply.Bind( wx.EVT_BUTTON, self.doApply )
		self.bCancel.Bind( wx.EVT_BUTTON, self.doApply )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def doApply( self, event ):
		event.Skip()




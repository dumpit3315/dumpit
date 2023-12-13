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
## Class forwardDialog
###########################################################################

class forwardDialog ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 384,229 ), style = wx.CAPTION|wx.SYSTEM_MENU )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer23 = wx.BoxSizer( wx.VERTICAL )

		self.lPin = wx.StaticText( self, wx.ID_ANY, u"Your Instance Code is:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
		self.lPin.Wrap( -1 )

		self.lPin.SetFont( wx.Font( 18, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Sans" ) )
		self.lPin.SetMinSize( wx.Size( -1,30 ) )

		bSizer23.Add( self.lPin, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )

		self.tPin = wx.TextCtrl( self, wx.ID_ANY, u"1a2b3c4d", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_READONLY )
		self.tPin.SetFont( wx.Font( 32, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

		bSizer23.Add( self.tPin, 1, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )

		self.status = wx.richtext.RichTextCtrl( self, wx.ID_ANY, u"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean ac libero vel massa tristique ullamcorper ac et quam. Nunc ultricies dui nibh, ac auctor augue pulvinar sit amet. Nulla malesuada, arcu eu aliquet semper, leo est tincidunt ante, id aliquet tortor leo vel ex. Suspendisse orci lorem, molestie in auctor in, lacinia a felis. Nam molestie sagittis rutrum. Pellentesque tellus mi, posuere sed bibendum quis, laoreet a dui. In vehicula feugiat est, sit amet pellentesque neque porta sit amet. Nam in elit malesuada, imperdiet dolor eu, maximus elit.\n\nDuis tincidunt ante at massa ornare, in vehicula dolor bibendum. Integer eu est interdum, malesuada ex id, rhoncus lectus. Nullam elementum orci in tellus vestibulum porttitor. Etiam vel lectus aliquet, iaculis erat ac, convallis tortor. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Sed bibendum ultrices tempus. Cras diam felis, sodales a lacinia non, rutrum sit amet nisl. Cras dapibus, ex vitae fringilla convallis, mi lacus faucibus lorem, a aliquam ligula orci in quam. Fusce eu erat maximus, volutpat mauris quis, egestas dolor.\n\nPellentesque elementum ultrices dignissim. Integer bibendum elementum auctor. Nulla facilisi. Integer tristique bibendum facilisis. Morbi id risus molestie, tempor diam non, dignissim mauris. In sit amet orci id tellus fringilla cursus. Nam rhoncus lectus a nibh congue, at fermentum elit accumsan. Proin congue nunc velit, at tempor arcu vulputate vitae. Aenean ac diam quis neque gravida ullamcorper. Pellentesque ac erat ex.\n\nMauris lectus risus, consequat quis eros vitae, feugiat fermentum purus. Aenean risus ipsum, dignissim quis consectetur hendrerit, ultrices sed velit. Duis maximus massa tellus, at blandit elit fringilla nec. Ut luctus facilisis mi, non vehicula lorem sagittis vel. Morbi gravida lacus eu sapien condimentum gravida. Vestibulum consectetur auctor est ac efficitur. Aliquam aliquam commodo nibh. Proin ultricies porttitor arcu id accumsan. Maecenas quam eros, egestas vitae fermentum laoreet, efficitur at lacus.\n\nCurabitur id erat eu sapien volutpat ullamcorper. Nulla volutpat dignissim varius. Duis vulputate imperdiet tincidunt. Aenean in leo feugiat, rhoncus erat quis, sollicitudin sapien. Vivamus imperdiet turpis sit amet velit tristique, in dictum dolor pharetra. Duis efficitur magna nec hendrerit congue. In vel luctus purus. ", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
		self.status.Hide()

		bSizer23.Add( self.status, 1, wx.EXPAND |wx.ALL, 5 )

		self.bStop = wx.Button( self, wx.ID_ANY, u"Stop", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer23.Add( self.bStop, 0, wx.ALL, 5 )


		self.SetSizer( bSizer23 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_IDLE, self.doLoop )
		self.bStop.Bind( wx.EVT_BUTTON, self.doStop )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def doLoop( self, event ):
		event.Skip()

	def doStop( self, event ):
		event.Skip()



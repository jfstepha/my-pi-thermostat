#!/usr/bin/python

import wx
from wx.lib.wordwrap import wordwrap
import requests
import re
import datetime

url = "http://localhost:80"

####################################################################################
####################################################################################
class PanelMain(wx.Panel):
####################################################################################
####################################################################################

   #################################################################### 
   def __init__(self, parent):
   #################################################################### 
        #### MAIN panel ######
        wx.Panel.__init__(self,parent=parent)
        self.bnJon = wx.Button(self, -1, "Jon", (150,150))
        self.bnGretch = wx.Button(self, -1, "Gretch", (150,150))
        self.bnJon.SetFont(wx.Font(20, wx.DEFAULT, wx.BOLD, wx.NORMAL))
        self.bnGretch.SetFont(wx.Font(20, wx.DEFAULT, wx.BOLD, wx.NORMAL))

        self.sizerMainH = wx.BoxSizer(wx.HORIZONTAL)
        self.sizerMainH.Add(self.bnJon, 1, wx.EXPAND)
        self.sizerMainH.Add(self.bnGretch, 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, parent.OnBnJon, self.bnJon)
        self.Bind(wx.EVT_BUTTON, parent.OnBnGretch, self.bnGretch)

        self.sizerMainH.Fit(self)
        self.SetSizer(self.sizerMainH)
        self.SetAutoLayout(1)



####################################################################################
####################################################################################
class PanelUser(wx.Panel):
####################################################################################
####################################################################################

   #################################################################### 
   def __init__(self, parent):
   #################################################################### 
        self.parent = parent
        wx.Panel.__init__(self,parent=parent)

        self.sizerJonH = wx.BoxSizer(wx.HORIZONTAL)
        self.lTargTmp = wx.StaticText(self, -1, "Target: 70")
        self.lCurTmp = wx.StaticText(self, -1, "Current: 70")
        self.lTargTmp.SetFont(wx.Font(20, wx.DEFAULT, wx.BOLD, wx.NORMAL))
        self.lCurTmp.SetFont(wx.Font(20, wx.DEFAULT, wx.BOLD, wx.NORMAL))

        self.bnUp = wx.Button(self, -1, "Up", (150,150))
        self.bnDown = wx.Button(self, -1, "Down", (150,150))
        self.bnBack = wx.Button(self, -1, "Back", (150,150))

        self.sizerJonVL = wx.BoxSizer(wx.VERTICAL)
        self.sizerJonVL.Add(self.bnUp, 1, wx.EXPAND )
        self.sizerJonVL.Add(self.bnDown, 1, wx.EXPAND)

        self.bnUp.SetFont(wx.Font(25, wx.DEFAULT, wx.BOLD, wx.NORMAL))
        self.bnDown.SetFont(wx.Font(25, wx.DEFAULT, wx.BOLD, wx.NORMAL))
        self.bnBack.SetFont(wx.Font(25, wx.DEFAULT, wx.BOLD, wx.NORMAL))

        self.Bind(wx.EVT_BUTTON, parent.OnBnUp, self.bnUp)
        self.Bind(wx.EVT_BUTTON, parent.OnBnDown, self.bnDown)
        self.Bind(wx.EVT_BUTTON, parent.OnBnBack, self.bnBack)
        
        
        self.bnModeHeat = wx.ToggleButton( self, -1, "Heat")
        self.bnModeCool = wx.ToggleButton( self, -1, "Cool" )
        self.bnModeOff = wx.ToggleButton( self, -1, "Off" )
        self.bnModeAway = wx.ToggleButton( self, -1, "Away" )
        
        self.bnModeHeat.SetBackgroundColour( "#FFDDDD" )
        self.bnModeCool.SetBackgroundColour( "#DDDDFF" )
        
        self.Bind(wx.EVT_TOGGLEBUTTON, parent.OnModeHeat, self.bnModeHeat)
        self.Bind(wx.EVT_TOGGLEBUTTON, parent.OnModeCool, self.bnModeCool)
        self.Bind(wx.EVT_TOGGLEBUTTON, parent.OnModeOff, self.bnModeOff)
        self.Bind(wx.EVT_TOGGLEBUTTON, parent.OnModeAway, self.bnModeAway)

        self.sizerModeV = wx.BoxSizer( wx.VERTICAL )
        self.sizerModeHT = wx.BoxSizer( wx.HORIZONTAL)
        self.sizerModeHB = wx.BoxSizer( wx.HORIZONTAL )
       
        self.sizerModeHT.Add( self.bnModeHeat, 1, wx.EXPAND )
        self.sizerModeHT.Add( self.bnModeCool, 1, wx.EXPAND )
        self.sizerModeHB.Add( self.bnModeOff, 1, wx.EXPAND )
        self.sizerModeHB.Add( self.bnModeAway, 1, wx.EXPAND )
        self.sizerModeV.Add( self.sizerModeHT, 1, wx.EXPAND)
        self.sizerModeV.Add( self.sizerModeHB, 1, wx.EXPAND)

        self.sizerJonVR = wx.BoxSizer(wx.VERTICAL)
        self.sizerJonVR.Add(self.lTargTmp, 1, wx.EXPAND)
        self.sizerJonVR.Add(self.lCurTmp, 1, wx.EXPAND)
        self.sizerJonVR.Add(self.sizerModeHT, 1, wx.EXPAND)
        self.sizerJonVR.Add(self.sizerModeHB, 1, wx.EXPAND)
        self.sizerJonVR.Add(self.bnBack, 1, wx.EXPAND)
        
        self.sizerJonH.Add(self.sizerJonVL, 1, wx.EXPAND)
        self.sizerJonH.Add(self.sizerJonVR, 1, wx.EXPAND)

        self.SetSizer(self.sizerJonH)
        self.sizerJonVR.Fit(self)
        self.sizerJonVL.Fit(self)
        self.sizerJonH.Fit(self)
   #################################################################### 
   def updateMode(self, mode):
   #################################################################### 
        if mode == "heat":
            self.bnModeHeat.SetValue( True )
            self.bnModeCool.SetValue( False )
            self.bnModeOff.SetValue( False )
            self.bnModeAway.SetValue( False )
        elif mode == "cool":
            self.bnModeHeat.SetValue( False)
            self.bnModeCool.SetValue( True )
            self.bnModeOff.SetValue( False )
            self.bnModeAway.SetValue( False )
        elif mode == "off":
            self.bnModeHeat.SetValue( False)
            self.bnModeCool.SetValue( False )
            self.bnModeOff.SetValue( True )
            self.bnModeAway.SetValue( False )
        elif mode == "away":
            self.bnModeHeat.SetValue( False)
            self.bnModeCool.SetValue( False )
            self.bnModeOff.SetValue( False )
            self.bnModeAway.SetValue( True )
            

####################################################################################
####################################################################################
class PanelMode(wx.Panel):
####################################################################################
####################################################################################
   #################################################################### 
   def __init__(self, parent):
   #################################################################### 
        wx.Panel.__init__(self,parent=parent, style=wx.SUNKEN_BORDER)
        self.sizerH = wx.BoxSizer(wx.HORIZONTAL)
        self.lblCurrent = wx.StaticText(self, -1, "C:xxx ")
        self.lblTarg = wx.StaticText(self, -1, "S:xxx ")
        self.lblMode = wx.StaticText(self, -1, "M:xxxx ")
        #self.lblWhatsOn = wx.StaticText(self, -1, "H:xxx C:xxx F:xxx ")
        self.lblHOn = wx.StaticText(self, -1, "H:xxx")
        self.lblCOn = wx.StaticText(self, -1, "C:xxx")
        self.lblFOn = wx.StaticText(self, -1, "F:xxx")
        self.sizerH.Add(self.lblCurrent)
        self.sizerH.Add(self.lblTarg)
        self.sizerH.Add(self.lblMode)
        #self.sizerH.Add(self.lblWhatsOn)
        self.sizerH.Add(self.lblHOn)
        self.sizerH.Add(self.lblCOn)
        self.sizerH.Add(self.lblFOn)
        self.SetSizer(self.sizerH)
        self.sizerH.Fit(self)


####################################################################################
####################################################################################
class PanelStatus(wx.Panel):
####################################################################################
####################################################################################

   #################################################################### 
   def __init__(self, parent):
   #################################################################### 
        wx.Panel.__init__(self,parent=parent, style=wx.SUNKEN_BORDER)
        self.sizerH = wx.BoxSizer(wx.HORIZONTAL)
        self.lblCurrent = wx.StaticText(self, -1, "C:xxxxx ")
        self.lblTarg = wx.StaticText(self, -1, "S:xxxxx ")
        self.lblMode = wx.StaticText(self, -1, "M:xxxxxx ")
        self.lblHOn = wx.StaticText(self, -1, "H:xxxxx")
        self.lblCOn = wx.StaticText(self, -1, "C:xxxxx")
        self.lblFOn = wx.StaticText(self, -1, "F:xxxxx")
        self.sizerH.Add(self.lblCurrent)
        self.sizerH.Add(self.lblTarg)
        self.sizerH.Add(self.lblMode)
        self.sizerH.Add(self.lblHOn)
        self.sizerH.Add(self.lblCOn)
        self.sizerH.Add(self.lblFOn)
        self.SetSizer(self.sizerH)
        self.sizerH.Fit(self)

   #################################################################### 
   def updateTarg(self, setTmp):
   #################################################################### 
        self.lblTarg.SetLabel("T:%.1f" % setTmp)
        self.Layout()
        
   #################################################################### 
   def updateCurrent(self, curTmp):
   #################################################################### 
        self.lblCurrent.SetLabel("C:%.1f " % curTmp)
   
   #################################################################### 
   def updateMode(self, mode):
   #################################################################### 
        self.lblMode.SetLabel("M:%s " % mode)
   
   #################################################################### 
   def updateWhatsOn(self, heat, cool, fan):
   #################################################################### 
        #self.lblWhatsOn.SetLabel("H:%s C:%s F:%s " % (heat, cool, fan))
        self.lblHOn.SetLabel("H:%s " % heat)
        self.lblCOn.SetLabel("C:%s " % cool)
        self.lblFOn.SetLabel("F:%s " % fan)

        if heat == "ON":
            self.lblHOn.SetForegroundColour("#FF0000")
        else:
            self.lblHOn.SetForegroundColour("#000000")
            
        if cool == "ON":
            self.lblCOn.SetForegroundColour("#0000FF")
        else:
            self.lblCOn.SetForegroundColour("#000000")
            
        if fan == "ON":
            self.lblFOn.SetForegroundColour("#008800")
        else:
            self.lblFOn.SetForegroundColour("#000000")

####################################################################################
####################################################################################
class PanelJon(PanelUser):
####################################################################################
####################################################################################
    def __init__(self, parent):
        PanelUser.__init__(self,parent)

        
####################################################################################
####################################################################################
class PanelGretch(PanelUser):
####################################################################################
####################################################################################
    def __init__(self, parent):
        PanelUser.__init__(self,parent)
        self.bnUp.SetLabel( "I'm cold")
        self.bnDown.SetLabel( "I'm hot")

        
   

####################################################################################
####################################################################################
class MainFrame(wx.Frame):
####################################################################################
####################################################################################

    #################################################################### 
    def __init__(self, redirect=False, filename=None):
    #################################################################### 
        self.setpt = 70
        self.user = "none"
        wx.Frame.__init__(self, None, wx.ID_ANY, title='Main') 
        self.timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(5000)

        ### Common controls ####
        self.sizerH = wx.BoxSizer(wx.HORIZONTAL)
        self.sizerV = wx.BoxSizer(wx.VERTICAL)

        self.pnMain = PanelMain(self)
        self.pnJon = PanelJon(self)
        self.pnGretch = PanelGretch(self)
        self.pnStat = PanelStatus(self)

        self.sizerH.Add(self.pnMain, 1, wx.EXPAND)
        self.sizerH.Add(self.pnJon, 1, wx.EXPAND)
        self.sizerH.Add(self.pnGretch, 1, wx.EXPAND)
        self.sizerV.Add(self.sizerH, 1, wx.EXPAND)
        self.sizerV.Add(self.pnStat,0)

        self.pnJon.Hide()
        self.pnGretch.Hide()
        self.SetSizer(self.sizerV)
        
        self.ticks_since_interaction = 0
        
    #################################################################### 
    def reset_timeout(self):
    #################################################################### 
        self.ticks_since_interaction = 0

    #################################################################### 
    def on_timer(self, evt):
    #################################################################### 
        print "[%s] my_gui tick" % (datetime.datetime.now())
        self.UpdateCurrentTemp()
        self.UpdateTargetTemp()
        self.UpdateMode()
        self.UpdateWhatsOn()
        self.ticks_since_interaction += 1
        if self.ticks_since_interaction > 20:
            self.GoBack()
        
    #################################################################### 
    def OnModeHeat(self, evt):
    #################################################################### 
        print "OnModeHeat"
        self.SubmitMode("heat")
        self.reset_timeout()

    #################################################################### 
    def OnModeCool(self, evt):
    #################################################################### 
        self.SubmitMode("cool")
        self.reset_timeout()
    
    #################################################################### 
    def OnModeOff(self, evt):
    #################################################################### 
        self.SubmitMode("off")
        self.reset_timeout()

    #################################################################### 
    def OnModeAway(self, evt):
    #################################################################### 
        self.SubmitMode("away")
        self.reset_timeout()

    #################################################################### 
    def OnBnJon(self, evt):
    #################################################################### 
        self.pnMain.Hide()
        self.pnJon.Show()
        self.Layout()
        self.reset_timeout()

    #################################################################### 
    def OnBnGretch(self, evt):
    #################################################################### 
        self.pnMain.Hide()
        self.pnGretch.Show()
        self.Layout()
        self.reset_timeout()

    #################################################################### 
    def OnBnBack(self, evt):
    #################################################################### 
        self.GoBack()

    #################################################################### 
    def GoBack(self):
    #################################################################### 
        self.pnMain.Show()
        self.pnJon.Hide()
        self.pnGretch.Hide()
        self.Layout()
        self.reset_timeout()

    #################################################################### 
    def OnBnUp(self, evt):
    #################################################################### 
       self.setpt += 1
       self.UpdateSetpoint()
       self.reset_timeout()

    #################################################################### 
    def OnBnDown(self, evt):
    #################################################################### 
       self.setpt -= 1
       self.UpdateSetpoint()
       self.reset_timeout()

    #################################################################### 
    def UpdateSetpoint(self):
    #################################################################### 
       self.pnJon.lTargTmp.SetLabel("Target: %d" % self.setpt)
       self.pnGretch.lTargTmp.SetLabel("Target: %d" % self.setpt)
       self.SubmitTemp(self.setpt)
       self.pnStat.updateTarg(self.setpt)

    #################################################################### 
    def SubmitTemp(self, setTmp):
    #################################################################### 
        print "SubmitTemp"
        try:
            r = requests.get(url + "/_setTarget/%0.1f" % float(setTmp))
        except:
            print "submit temp failed"
            return -1
        return (r)

    #################################################################### 
    def SubmitMode(self, mode):
    #################################################################### 
        print "SubmitMode"
        try:
            r = requests.get(url + "/_setMode/%s" % mode)
        except:
            print "submit mode failed"
            return -1
        return (r)

    #################################################################### 
    def GetCurrentTemp(self):
    #################################################################### 
       try:
           r = requests.get(url + "/_liveTemp")
       except:
           print "live temp request failed"
           return -1

       return float(r.content)
       
    #################################################################### 
    def UpdateCurrentTemp(self):
    #################################################################### 
       temp = self.GetCurrentTemp()
       self.pnStat.updateCurrent( temp )
       self.pnJon.lCurTmp.SetLabel("Current: %d" % temp)
       self.pnGretch.lCurTmp.SetLabel("Current: %d" % temp)


    #################################################################### 
    def GetTargetTemp(self):
    #################################################################### 
       try:
           r = requests.get(url + "/_liveTargetTemp")
       except:
           print "live target temp request failed"
           return -1

       return float(r.content)

    #################################################################### 
    def UpdateTargetTemp(self):
    #################################################################### 
       temp = self.GetTargetTemp()
       self.pnStat.updateTarg( temp )
       self.pnJon.lTargTmp.SetLabel("Target: %d" % temp)
       self.pnGretch.lTargTmp.SetLabel("Target: %d" % temp)

    #################################################################### 
    def GetMode(self):
    #################################################################### 
       try:
           r = requests.get(url + "/_liveMode")
       except:
           print "live mode request failed"
           return -1

       return r.content

    #################################################################### 
    def UpdateMode(self, mode=None):
    #################################################################### 
        if mode == None:
           mode = self.GetMode()
        print "update mode: %s " % str(mode)

        if mode == "cool":
            self.pnStat.lblMode.SetForegroundColour( "#0000FF" )
        elif mode == "heat":
            self.pnStat.lblMode.SetForegroundColour( "#FF0000")
        else:
            self.pnStat.lblMode.SetForegroundColour( "#000000")

        self.pnStat.updateMode( mode )
        self.pnJon.updateMode( mode )
        self.pnGretch.updateMode( mode )


    #################################################################### 
    def GetWhatsOn(self):
    #################################################################### 
       try:
           r = requests.get(url + "/_liveWhatsOn")
       except:
           print "live mode request failed"
           return -1
       heat = re.findall("heat (\w+)", r.content)[0]
       cool = re.findall("cool (\w+)", r.content)[0]
       fan = re.findall("fan (\w+)", r.content)[0]
       return (heat,cool,fan)

    #################################################################### 
    def UpdateWhatsOn(self):
    #################################################################### 
       heat, cool, fan = self.GetWhatsOn()
       self.pnStat.updateWhatsOn( heat=heat, cool=cool, fan=fan)
       
####################################################################################
####################################################################################
if __name__ == '__main__':
####################################################################################
####################################################################################
   app = wx.App(False)
   frame = MainFrame()
   frame.ShowFullScreen(True, style=wx.FULLSCREEN_ALL)
   app.MainLoop()

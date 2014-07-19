#!/usr/bin/python

import wx
from wx.lib.wordwrap import wordwrap
import requests
import re

url = "http://localhost:80"

class PanelMain(wx.Panel):
   
   def __init__(self, parent):
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



class PanelJon(wx.Panel):
   def __init__(self, parent):
        #### Jon's panel ######
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

        self.sizerJonVR = wx.BoxSizer(wx.VERTICAL)
        self.sizerJonVR.Add(self.lTargTmp, 1, wx.EXPAND)
        self.sizerJonVR.Add(self.lCurTmp, 1, wx.EXPAND)
        self.sizerJonVR.Add(self.bnBack, 1, wx.EXPAND)
        
        self.sizerJonH.Add(self.sizerJonVL, 1, wx.EXPAND)
        self.sizerJonH.Add(self.sizerJonVR, 1, wx.EXPAND)

        self.SetSizer(self.sizerJonH)
        self.sizerJonVR.Fit(self)
        self.sizerJonVL.Fit(self)
        self.sizerJonH.Fit(self)

class PanelStatus(wx.Panel):
   def __init__(self, parent):
        wx.Panel.__init__(self,parent=parent, style=wx.SUNKEN_BORDER)
        self.sizerH = wx.BoxSizer(wx.HORIZONTAL)
        self.lblCurrent = wx.StaticText(self, -1, "C:xxx ")
        self.lblTarg = wx.StaticText(self, -1, "S:xxx ")
        self.lblMode = wx.StaticText(self, -1, "M:xxxx ")
        self.lblWhatsOn = wx.StaticText(self, -1, "H:xxx C:xxx F:xxx ")
        self.sizerH.Add(self.lblCurrent)
        self.sizerH.Add(self.lblTarg)
        self.sizerH.Add(self.lblMode)
        self.sizerH.Add(self.lblWhatsOn)
        self.SetSizer(self.sizerH)
        self.sizerH.Fit(self)
   def updateTarg(self, setTmp):
        self.lblTarg.SetLabel("T:%d" % setTmp)
        self.Layout()
   def updateCurrent(self, curTmp):
        self.lblCurrent.SetLabel("C:%d " % curTmp)
   def updateMode(self, mode):
        self.lblMode.SetLabel("M:%s " % mode)
   def updateWhatsOn(self, heat, cool, fan):
        self.lblWhatsOn.SetLabel("H:%s C:%s F:%s " % (heat, cool, fan))

class PanelGretch(wx.Panel):
   def __init__(self, parent):
        #### 's panel ######
        wx.Panel.__init__(self,parent=parent)

        self.sizerH = wx.BoxSizer(wx.HORIZONTAL)
        self.lTargTmp = wx.StaticText(self, -1, "Target: 70")
        self.lCurTmp = wx.StaticText(self, -1, "Current: 70")
        self.lTargTmp.SetFont(wx.Font(20, wx.DEFAULT, wx.BOLD, wx.NORMAL))
        self.lCurTmp.SetFont(wx.Font(20, wx.DEFAULT, wx.BOLD, wx.NORMAL))

        self.bnUp = wx.Button(self, -1, "I'm cold", (150,150))
        self.bnDown = wx.Button(self, -1, "I'm hot", (150,150))
        self.bnBack = wx.Button(self, -1, "Back", (150,150))

        self.sizerVL = wx.BoxSizer(wx.VERTICAL)
        self.sizerVL.Add(self.bnUp, 1, wx.EXPAND )
        self.sizerVL.Add(self.bnDown, 1, wx.EXPAND)

        self.bnUp.SetFont(wx.Font(25, wx.DEFAULT, wx.BOLD, wx.NORMAL))
        self.bnDown.SetFont(wx.Font(25, wx.DEFAULT, wx.BOLD, wx.NORMAL))
        self.bnBack.SetFont(wx.Font(25, wx.DEFAULT, wx.BOLD, wx.NORMAL))

        self.Bind(wx.EVT_BUTTON, parent.OnBnUp, self.bnUp)
        self.Bind(wx.EVT_BUTTON, parent.OnBnDown, self.bnDown)
        self.Bind(wx.EVT_BUTTON, parent.OnBnBack, self.bnBack)

        self.sizerVR = wx.BoxSizer(wx.VERTICAL)
        self.sizerVR.Add(self.lTargTmp, 1, wx.EXPAND)
        self.sizerVR.Add(self.lCurTmp, 1, wx.EXPAND)
        self.sizerVR.Add(self.bnBack, 1, wx.EXPAND)
        
        self.sizerH.Add(self.sizerVL, 1, wx.EXPAND)
        self.sizerH.Add(self.sizerVR, 1, wx.EXPAND)

        self.SetSizer(self.sizerH)
        self.sizerVR.Fit(self)
        self.sizerVL.Fit(self)
        self.sizerH.Fit(self)
        self.SetAutoLayout(1)
   

class MainFrame(wx.Frame):
   def __init__(self, redirect=False, filename=None):
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
   def on_timer(self, evt):
        print "tick"
        self.UpdateCurrentTemp()
        self.UpdateTargetTemp()
        self.UpdateMode()
        self.UpdateWhatsOn()

   def OnBnJon(self, evt):
        self.pnMain.Hide()
        self.pnJon.Show()
        self.Layout()

   def OnBnGretch(self, evt):
        self.pnMain.Hide()
        self.pnGretch.Show()
        self.Layout()

   def OnBnBack(self, evt):
        self.pnMain.Show()
        self.pnJon.Hide()
        self.pnGretch.Hide()
        self.Layout()

   def OnBnUp(self, evt):
       self.setpt += 1
       self.UpdateSetpoint()

   def OnBnDown(self, evt):
       self.setpt -= 1
       self.UpdateSetpoint()

   def UpdateSetpoint(self):
       self.pnJon.lTargTmp.SetLabel("Target: %d" % self.setpt)
       self.pnGretch.lTargTmp.SetLabel("Target: %d" % self.setpt)
       self.SubmitTemp(self.setpt, True)
       self.pnStat.updateTarg(self.setpt)

   def SubmitTemp(self, setTmp, cool):
       if cool:
          payload = {'target':str(setTmp), 'onoffswitch':cool}
       else:
          payload = {'target':str(setTmp)}

       try:
           r = requests.post(url, payload)
       except:
           print "submit temp request failed"
           return -1

   def GetCurrentTemp(self):
       try:
           r = requests.get(url + "/_liveTemp")
       except:
           print "live temp request failed"
           return -1

       return float(r.content)
       
   def UpdateCurrentTemp(self):
       temp = self.GetCurrentTemp()
       self.pnStat.updateCurrent( temp )
       self.pnJon.lCurTmp.SetLabel("Current: %d" % temp)
       self.pnGretch.lCurTmp.SetLabel("Current: %d" % temp)

   def GetTargetTemp(self):
       try:
           r = requests.get(url + "/_liveTargetTemp")
       except:
           print "live target temp request failed"
           return -1

       return float(r.content)

   def UpdateTargetTemp(self):
       temp = self.GetTargetTemp()
       self.pnStat.updateTarg( temp )
       self.pnJon.lTargTmp.SetLabel("Target: %d" % temp)
       self.pnGretch.lTargTmp.SetLabel("Target: %d" % temp)

   def GetMode(self):
       try:
           r = requests.get(url + "/_liveMode")
       except:
           print "live mode request failed"
           return -1

       return r.content

   def UpdateMode(self):
       mode = self.GetMode()
       self.pnStat.updateMode( mode )

   def GetWhatsOn(self):
       try:
           r = requests.get(url + "/_liveWhatsOn")
       except:
           print "live mode request failed"
           return -1
       heat = re.findall("heat (\w+)", r.content)[0]
       cool = re.findall("cool (\w+)", r.content)[0]
       fan = re.findall("fan (\w+)", r.content)[0]
       return (heat,cool,fan)

   def UpdateWhatsOn(self):
       heat, cool, fan = self.GetWhatsOn()
       self.pnStat.updateWhatsOn( heat=heat, cool=cool, fan=fan)
       
if __name__ == '__main__':
   app = wx.App(False)
   frame = MainFrame()
   frame.ShowFullScreen(True, style=wx.FULLSCREEN_ALL)
   app.MainLoop()

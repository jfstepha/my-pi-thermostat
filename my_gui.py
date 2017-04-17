#!/usr/bin/python

import wx
from wx.lib.wordwrap import wordwrap
import requests
import re
import datetime
import random
import time
import inspect

url = "http://localhost:80"
MAX_TEMP_SET = 99
MIN_TEMP_SET = 1

# these are just the integer part
STATE_NO_SENSOR =    0
STATE_DAY_IDLE =     1
STATE_DAY_MOTION =   2
STATE_DAY_AWAY =     3
STATE_DAY_ACTIVE =   4
STATE_NIGHT_IDLE =   5
STATE_NIGHT_MOTION = 6
STATE_NIGHT_AWAY =   7
STATE_NIGHT_ACTIVE = 8

####################################################################################
####################################################################################
class PanelScreenSaver(wx.Panel):
####################################################################################
####################################################################################

   #################################################################### 
   def __init__(self, parent):
   #################################################################### 
        #### MAIN panel ######
        wx.Panel.__init__(self,parent=parent)
        self.parent = parent
        self.temp_x = 20
        self.temp_y = 20
        self.temp_xmax = 200
        self.temp_ymax = 100
        self.minspeed = 0.1
        self.maxspeed = 1
        self.temp_xdir = self.GetRandDir()
        self.temp_ydir = self.GetRandDir()
        self.bgr = 240
        self.bgg = 0
        self.bgb = 0
        self.colorstep = 1

        self.lblTemp = wx.StaticText(self,label="Starting...", pos=(20,20))
        font = wx.Font( 30, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.lblTemp.SetFont( font )

        self.lblStatus = wx.StaticText(self,label="Starting...", pos=(20,90))
        font = wx.Font( 10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.lblStatus.SetFont( font )


        self.SetBackgroundColour( (self.bgr, self.bgg, self.bgb))
        self.lblTemp.SetForegroundColour( "#FFFFFF")
        self.lblStatus.SetForegroundColour( "#FFFFFF")
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        self.lblTemp.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        self.lblStatus.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        
        self.temp = 0
   #################################################################### 
   def OnClick(self, evt):
   #################################################################### 
        self.parent.ShowMain()
        
   #################################################################### 
   def GetRandDir(self):
   #################################################################### 
        retval = random.random() * self.maxspeed * 2 - self.maxspeed
        if retval < self.minspeed and retval >= 0:
            retval = self.minspeed
        if retval > -self.minspeed and retval < 0:
            retval = -self.minspeed 
        return retval
    
        
   #################################################################### 
   def Update(self):
   #################################################################### 
        self.temp_x += self.temp_xdir
        if self.temp_x > self.temp_xmax:
            self.temp_x = self.temp_xmax
            self.temp_xdir = self.GetRandDir()
        if self.temp_x < 0:
            self.temp_x = 0
            self.temp_xdir = self.GetRandDir()
            

        self.temp_y += self.temp_ydir
        if self.temp_y > self.temp_ymax:
            self.temp_y = self.temp_ymax 
            self.temp_ydir = self.GetRandDir()
        if self.temp_y < 0:
            self.temp_y = 0
            self.temp_ydir = self.GetRandDir()
        
        self.lblTemp.SetPosition((self.temp_x, self.temp_y))
        self.lblStatus.SetPosition((self.temp_x+10, self.temp_y+90))
        print "position: %d, %d" % (self.temp_x, self.temp_y)
        self.bgr += self.colorstep
        if self.bgr > 255:
            self.bgr = 0
            self.bgg += self.colorstep
        if self.bgg > 255:
            self.bgg = 0
            self.bgb += self.colorstep
        if self.bgb > 255:
            self.bgb = 0
        if (self.bgr + self.bgg + self.bgb) > 1024:
            self.lblTemp.SetForegroundColour( "#000000")
            self.lblStatus.SetForegroundColour( "#000000")
        else:
            self.lblTemp.SetForegroundColour( "#FFFFFF")
            self.lblStatus.SetForegroundColour( "#FFFFFF")
        self.SetBackgroundColour( (self.bgr, self.bgg, self.bgb))
        if self.IsShown():
            self.Refresh()

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
        self.bnModeInUse = wx.ToggleButton( self, -1, "InUse" )
        self.bnModeSmart = wx.ToggleButton( self, -1, "Smart" )
        
        self.bnModeHeat.SetBackgroundColour( "#FFDDDD" )
        self.bnModeCool.SetBackgroundColour( "#DDDDFF" )
        
        self.Bind(wx.EVT_TOGGLEBUTTON, parent.OnModeHeat, self.bnModeHeat)
        self.Bind(wx.EVT_TOGGLEBUTTON, parent.OnModeCool, self.bnModeCool)
        self.Bind(wx.EVT_TOGGLEBUTTON, parent.OnModeOff, self.bnModeOff)
        self.Bind(wx.EVT_TOGGLEBUTTON, parent.OnModeAway, self.bnModeAway)
        self.Bind(wx.EVT_TOGGLEBUTTON, parent.OnModeInUse, self.bnModeInUse)
        self.Bind(wx.EVT_TOGGLEBUTTON, parent.OnModeSmart, self.bnModeSmart)

        self.sizerModeV = wx.BoxSizer( wx.VERTICAL )
        self.sizerModeHT = wx.BoxSizer( wx.HORIZONTAL)
        self.sizerModeHB = wx.BoxSizer( wx.HORIZONTAL )
        self.sizerModeHC = wx.BoxSizer( wx.HORIZONTAL )
       
        self.sizerModeHT.Add( self.bnModeHeat, 1, wx.EXPAND )
        self.sizerModeHT.Add( self.bnModeCool, 1, wx.EXPAND )
        self.sizerModeHC.Add( self.bnModeSmart, 1, wx.EXPAND )
        self.sizerModeHC.Add( self.bnModeOff, 1, wx.EXPAND )
        self.sizerModeHB.Add( self.bnModeAway, 1, wx.EXPAND )
        self.sizerModeHB.Add( self.bnModeInUse, 1, wx.EXPAND )
        self.sizerModeV.Add( self.sizerModeHT, 1, wx.EXPAND)
        self.sizerModeV.Add( self.sizerModeHC, 1, wx.EXPAND)
        #self.sizerModeV.Add( self.sizerModeHB, 1, wx.EXPAND)

        self.sizerJonVL = wx.BoxSizer(wx.VERTICAL)
        self.sizerJonVL.Add(self.bnUp, 1, wx.EXPAND )
        self.sizerJonVL.Add(self.bnDown, 1, wx.EXPAND)
        self.sizerJonVL.Add(self.sizerModeHB, 1, wx.EXPAND)

        self.sizerJonVR = wx.BoxSizer(wx.VERTICAL)
        self.sizerJonVR.Add(self.lTargTmp, 1, wx.EXPAND)
        self.sizerJonVR.Add(self.lCurTmp, 1, wx.EXPAND)
        self.sizerJonVR.Add(self.sizerModeHT, 1, wx.EXPAND)
        #self.sizerJonVR.Add(self.sizerModeHB, 1, wx.EXPAND)
        self.sizerJonVR.Add(self.sizerModeHC, 1, wx.EXPAND)
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
        self.lblLSM = wx.StaticText(self, -1, "M:xxxxx")
        self.lblSMStr = wx.StaticText(self, -1, "xxxxx")
        
        font = wx.Font( 8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.lblCurrent.SetFont( font )
        self.lblTarg.SetFont(font)
        self.lblMode.SetFont(font)
        self.lblHOn.SetFont(font)
        self.lblCOn.SetFont(font)
        self.lblFOn.SetFont(font)
        self.lblLSM.SetFont(font)
        self.lblSMStr.SetFont(font)

        self.sizerH.Add(self.lblCurrent)
        self.sizerH.Add(self.lblTarg)
        self.sizerH.Add(self.lblMode)
        self.sizerH.Add(self.lblHOn)
        self.sizerH.Add(self.lblCOn)
        self.sizerH.Add(self.lblFOn)
        self.sizerH.Add(self.lblLSM)
        self.sizerH.Add(self.lblSMStr)
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
   def updateWhatsOn(self, heat, cool, fan, lsm, smartmodestring):
   #################################################################### 
        #self.lblWhatsOn.SetLabel("H:%s C:%s F:%s " % (heat, cool, fan))
        self.lblHOn.SetLabel("H:%s " % heat)
        self.lblCOn.SetLabel("C:%s " % cool)
        self.lblFOn.SetLabel("F:%s " % fan)
        self.lblLSM.SetLabel("M:%s " % lsm)
        self.lblSMStr.SetLabel("%s" % smartmodestring)

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
        self.timer.Start(3000)

        ### Common controls ####
        self.sizerH = wx.BoxSizer(wx.HORIZONTAL)
        self.sizerV = wx.BoxSizer(wx.VERTICAL)

        self.pnMain = PanelMain(self)
        self.pnJon = PanelJon(self)
        self.pnGretch = PanelGretch(self)
        self.pnStat = PanelStatus(self)
        self.pnScrenSaver = PanelScreenSaver(self)

        self.sizerH.Add(self.pnMain, 1, wx.EXPAND)
        self.sizerH.Add(self.pnJon, 1, wx.EXPAND)
        self.sizerH.Add(self.pnGretch, 1, wx.EXPAND)
        self.sizerH.Add(self.pnScrenSaver,1,wx.EXPAND)
        self.sizerV.Add(self.sizerH, 1, wx.EXPAND)
        self.sizerV.Add(self.pnStat,0)

        self.pnJon.Hide()
        self.pnGretch.Hide()
        self.pnMain.Hide()
        self.pnStat.Hide()
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
        self.UpdateSmartButtons()
        self.pnScrenSaver.Update()
        self.ticks_since_interaction += 1
        if self.ticks_since_interaction > 80:
            self.ShowScreenSaver()

        
    #################################################################### 
    def OnModeHeat(self, evt):
    #################################################################### 
        print "[%s] OnModeHeat" % (datetime.datetime.now())
        self.SubmitMode("heat")
        self.reset_timeout()

    #################################################################### 
    def OnModeCool(self, evt):
    #################################################################### 
        print "[%s] OnModeCool" % (datetime.datetime.now())
        self.SubmitMode("cool")
        self.reset_timeout()
    
    #################################################################### 
    def OnModeOff(self, evt):
    #################################################################### 
        print "[%s] OnModeOff" % (datetime.datetime.now())
        self.SubmitMode("off")
        self.reset_timeout()

    #################################################################### 
    def OnModeAway(self, evt):
    #################################################################### 
        print "[%s] OnModeAway" % (datetime.datetime.now())
        self.SubmitSmartMode("away")
        self.reset_timeout()

    #################################################################### 
    def OnModeSmart(self, evt):
    #################################################################### 
        print "[%s] OnModeSmart" % (datetime.datetime.now())
        self.SubmitSmartMode("smart")
        self.reset_timeout()

    #################################################################### 
    def OnModeInUse(self, evt):
    #################################################################### 
        print "[%s] OnModeInUse" % (datetime.datetime.now())
        self.SubmitSmartMode("inuse")
        self.reset_timeout()

    #################################################################### 
    def OnBnJon(self, evt):
    #################################################################### 
        print "[%s] OnModeBnJon" % (datetime.datetime.now())
        self.pnMain.Hide()
        self.pnJon.Show()
        self.Layout()
        self.reset_timeout()

    #################################################################### 
    def OnBnGretch(self, evt):
    #################################################################### 
        print "[%s] OnModeBnGretch" % (datetime.datetime.now())
        self.pnMain.Hide()
        self.pnGretch.Show()
        self.Layout()
        self.reset_timeout()

    #################################################################### 
    def OnBnBack(self, evt):
    #################################################################### 
        print "[%s] OnModeBnBack" % (datetime.datetime.now())
        self.ShowMain()

    #################################################################### 
    def ShowMain(self):
    #################################################################### 
        self.pnMain.Show()
        self.pnJon.Hide()
        self.pnGretch.Hide()
        self.pnScrenSaver.Hide()
        self.pnStat.Show()
        self.Layout()
        self.reset_timeout()

    #################################################################### 
    def ShowScreenSaver(self):
    #################################################################### 
        self.pnMain.Hide()
        self.pnJon.Hide()
        self.pnGretch.Hide()
        self.pnScrenSaver.Show()
        self.pnStat.Hide()
        self.Layout()
        self.reset_timeout()
        self.WarpPointer(240,340)

    #################################################################### 
    def OnBnUp(self, evt):
    #################################################################### 
        print "[%s] OnModeBnUp current sp %d" % (datetime.datetime.now(), self.setpt)
        self.UpdateTargetTemp()
        self.UserChangeSetptSmart() # force us into motion mode
        print("Current setpt: %0.2f" % self.setpt)
        self.setpt += 1
        if self.setpt > MAX_TEMP_SET:
            self.setpt = MAX_TEMP_SET
        self.UpdateSetpoint()
        self.reset_timeout()

    #################################################################### 
    def OnBnDown(self, evt):
    #################################################################### 
        print "[%s] OBnDown current sp %d" % (datetime.datetime.now(), self.setpt)
        self.UpdateTargetTemp()
        self.UserChangeSetptSmart() # force us into motion mode
        print "[%s] OBnDown after UserChangeSetpt: %d" % (datetime.datetime.now(), self.setpt)
        self.setpt -= 1
        print "[%s] OBnDown after decreasing sp: %d" % (datetime.datetime.now(), self.setpt)
        if self.setpt < MIN_TEMP_SET:
             self.setpt = MIN_TEMP_SET
        self.UpdateSetpoint()
        self.reset_timeout()
    
    #################################################################### 
    def UserChangeSetptSmart(self):
        ''' Get out of any override or idle states when a user clicks 
            a temperature change button '''
    #################################################################### 
        mode = self.GetSmartState()
        print("UserChangeSetptSmart current mode: %d" % mode)
        if mode in [STATE_DAY_AWAY, STATE_DAY_IDLE, STATE_NIGHT_AWAY, STATE_NIGHT_ACTIVE]:
            print("UserChangeSetptSmart overriding motion and setting mode")
            self.MotionOverride()
            self.SubmitSmartMode( "smart" )
            a = self.GetActiveTargetTemp()  # need to refresh setpt as the smart setpt
            print("got active temp of %0.1f"%a)
            self.setpt = a
        
    #################################################################### 
    def MotionOverride(self):
        ''' Trick the system into thinking motion has occurred through the motionoverride file'''
    #################################################################### 
        f = open('/dev/shm/motionoverride','w')
        f.write("\n" )
        f.close()
        

    #################################################################### 
    def UpdateSetpoint(self):
    #################################################################### 
       print "[%s] UpdateSetpoint" % (datetime.datetime.now())
       curframe = inspect.currentframe()
       calframe = inspect.getouterframes(curframe, 2)
       print "[%s]   caller: %s" % (datetime.datetime.now(), calframe[1][3])
       # self.UpdateTargetTemp()  this was getting the current temp from the web server again, overwriting
       self.UserChangeSetptSmart() # force us into motion mode
       print("Current setpt: %0.2f" % self.setpt)

       self.pnJon.lTargTmp.SetLabel("Target: %d" % self.setpt)
       self.pnGretch.lTargTmp.SetLabel("Target: %d" % self.setpt)
       self.SubmitTemp(self.setpt)
       self.SubmitActiveTemp(self.setpt)
       self.pnStat.updateTarg(self.setpt)

    #################################################################### 
    def SubmitActiveTemp(self, setTmp):
    #################################################################### 
        print "SubmitActiveTemp"
        try:
            current_mode = self.GetSmartState()
            if current_mode > 4:
                r = requests.get(url + "/_setTargetNightActive/%0.1f" % float(setTmp))
            else:
                r = requests.get(url + "/_setTargetDayActive/%0.1f" % float(setTmp))
        except KeyboardInterrupt:
            print "Keyboard interrupt"
            exit()
        except:
            print "submit temp failed"
            return -1

        return (r)

    #################################################################### 
    def SubmitTemp(self, setTmp):
    #################################################################### 
        print "[%s] SubmitTemp %d" % (datetime.datetime.now(), setTmp)
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        print "[%s]   caller: %s" % (datetime.datetime.now(), calframe[1][3])
        try:
            r = requests.get(url + "/_setTarget/%0.1f" % float(setTmp))
        except KeyboardInterrupt:
            print "Keyboard interrupt"
            exit()
        except:
            print "submit temp failed"
            return -1

        return (r)

    #################################################################### 
    def SubmitSmartMode(self, mode):
    #################################################################### 
        print "SubmitSmartMode"
        current_mode = self.GetSmartState()
        if mode == "away":
            if current_mode < 5: # if it's day
                state = STATE_DAY_AWAY
            else:
                state = STATE_NIGHT_AWAY
        elif mode == "inuse":
            if current_mode < 5:
                state = STATE_DAY_ACTIVE
            else:
                state = STATE_DAY_ACTIVE
        elif mode == "smart":  
            if current_mode < 5:
                state = STATE_DAY_MOTION
            else:
                state = STATE_NIGHT_MOTION
        else:
            print "ERROR: mode %s not valid" % mode
        try:
            r = requests.get(url + "/_setSmartState/%s" % state)
        except KeyboardInterrupt:
            print "Keyboard interrupt"
            exit()
        except:
            print "submit mode failed"
            return -1
        return (r)

    #################################################################### 
    def SubmitMode(self, mode):
    #################################################################### 
        print "SubmitMode"
        try:
            r = requests.get(url + "/_setMode/%s" % mode)
        except KeyboardInterrupt:
            print "Keyboard interrupt"
            exit()
        except:
            print "submit mode failed"
            return -1
        return (r)

    #################################################################### 
    def GetCurrentTemp(self):
    #################################################################### 
       try:
           r = requests.get(url + "/_liveTemp")
       except KeyboardInterrupt:
            print "Keyboard interrupt"
            exit()
       except:
           print "live temp request failed"
           return -1

       return float(r.content)
       
    #################################################################### 
    def UpdateCurrentTemp(self):
    #################################################################### 
       temp = self.GetCurrentTemp()
       targ = self.GetTargetTemp()
       statestr = self.GetSmartStateString()
       orr = self.GetOverrideRemaining()
       whatson = self.GetWhatsOn()
       lsm = self.GetLSM()

       self.pnStat.updateCurrent( temp )
       self.pnJon.lCurTmp.SetLabel("Current: %d" % temp)
       self.pnGretch.lCurTmp.SetLabel("Current: %d" % temp)
#       self.pnScrenSaver.lblTemp.SetLabel("%0.1f\nT: %0.1f" % (temp, self.setpt))
       now = datetime.datetime.now()
       if now.hour > 11:
           ampm = "pm"
       else:
           ampm = "am"
       if now.hour > 12:
           h = now.hour - 12
       else:
           h = now.hour
       if orr == 0:
           orstr = ""
       else:
           orstr = ":%0.2f min override" % orr
       t = "%d:%02d%s %d/%d/%d" % (h, now.minute, ampm, now.month, now.day, now.year)
       self.pnScrenSaver.lblTemp.SetLabel("%0.1f\nT: %0.1f" % (temp, targ))
       self.pnScrenSaver.lblStatus.SetLabel("%s\n%s%s\nheat:%s cool:%s fan:%s\nlast motion %ds ago" % (t, statestr,orstr, whatson[0], whatson[1],whatson[2],lsm))

    #################################################################### 
    def GetOverrideRemaining(self):
    #################################################################### 
       try:
           r = requests.get(url + "/_liveOverrideRemaining")
       except KeyboardInterrupt:
            print "Keyboard interrupt"
            exit()
       except:
           print "live override remaining request failed"
           return -1

       return float(r.content)


    #################################################################### 
    def GetActiveTargetTemp(self):
    #################################################################### 
       try:
           mode = self.GetSmartState()
           print("GetActiveTargetTemp got mode %d"  % mode)
           if mode > 4: # night
               r = requests.get(url + "/_liveTargetNightActive")
           else:
               r = requests.get(url + "/_liveTargetDayActive")
       except KeyboardInterrupt:
            print "Keyboard interrupt"
            exit()
       except:
           print "live target temp request failed"
           return -1

       return float(r.content)

    #################################################################### 
    def GetTargetTemp(self):
    #################################################################### 
       try:
           r = requests.get(url + "/_liveTargetTemp")
       except KeyboardInterrupt:
            print "Keyboard interrupt"
            exit()
       except:
           print "live target temp request failed"
           return -1

       print("GetTargetTemp got %0.2f" % float(r.content))
       return float(r.content)

    #################################################################### 
    def UpdateTargetTemp(self):
    #################################################################### 
       temp = self.GetTargetTemp()
       self.pnStat.updateTarg( temp )
       self.pnJon.lTargTmp.SetLabel("Target: %d" % temp)
       self.pnGretch.lTargTmp.SetLabel("Target: %d" % temp)
       self.setpt = temp

    #################################################################### 
    def UpdateSmartButtons(self):
    #################################################################### 
       #print("Updating smart buttons")
       orrem = self.GetOverrideRemaining()
       h = int( orrem / 60 )
       m = int( orrem % 60 )
       s = int( orrem * 60 ) % 60
       smartmode = self.GetSmartState()
       smartstr = self.GetSmartStateString()
       #print("orrem=%0.3f" % orrem)
       #print("smartmode=%d" % smartmode)
       fontsmall = wx.Font( 9, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
       fontlarge = wx.Font( 12, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
       if smartmode == STATE_DAY_AWAY or smartmode == STATE_NIGHT_AWAY: # away
           self.pnJon.bnModeAway.SetLabel( "Away %d:%02d" % (h, m))
           self.pnGretch.bnModeAway.SetLabel( "Away %d:%02d" % (h, m))
           self.pnJon.bnModeInUse.SetLabel( "In Use" )
           self.pnGretch.bnModeInUse.SetLabel( "In Use" )
           self.pnJon.bnModeSmart.SetLabel( "Smart(%s)" % smartstr )
           self.pnGretch.bnModeSmart.SetLabel( "Smart" )

           self.pnJon.bnModeAway.SetValue( True )
           self.pnJon.bnModeInUse.SetValue( False )
           self.pnJon.bnModeSmart.SetValue( False )
           self.pnGretch.bnModeAway.SetValue( True )
           self.pnGretch.bnModeInUse.SetValue( False )
           self.pnGretch.bnModeSmart.SetValue( False )

           self.pnJon.bnModeAway.SetFont(fontsmall)
           self.pnGretch.bnModeAway.SetFont(fontsmall)
           self.pnJon.bnModeInUse.SetFont(fontlarge)
           self.pnGretch.bnModeInUse.SetFont(fontlarge)
           self.pnJon.bnModeSmart.SetFont(fontsmall)
           self.pnGretch.bnModeSmart.SetFont(fontlarge)

       elif smartmode == STATE_DAY_ACTIVE or smartmode == STATE_DAY_ACTIVE: 
           self.pnJon.bnModeAway.SetLabel( "Away" )
           self.pnGretch.bnModeAway.SetLabel( "Away" )
           self.pnJon.bnModeInUse.SetLabel( "IU %d:%02d" % (h,m))
           self.pnGretch.bnModeInUse.SetLabel( "IU %d:%02d" % (h,m))
           self.pnJon.bnModeSmart.SetLabel( "Smt (%s)" % smartstr )
           self.pnGretch.bnModeSmart.SetLabel( "Smart" )
           self.pnJon.bnModeAway.SetValue( False)
           self.pnJon.bnModeInUse.SetValue( True )
           self.pnJon.bnModeSmart.SetValue( False )
           self.pnGretch.bnModeAway.SetValue( False )
           self.pnGretch.bnModeInUse.SetValue( True )
           self.pnGretch.bnModeSmart.SetValue( False )

           self.pnJon.bnModeAway.SetFont(fontlarge)
           self.pnGretch.bnModeAway.SetFont(fontlarge)
           self.pnJon.bnModeInUse.SetFont(fontsmall)
           self.pnGretch.bnModeInUse.SetFont(fontsmall)
           self.pnJon.bnModeSmart.SetFont(fontsmall)
           self.pnGretch.bnModeSmart.SetFont(fontlarge)

       else: # smart mode
           self.pnJon.bnModeAway.SetLabel( "Away" )
           self.pnGretch.bnModeAway.SetLabel( "Away" )
           self.pnJon.bnModeInUse.SetLabel( "InUse" )
           self.pnGretch.bnModeInUse.SetLabel( "InUse" )
           self.pnJon.bnModeSmart.SetLabel( "Smt(%s)" % smartstr )
           self.pnGretch.bnModeSmart.SetLabel( "Smart" )

           self.pnJon.bnModeAway.SetValue( False)
           self.pnJon.bnModeInUse.SetValue( False )
           self.pnJon.bnModeSmart.SetValue( True )
           self.pnGretch.bnModeAway.SetValue( False )
           self.pnGretch.bnModeInUse.SetValue( False )
           self.pnGretch.bnModeSmart.SetValue( True )

           self.pnJon.bnModeAway.SetFont(fontlarge)
           self.pnGretch.bnModeAway.SetFont(fontlarge)
           self.pnJon.bnModeInUse.SetFont(fontlarge)
           self.pnGretch.bnModeInUse.SetFont(fontlarge)
           self.pnJon.bnModeSmart.SetFont(fontsmall)
           self.pnGretch.bnModeSmart.SetFont(fontlarge)

    #################################################################### 
    def GetMode(self):
    #################################################################### 
       r = ""
       try:
           r = requests.get(url + "/_liveMode")
       except KeyboardInterrupt:
            print "Keyboard interrupt"
            exit()
       except:
           print "GetMode live mode request failed r:%s" %str(r)
           return -1

       return r.content

    #################################################################### 
    def GetSmartStateString(self):
    #################################################################### 
       r = ""
       try:
           r = requests.get(url + "/_liveSmartStateString")
       except KeyboardInterrupt:
            print "Keyboard interrupt"
            exit()
       except:
           print "GetSmartStateString live mode request failed r:%s" %str(r)
           return -1

       return r.content

    #################################################################### 
    def GetSmartState(self):
    #################################################################### 
       r = ""
       try:
           r = requests.get(url + "/_liveSmartState")
       except KeyboardInterrupt:
            print "Keyboard interrupt"
            exit()
       except:
           print "GetSmartState live mode request failed r:%s" %str(r)
           return -1

       return int(r.content)

    #################################################################### 
    def UpdateMode(self, mode=None):
    #################################################################### 
        if mode == None:
           mode = self.GetMode()
        #print "update mode: %s " % str(mode)

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
    def GetLSM(self):
    #################################################################### 
       try:
           r = requests.get(url + "/_liveMotion")
       except KeyboardInterrupt:
            print "Keyboard interrupt"
            exit()
       except:
           print "GetLSM live mode request failed"
           return -1
       return int(r.content)

    #################################################################### 
    def GetWhatsOn(self):
    #################################################################### 
       try:
           r = requests.get(url + "/_liveWhatsOn")
       except KeyboardInterrupt:
            print "Keyboard interrupt"
            exit()
       except:
           print "GetWhatsOn live mode request failed"
           return -1
       heat = re.findall("heat (\w+)", r.content)[0]
       cool = re.findall("cool (\w+)", r.content)[0]
       fan = re.findall("fan (\w+)", r.content)[0]
       return (heat,cool,fan)

    #################################################################### 
    def UpdateWhatsOn(self):
    #################################################################### 
       try:
           heat, cool, fan = self.GetWhatsOn()
           lsm = self.GetLSM()
           smartmodestring= self.GetSmartStateString()
           self.pnStat.updateWhatsOn( heat=heat, cool=cool, fan=fan, lsm=lsm, smartmodestring=smartmodestring)
       except KeyboardInterrupt:
            print "Keyboard interrupt"
            exit()
       except:
           print "UpdateWhatsOn live mode request failed"
           return -1
       
####################################################################################
####################################################################################
if __name__ == '__main__':
####################################################################################
####################################################################################
   app = wx.App(False)
   cursor = wx.StockCursor(wx.CURSOR_BLANK) 
   frame = MainFrame()
   frame.SetCursor(cursor) 
   frame.ShowFullScreen(True, style=wx.FULLSCREEN_ALL)
   app.MainLoop()

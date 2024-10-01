import wx

class ExpandablePanel(wx.Panel):
    def __init__(self, parent, color, position):
        super().__init__(parent)
        self.SetBackgroundColour(color)
        self.position = position
        self.main_frame = self.GetTopLevelParent()

        sizer = wx.BoxSizer(wx.VERTICAL)
        
        expand_left = wx.Button(self, label="Expand Left")
        expand_right = wx.Button(self, label="Expand Right")
        
        sizer.AddStretchSpacer(1)
        sizer.Add(expand_left, 0, wx.CENTER | wx.ALL, 5)
        sizer.Add(expand_right, 0, wx.CENTER | wx.ALL, 5)
        sizer.AddStretchSpacer(1)
        
        self.SetSizer(sizer)
        
        expand_left.Bind(wx.EVT_BUTTON, self.on_expand_left)
        expand_right.Bind(wx.EVT_BUTTON, self.on_expand_right)

    def on_expand_left(self, event):
        if self.position > 0:
            self.main_frame.adjust_proportions(self.position - 1, 1)
            self.main_frame.adjust_proportions(self.position, -1)

    def on_expand_right(self, event):
        if self.position < 2:
            self.main_frame.adjust_proportions(self.position, 1)
            self.main_frame.adjust_proportions(self.position + 1, -1)

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='3 Panels with Expand Buttons')
        
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.panels = [
            ExpandablePanel(self, wx.RED, 0),
            ExpandablePanel(self, wx.GREEN, 1),
            ExpandablePanel(self, wx.BLUE, 2)
        ]
        
        for panel in self.panels:
            self.main_sizer.Add(panel, 1, wx.EXPAND)
        
        self.SetSizer(self.main_sizer)
        self.SetInitialSize((800, 400))

    def adjust_proportions(self, panel_index, change):
        item = self.main_sizer.GetItem(self.panels[panel_index])
        current_proportion = item.GetProportion()
        new_proportion = max(1, current_proportion + change)
        item.SetProportion(new_proportion)
        self.main_sizer.Layout()

if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
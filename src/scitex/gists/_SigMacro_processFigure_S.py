def sigmacro_process_figure_s():
    """Print a macro for SigmaPlot (v12.0) to format a panel.
    
    Please refer to the 'Automating Routine Tasks' section of the official documentation.
    """
    print(
        """
Option Explicit

' Constants for FLAG_SET_BIT and FLAG_CLEAR_BIT should be defined
Const FLAG_SET_BIT As Long = 1 ' Assuming value, replace with actual value
Const FLAG_CLEAR_BIT As Long = 0 ' Assuming value, replace with actual value

' Function to set option flag bits on
Function FlagOn(flag As Long) As Long
    FlagOn = flag Or FLAG_SET_BIT
End Function

' Function to set option flag bits off
Function FlagOff(flag As Long) As Long
    FlagOff = flag And Not FLAG_CLEAR_BIT
End Function

' Procedure to set the title size to 8 points
Sub setTitleSize()
    ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_GRAPH).NameObject.SetObjectCurrent
    ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETOBJECTATTR, STA_SIZE, "111") ' Size set to 8 points
End Sub

' Procedure to set label size for a given dimension to 8 points
Sub setLabelSize(dimension)
    ' ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_GRAPH).NameObject.SetObjectCurrent
    ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_AXIS).NameObject.SetObjectCurrent
    ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETPLOTATTR, SLA_SELECTDIM, dimension)
    ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETOBJECTATTR, STA_SIZE, "111") ' Size set to 8 points
End Sub

' Procedure to set tick label size for a given dimension to 7 points
Sub setTickLabelSize(dimension)
    ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_GRAPH).NameObject.SetObjectCurrent
    ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETPLOTATTR, SLA_SELECTDIM, dimension)
    ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_AXIS).TickLabelAttributes(SAA_LINE_MAJORTIC).SetObjectCurrent
    ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETOBJECTATTR, STA_SIZE, "97") ' Size set to 7 points
End Sub

' Procedure to process tick settings for a given dimension
Sub processTicks(dimension)
    ' Ensure the object is correctly targeted before setting attributes
    ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_AXIS).NameObject.SetObjectCurrent
    ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETPLOTATTR, SLA_SELECTDIM, dimension)
    ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETAXISATTR, SAA_SELECTLINE, 1)
    ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETAXISATTR, SEA_THICKNESS, &H00000008)
    ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETAXISATTR, SAA_TICSIZE, &H00000020)
    ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETAXISATTR, SAA_SELECTLINE, 2)
    ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETAXISATTR, SEA_THICKNESS, &H00000008)
    ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETAXISATTR, SAA_TICSIZE, &H00000020)    
End Sub

' Procedure to remove an axis for a given dimension
Sub removeAxis(dimension)
    ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETPLOTATTR, SLA_SELECTDIM, dimension)
    ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETAXISATTR, SAA_SUB2OPTIONS, &H00000000)
End Sub

Sub resizeFigure
	ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_GRAPH).NameObject.SetObjectCurrent
    With ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_GRAPH)
	'.Top = 0
	'.Left = 0
	.Width = &H000004F5&
	.Height = &H00000378&
	End With
End Sub

' Main procedure
Sub Main()
    Dim FullPATH As String
    Dim OrigPageName As String
    Dim ObjectType As String
    Dim COLOR As Long
    
    ' Saves the original page to jump back
    FullPATH = ActiveDocument.FullName
    OrigPageName = ActiveDocument.CurrentPageItem.Name
    ActiveDocument.NotebookItems(OrigPageName).IsCurrentBrowserEntry = True

	' Code to set the figure size should be implemented here    
    resizeFigure

    ' Set the title sizes
    setTitleSize

    ' Set the sizes of X/Y labels
    setLabelSize(1) ' X-axis
    setLabelSize(2) ' Y-axis
    
    ' Set the sizes of X/Y tick labels
    setTickLabelSize(1) ' X-axis
    setTickLabelSize(2) ' Y-axis

    ' Set tick length and width
    processTicks(1) ' X-axis
    processTicks(2) ' Y-axis
    
    ' Remove right and top axes
    removeAxis(1) ' Right axis
    removeAxis(2) ' Top axis
    
    ' Go back to the original page
	Notebooks(FullPATH).NotebookItems(OrigPageName).Open
 
End Sub
    """
    )


# Backward compatibility alias
import warnings


def SigMacro_processFigure_S():
    """Deprecated: Use sigmacro_process_figure_s() instead."""
    warnings.warn(
        "SigMacro_processFigure_S is deprecated, use sigmacro_process_figure_s() instead",
        DeprecationWarning,
        stacklevel=2
    )
    return sigmacro_process_figure_s()

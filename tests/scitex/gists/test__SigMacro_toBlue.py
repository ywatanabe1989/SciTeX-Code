# Add your tests here

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/gists/_SigMacro_toBlue.py
# --------------------------------------------------------------------------------
# def SigMacro_toBlue():
#     """Print a macro for SigmaPlot (v12.0) that changes the color and style of the selected object. Please refer to the 'Automating Routine Tasks' section of the official documentation."""
#     print(
#         """
# Option Explicit
#
# Function FlagOn(flag As Long) As Long
#     FlagOn = flag Or FLAG_SET_BIT ' Use to set option flag bits on, leaving others unchanged
# End Function
#
# Function FlagOff(flag As Long) As Long
#     FlagOff = flag Or FLAG_CLEAR_BIT ' Use to set option flag bits off, leaving others unchanged
# End Function
#
# Function getColor(colorName As String) As Long
#     Select Case colorName
#
#         Case "Black"
#             getColor = RGB(0, 0, 0)
#         Case "Gray"
#             getColor = RGB(128, 128, 128)
#         Case "White"
#             getColor = RGB(255, 255, 255)
#
#
#         Case "Blue"
#             getColor = RGB(0, 128, 192)
#         Case "Green"
#             getColor = RGB(20, 180, 20)
#         Case "Red"
#             getColor = RGB(255, 70, 50)
#
#
#         Case "Yellow"
#             getColor = RGB(230, 160, 20)
#         Case "Purple"
#             getColor = RGB(200, 50, 255)
#
#
#         Case "Pink"
#             getColor = RGB(255, 150, 200)
#         Case "LightBlue"
#             getColor = RGB(20, 200, 200)
#
#
#         Case "DarkBlue"
#             getColor = RGB(0, 0, 100)
#         Case "Dan"
#             getColor = RGB(228, 94, 50)
#         Case "Brown"
#             getColor = RGB(128, 0, 0)
#
#         Case Else
#             ' Default or error handling
#             getColor = RGB(0, 0, 0) ' Returning black as default or for an unrecognized color
#     End Select
# End Function
#
#
# Sub updatePlot(COLOR As Long)
#     ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_GRAPH).NameObject.SetObjectCurrent
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETPLOTATTR, SEA_COLOR, COLOR)
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETPLOTATTR, SEA_COLORREPEAT, &H00000002&)
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETPLOTATTR, SEA_THICKNESS, &H00000005&) ' .12 mm = .047 Inches
# End Sub
#
# Sub updateScatter(COLOR As Long)
#     ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_GRAPH).NameObject.SetObjectCurrent
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETPLOTATTR, SSA_EDGECOLOR, COLOR)
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETPLOTATTR, SSA_COLOR, COLOR)
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETPLOTATTR, SSA_COLORREPEAT, &H00000002&)
# 	ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETPLOTATTR, SSA_SIZE, &H00000020&) ' .8 mm = .032 inch
#     ' fixme scattersize=0.032 Innches
# End Sub
# Sub updateSolid(COLOR As Long)
# 	ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_GRAPH).NameObject.SetObjectCurrent
# 	ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETPLOTATTR, SDA_COLOR, COLOR)
# 	ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETPLOTATTR, SDA_COLORREPEAT, &H00000002&)
# End Sub
#
#
#
# Function findObjectType() As String
#     On Error GoTo ErrorHandler
#
#     Dim ObjectType As Variant
#     Dim object_type As Variant
# 	object_type = ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_GRAPH).Plots(0).GetAttribute(SLA_TYPE, ObjectType)
#
#     If object_type = False Then
#         findObjectType = "Error: Failed to get object type."
#         Exit Function
#     End If
#
#     ' Map the ObjectType to a string
#     Select Case object_type
#         Case SLA_TYPE_SCATTER
#             findObjectType = "Scatter/Line"
#         Case SLA_TYPE_BAR
#             findObjectType = "Bar"
#         Case SLA_TYPE_STACKED
#             findObjectType = "Stacked Bar"
#         Case SLA_TYPE_TUKEY
#             findObjectType = "Box"
#         Case SLA_TYPE_3DSCATTER
#             findObjectType = "3D Scatter/Line"
#         Case Else
#             findObjectType = "Unknown Object Type: " & object_type
#     End Select
#     Exit Function
#
# ErrorHandler:
#     findObjectType = "An error has occurred: " & Err.Description
# End Function
#
# Sub Main()
#     On Error GoTo ErrorHandler
#
# 	Dim FullPATH As String
#     Dim OrigPageName As String
#     Dim ObjectType As String
#     Dim COLOR As Long
#
#     ' Remember the original page
#     FullPATH = ActiveDocument.FullName
#     OrigPageName = ActiveDocument.CurrentPageItem.Name
#     ActiveDocument.NotebookItems(OrigPageName).IsCurrentBrowserEntry = True
#
#     ' Get the color value for blue
#     COLOR = getColor("Blue")
#
#     ' Find the type of the object
#     ObjectType = findObjectType()
#
#     ' Check the object type and call the corresponding update function
#     If ObjectType = "Scatter/Line" Or ObjectType = "3D Scatter/Line" Then
#         updatePlot COLOR
#         updateScatter COLOR
#     ElseIf ObjectType = "Bar" Or ObjectType = "Stacked Bar" Or ObjectType = "Box" Then
#         updateSolid COLOR
#     Else
#         ' Raise a custom error
#         Err.Raise vbObjectError + 513, "Main", "Unknown or unsupported object type: " & ObjectType
#     End If
#
#     ' Go back to the original page
# 	Notebooks(FullPATH).NotebookItems(OrigPageName).Open
#
#     Exit Sub
#
# ErrorHandler:
#     MsgBox "An error has occurred: " & Err.Description
# End Sub
# """
#     )

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/gists/_SigMacro_toBlue.py
# --------------------------------------------------------------------------------

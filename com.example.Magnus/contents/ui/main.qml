import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root
    
    property real vectorX: 0
    property real vectorY: 0
    property string vectorFile: ""
    property int readCount: 0
    
    preferredRepresentation:  compactRepresentation
    
    Component.onCompleted: {
        vectorFile = "/home/Add_Later/.local/share/vector_data/vector.json"
        readVectorFile()
    }
    
    Timer {
        id: fileReader
        interval: 1000
        running: true
        repeat:  true
        onTriggered: readVectorFile()
    }
    
    function readVectorFile() {
        readCount++
        
        var xhr = new XMLHttpRequest()
        var fileUrl = "file://" + vectorFile
        
        xhr.open("GET", fileUrl)
        
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 0 || xhr.status === 200) {
                    if (xhr.responseText !== "") {
                        try {
                            var data = JSON.parse(xhr.responseText)
                            if (data.vector) {
                                vectorX = data.vector.x
                                vectorY = data.vector.y
                            }
                        } catch (e) {}
                    }
                }
            }
        }
        
        xhr.send()
    }
    
    compactRepresentation: Item {
        Layout.preferredWidth: label.implicitWidth + Kirigami.Units.smallSpacing * 2
        Layout.preferredHeight: label.implicitHeight
        
        MouseArea {
            anchors.fill: parent
            onClicked: root.expanded = !root.expanded
            hoverEnabled: true
            
            PlasmaComponents.ToolTip {
                text: "2D Vector Monitor\nX: " + vectorX + "\nY:  " + vectorY + "\nReads: " + readCount
            }
        }
        
        PlasmaComponents.Label {
            id: label
            anchors.centerIn: parent
            text: "(" + vectorX + ", " + vectorY + ")"
        }
    }
    
    fullRepresentation: Item {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 20
        Layout.preferredHeight: Kirigami.Units.gridUnit * 15
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Kirigami.Units.largeSpacing
            spacing: Kirigami.Units.largeSpacing
            
            Kirigami.Heading {
                text: "2D Vector Monitor"
                level: 2
            }
            
            GridLayout {
                columns: 2
                columnSpacing: Kirigami.Units.largeSpacing
                rowSpacing: Kirigami.Units.smallSpacing
                
                PlasmaComponents.Label {
                    text: "X:"
                    font.bold: true
                }
                PlasmaComponents.Label {
                    text: vectorX
                }
                
                PlasmaComponents.Label {
                    text: "Y:"
                    font.bold: true
                }
                PlasmaComponents.Label {
                    text: vectorY
                }
                
                PlasmaComponents.Label {
                    text: "Reads:"
                    font.bold: true
                }
                PlasmaComponents.Label {
                    text: readCount
                }
                
                PlasmaComponents.Label {
                    text: "File:"
                    font.bold: true
                }
                PlasmaComponents.Label {
                    text: vectorFile
                    Layout.fillWidth: true
                    elide: Text.ElideMiddle
                }
            }
            
            PlasmaComponents.Button {
                text: "Manual Read"
                onClicked: readVectorFile()
            }
            
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "transparent"
                border.color: Kirigami.Theme.textColor
                border.width: 1
                radius: Kirigami.Units.smallSpacing
                
                Rectangle {
                    width:  Kirigami.Units.gridUnit
                    height: Kirigami.Units.gridUnit
                    radius: width / 2
                    color: Kirigami.Theme.highlightColor
                    x: (parent.width / 100) * vectorX - width / 2
                    y: (parent.height / 100) * vectorY - height / 2
                    
                    Behavior on x { NumberAnimation { duration: 200 } }
                    Behavior on y { NumberAnimation { duration: 200 } }
                }
            }
        }
    }
}
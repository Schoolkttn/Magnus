import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root
    
    property var vectors: []
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
                            // Support both old single vector format and new multiple vectors format
                            if (data.vectors) {
                                vectors = data.vectors
                            } else if (data.vector) {
                                // Backwards compatibility with single vector
                                vectors = [{
                                    x: data.vector.x,
                                    y: data.vector.y,
                                    name: "Vector",
                                    magnitude: 0
                                }]
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
                text: {
                    var tooltip = "2D Vector Monitor\n"
                    tooltip += "Vectors: " + vectors.length + "\n"
                    for (var i = 0; i < vectors.length; i++) {
                        tooltip += vectors[i].name + ": (" + vectors[i].x.toFixed(1) + ", " + vectors[i].y.toFixed(1) + ")\n"
                    }
                    tooltip += "Reads: " + readCount
                    return tooltip
                }
            }
        }
        
        PlasmaComponents.Label {
            id: label
            anchors.centerIn: parent
            text: "Vectors: " + vectors.length
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
                    text: "Vectors:"
                    font.bold: true
                }
                PlasmaComponents.Label {
                    text: vectors.length
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
                
                // Center point
                Rectangle {
                    width: Kirigami.Units.gridUnit * 0.5
                    height: Kirigami.Units.gridUnit * 0.5
                    radius: width / 2
                    color: Kirigami.Theme.textColor
                    x: parent.width / 2 - width / 2
                    y: parent.height / 2 - height / 2
                }
                
                // Repeater to create multiple arrows for each vector
                Repeater {
                    model: vectors.length
                    
                    delegate: Item {
                        anchors.fill: parent
                        
                        property var vectorData: vectors[index]
                        property real centerX: parent.width / 2
                        property real centerY: parent.height / 2
                        property real scale: Math.min(parent.width, parent.height) / 200
                        property real vectorAngle: -Math.atan2(vectorData.y, -vectorData.x)
                        property color vectorColor: vectorData.name === "Known" ? Kirigami.Theme.positiveTextColor : Kirigami.Theme.neutralTextColor
                        
                        // Arrow line
                        Rectangle {
                            id: arrowLine
                            width: Math.sqrt(Math.pow(vectorData.x * scale, 2) + Math.pow(vectorData.y * scale, 2))
                            height: 2
                            color: parent.vectorColor
                            
                            x: centerX
                            y: centerY
                            
                            transformOrigin: Item.Left
                            rotation: parent.vectorAngle * 180 / Math.PI
                            
                            Behavior on rotation { NumberAnimation { duration: 200 } }
                            Behavior on width { NumberAnimation { duration: 200 } }
                        }
                        
                        // Arrow head (triangle)
                        Canvas {
                            id: arrowHead
                            width: 20
                            height: 20
                            
                            property real endX: centerX - vectorData.x * scale
                            property real endY: centerY - vectorData.y * scale
                            
                            x: endX - width / 2
                            y: endY - height / 2
                            
                            Behavior on x { NumberAnimation { duration: 200 } }
                            Behavior on y { NumberAnimation { duration: 200 } }
                            
                            onPaint: {
                                var ctx = getContext("2d")
                                ctx.reset()
                                
                                ctx.fillStyle = parent.vectorColor
                                
                                ctx.save()
                                ctx.translate(width / 2, height / 2)
                                ctx.rotate(parent.vectorAngle)
                                
                                ctx.beginPath()
                                ctx.moveTo(8, 0)
                                ctx.lineTo(-4, -6)
                                ctx.lineTo(-4, 6)
                                ctx.closePath()
                                ctx.fill()
                                
                                ctx.restore()
                            }
                            
                            Connections {
                                target: root
                                function onVectorsChanged() {
                                    arrowHead.requestPaint()
                                }
                            }
                        }
                        
                        // Label
                        PlasmaComponents.Label {
                            x: centerX - vectorData.x * scale - width / 2
                            y: centerY - vectorData.y * scale - height - 5
                            text: vectorData.name
                            color: parent.vectorColor
                            font.pixelSize: Kirigami.Units.gridUnit * 0.7
                            
                            Behavior on x { NumberAnimation { duration: 200 } }
                            Behavior on y { NumberAnimation { duration: 200 } }
                        }
                    }
                }
            }
        }
    }
}
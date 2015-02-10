import QtQuick 1.0

Item {
  width : 400
  height : 400

  Rectangle {
    x : 100
    y : 100
    id:vector1
    width : 100
    height : 100
    color : "lightsteelblue"
    property variant axis3d: Qt.vector3d(0,0,0.3)
    transform : Rotation {
      angle : 360
      axis: vector1.axis3d
//      Vector3dAnimation {
//        from : Qt.vector3d(0.3, 0.3, 0.3)
//        to : Qt.vector3d(0, 0.6, 0.6)
//        duration : 1000
//      }
//       axis : Qt.vector3d(1, 0, 0)
//      SequentialAnimation on axis {
//        Vector3dAnimation {
//          from : Qt.vector3d(0.3, 0.3, 0.3)
//          to : Qt.vector3d(0, 0.6, 0.6)
//          duration : 1000
//        }
//        Vector3dAnimation {
//          from : Qt.vector3d(0, 0.6, 0.6)
//          to : Qt.vector3d(0.3, 0.3, 0.3)
//          duration : 1000
//        }
//        loops : Animation.Infinite
//      }
    }
  }
}

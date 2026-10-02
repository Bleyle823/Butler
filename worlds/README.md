# Hotel world

Open `hotel.wbt` in Webots R2025a (installed binary, not a source build of webots-master).

The Windows installer does not ship furniture, kitchen, or TIAGo proto files. GitHub downloads also fail when Webots opens too many connections at once.

This world loads catalog protos from `assets/webots/projects/` inside this repo. You do not need `webots-master` on the machine, and you do not need GitHub at world-load time.

The local robot files are `../protos/ButlerServe.proto`, `ButlerTray.proto`, and `HotelDoor.proto`.

You should see:

- Lobby with desk and seating tucked to the west wall, open dock lane to the corridor door, and three ButlerServe robots
- Restaurant with two set tables, a fridge, and a pass worktop
- Pickup counter with plates, glasses, a carafe, and a pizza box
- Rooms 1204, 1205, 1206 with a bed, desk, and empty place setting
- Colored marker spheres named `counter`, `restaurant-table-1`, `room-1204`, `room-1205`, `room-1206`

`servebot-1` is the live robot. It is a TIAGo++ with Hey5 hands, Astra RGB-D, Hokuyo URG-04LX-UG01 (180 rays), GPS, compass, IMU, gyro, accelerometer, bumper, rear sonars, and extra front sonars. Idle arms fold in front of the torso. The chest tray uses the same glossy body paint and brushed aluminium as the robot, with a 45 mm rim and recessed wells so carried items cannot slide off.

Reload the world and it starts the pizza job on its own: drive to the counter, reach and grasp, seat the pizza/plate/glass on the tray, deliver to room 1204, fold, return to the dock. Select `servebot-1` and press `J` to rerun, `T` for keyboard teleop, arrows/WASD to drive. Select `butler_supervisor` and press 1-5 to toggle doors.

The other two ServeBots stay docked (body and tray, no arm or sensor devices).

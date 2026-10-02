# Hotel world

Open `hotel.wbt` in Webots R2025a (installed binary, not a source build of webots-master).

The Windows installer does not ship furniture, kitchen, or TIAGo proto files. GitHub downloads also fail when Webots opens too many connections at once.

This world loads catalog protos from `assets/webots/projects/` inside this repo. You do not need `webots-master` on the machine, and you do not need GitHub at world-load time.

The local robot files are `../protos/ButlerServe.proto` and `ButlerTray.proto`.

You should see:

- Lobby with a desk, sofa, and three ButlerServe robots
- Restaurant with two set tables (plate, glass, wineglass, cutlery, bottle), a fridge, and a pass worktop
- Pickup counter with plates, glasses, a carafe, and a pizza box
- Rooms 1204, 1205, 1206 with a bed, desk, and empty place setting
- Colored marker spheres named `counter`, `restaurant-table-1`, `room-1204`, `room-1205`, `room-1206`
- Empty circular pads on each robot’s chest tray (`plateSlot`, `glassSlot`, `wineglassSlot`, `boxSlot`)

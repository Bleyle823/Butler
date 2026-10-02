# Local Webots catalog

Cyberbotics proto files used by `worlds/hotel.wbt`. Licensed for use only with Webots.

The Windows installer does not ship furniture, kitchen, or TIAGo meshes. Downloading them from GitHub at world-load time fails when Webots opens too many connections.

Refresh from a local `webots-master` checkout:

```
powershell -ExecutionPolicy Bypass -File scripts/vendor-webots-assets.ps1
```

# Rover — revised Blender model

Editable reconstruction from the owner's original IMG_8361–IMG_8364 photographs, revised to improve the wheels and Logitech C270 webcam. Dimensions remain estimated, as requested.

## What changed

- Replaced the simplified wheels with tire and hub geometry extracted from Waveshare's published WAVE ROVER STL. The revised wheels retain the rounded tire section, tread channels, shoulder cuts and recessed curved spokes visible in the photographs.
- Rebuilt the webcam with a thin curved shell, separate faceplate, recessed optical well, indicator window, nine microphone holes and folded clip. Lowered it onto its mount to better match the photographs.
- Narrowed the concealed lower enclosure to clear the wider tires.

## Files

- `Rover.blend` — editable master scene with separate components, materials, four studio cameras; original private reference photographs removed.
- `Rover.glb` — portable rover model; excludes the studio and reference photographs.
- `Rover-Hero.png`, `Rover-Rear.png`, `Rover-Side.png`, `Rover-Top.png` — full-resolution Blender renders.
- `Rover-Camera-Detail.png`, `Rover-Wheel-Detail.png` — close-up renders of the revised components.
- `build_rover.py` and `assets/wave-rover-wheel.json` — construction script and required wheel geometry.
- `model-info.json` — scene version, object count and estimated overall dimensions, including cables.
- `validation.json` — saved-scene and GLB import checks.

## Editing

Open `Rover.blend`. Numbered collections separate the chassis, wheels, Pi board, webcam, cables, markings, studio and references. Move the whole model with **ROVER | move the complete model**. Rotate each wheel's named pivot around its local X axis. Adjust the webcam head with **C270 | camera tilt pivot**; its folded clip remains separate.

Cable curves and label text remain editable in Blender. The GLB converts these to meshes for portability.

## Scale and limitations

The scene uses metres and displays millimetres. The Raspberry Pi board is nominally 85 × 56 mm. Other dimensions and component positions are estimated from photographs, including the overall chassis reconstruction. The manufacturer's nominal 80 × 42.5 mm wheel geometry is uniformly enlarged to an approximately 99.6 mm diameter in this reconstruction to preserve the estimated proportions of the existing model. Its detailed shape comes from the manufacturer; its scale in this model is an estimate.

The webcam uses nominal C270 dimensions as a guide, with its clip pose and mounting inferred from the photos. Small electronics and unseen underside details are simplified. This is a visualization model, not measured engineering CAD or a fabrication file.

## Sources and attribution

- Owner's original photographs: IMG_8361, IMG_8362, IMG_8363 and IMG_8364.
- Waveshare WAVE ROVER documentation: https://www.waveshare.com/wiki/WAVE_ROVER
- Manufacturer model archive, source of the tire and hub geometry: https://files.waveshare.com/upload/e/ec/WAVE_ROVER_MODEL_STL.rar
- Logitech C270 product reference: https://www.logitech.com/en-us/shop/p/c270-hd-webcam
- Logitech C270 setup guide: https://secure.logitech.com/assets/46735/4/hd-webcam-c270.pdf

The manufacturer mesh and product marks remain attributable to their respective owners; this package does not grant an additional license to those assets.

## Rebuilding

Created with Blender 4.5 LTS. Keep the `assets` folder beside the script and run:

```sh
blender --background --python build_rover.py
```

This rebuilds the model, GLB and four overview renders in the script's folder. Add `-- --draft` for smaller hero and side previews, or `-- --no-render` for model files only. Close-up renders are supplied as additional previews. Optional private reference JPEGs can be supplied through `ROVER_REFERENCE_DIR`; the public `.blend` contains no reference photographs.

## Public repository copy

Original room photographs and their reference objects were removed from the Blender files. Modeled geometry and product renders are unchanged.
